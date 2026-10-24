"""Budgeted interpreter for the canonical AssayFlux core (not an OS sandbox)."""
from __future__ import annotations

import math
import operator
import re
import sys
from collections.abc import Callable
from contextlib import suppress
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from assayflux.diagnostics.model import (
    DatabaseErrorAF,
    Diagnostic,
    ImportErrorAF,
    PythonBridgeError,
    RuntimeErrorAF,
    SecurityError,
    Severity,
    SourceLocation,
)
from assayflux.diagnostics.reporter import write_report
from assayflux.language import ast_nodes as A
from assayflux.language.ast_validator import validate_ast
from assayflux.language.parser import parse
from assayflux.language.semantic import check
from assayflux.runtime.python_bridge import (
    PythonBridge,
    is_python_module_hard_denied,
)
from assayflux.security.checkpoints import SecurityPolicy, read_source


@dataclass
class ExecutionResult:
    output: list[str] = field(default_factory=list)
    variables: dict[str, Any] = field(default_factory=dict)
    steps: int = 0

@dataclass
class _SharedRuntime:
    steps: int = 0
    loop_count: int = 0
    output_chars: int = 0
    call_depth: int = 0
    module_cache: dict[str, Any] = field(default_factory=dict)
    modules_loading: set[str] = field(default_factory=set)
    import_depth: int = 0

@dataclass
class _UserFunction:
    definition: A.FunctionDef
    closure: dict[str, Any]
    owner: Any

@dataclass
class _SafeModule:
    name: str

@dataclass
class _AssayFluxModule:
    """Namespace exported by a safely loaded AssayFlux project module."""
    name: str
    values: dict[str, Any]
    functions: dict[str, Any]
    constants: frozenset[str] = frozenset()

@dataclass(frozen=True, slots=True)
class _ErrorValue:
    original: Any
    code: str
    message: str
    category: str
    line: int
    column: int
    def __str__(self): return self.message

class _ReturnSignal(Exception):
    def __init__(self, value): self.value=value
class _StopSignal(Exception): pass
class _SkipSignal(Exception): pass

def _safe_range(*args):
    value=range(*args)
    if len(value)>100_000: raise ValueError("range exceeds item limit")
    return value
def _safe_enumerate(value, start=0):
    if not isinstance(value,(list,tuple,str,range)): raise TypeError("enumerate requires a bounded sequence")
    if len(value)>100_000: raise ValueError("sequence exceeds item limit")
    return list(enumerate(value,start))
def _safe_zip(*values):
    if not all(isinstance(v,(list,tuple,str,range)) for v in values): raise TypeError("zip requires bounded sequences")
    if any(len(v)>100_000 for v in values): raise ValueError("sequence exceeds item limit")
    return list(zip(*values, strict=False))
def _safe_reversed(value):
    if not isinstance(value,(list,tuple,str,range)): raise TypeError("reversed requires a bounded sequence")
    if len(value)>100_000: raise ValueError("sequence exceeds item limit")
    return list(reversed(value))
def _safe_pow(a,b,mod=None):
    if (
        isinstance(b, int)
        and not isinstance(b, bool)
        and b >= 0
        and isinstance(a, int)
        and not isinstance(a, bool)
        and (b > 4096 or (abs(a) > 1 and a.bit_length() * b > 4096))
    ):
        raise ValueError("power result exceeds numeric budget")
    if mod is None: return pow(a,b)
    return pow(a,b,mod)

def _estimate_value_bytes(value, limit, seen=None, depth=0):
    """Conservative bounded estimate for interpreter-owned primitive containers."""
    if seen is None:
        seen = set()
    if depth > 256:
        return limit + 1
    identity = id(value)
    if identity in seen:
        return 0
    seen.add(identity)
    try:
        size = sys.getsizeof(value, 64)
    except (TypeError, ValueError):
        return limit + 1
    if size > limit:
        return limit + 1
    total = size
    if isinstance(value, dict):
        for key, child in value.items():
            remaining = limit - total
            if remaining <= 0:
                return limit + 1
            total += _estimate_value_bytes(key, remaining, seen, depth + 1)
            remaining = limit - total
            if remaining <= 0:
                return limit + 1
            total += _estimate_value_bytes(child, remaining, seen, depth + 1)
            if total > limit:
                return limit + 1
    elif isinstance(value, (list, tuple, set, frozenset)):
        for child in value:
            remaining = limit - total
            if remaining <= 0:
                return limit + 1
            total += _estimate_value_bytes(child, remaining, seen, depth + 1)
            if total > limit:
                return limit + 1
    return total
_BUILTINS: dict[str, Callable] = {
    "range": _safe_range, "len": len, "abs": abs, "min": min, "max": max,
    "sum": sum, "round": round, "str": str, "int": int, "float": float,
    "bool": bool, "list": list, "tuple": tuple, "dict": dict, "set": set,
    "enumerate": _safe_enumerate, "zip": _safe_zip, "sorted": sorted, "reversed": _safe_reversed,
    "all": all, "any": any, "divmod": divmod, "pow": _safe_pow,
}
_BINOPS = {"+":operator.add,"-":operator.sub,"*":operator.mul,"/":operator.truediv,"//":operator.floordiv,"%":operator.mod,"**":operator.pow,"@":None,"|":operator.or_,"&":operator.and_,"^":operator.xor,"<<":operator.lshift,">>":operator.rshift,"==":operator.eq,"!=":operator.ne,"<":operator.lt,">":operator.gt,"<=":operator.le,">=":operator.ge}

class Interpreter:
    def __init__(self, policy: SecurityPolicy | None = None, *, output_fn: Callable[[str], None] | None = None, workspace: Path | None = None, _shared: _SharedRuntime | None = None):
        self.policy=policy or SecurityPolicy(); self.output_fn=output_fn
        self.workspace=Path(workspace).resolve() if workspace is not None else None
        self._shared=_shared or _SharedRuntime()
        self.env:dict[str,Any]={}; self.constants:set[str]=set(); self.scope_declared:list[set[str]]=[set()]; self.scope_shadowed:list[dict[str,tuple[Any,bool]]]=[{}]; self.output:list[str]=[]
        self.steps=0; self.loop_count=0; self.output_chars=0; self.call_depth=0
        self.python_bridge=PythonBridge(self.policy)
        self.functions:dict[str,_UserFunction]={}; self._predeclared:set[str]=set()
    @property
    def steps(self): return self._shared.steps
    @steps.setter
    def steps(self,value): self._shared.steps=value
    @property
    def loop_count(self): return self._shared.loop_count
    @loop_count.setter
    def loop_count(self,value): self._shared.loop_count=value
    @property
    def output_chars(self): return self._shared.output_chars
    @output_chars.setter
    def output_chars(self,value): self._shared.output_chars=value
    @property
    def call_depth(self): return self._shared.call_depth
    @call_depth.setter
    def call_depth(self,value): self._shared.call_depth=value
    def _step(self,loc):
        self.steps+=1
        if self.steps>self.policy.max_steps: raise RuntimeErrorAF("Execution step budget exceeded",location=loc,suggestion="Check for an unintended infinite loop or reduce computation.")
    def _guard_value(self,value,loc):
        if isinstance(value,bool) or value is None or isinstance(value,str):
            if isinstance(value,str) and len(value)>self.policy.max_output_chars: raise RuntimeErrorAF("String value exceeds configured size limit",location=loc)
            if isinstance(value,str) and sys.getsizeof(value)>self.policy.max_value_bytes: raise RuntimeErrorAF("Value memory budget exceeded",location=loc)
            return value
        if isinstance(value,int):
            if value.bit_length()>self.policy.max_numeric_bits: raise RuntimeErrorAF("Integer exceeds configured numeric limit",location=loc)
            return value
        if isinstance(value,float):
            if not math.isfinite(value): raise RuntimeErrorAF("Non-finite numeric result is not permitted",location=loc)
            return value
        if isinstance(value,complex):
            if not math.isfinite(value.real) or not math.isfinite(value.imag): raise RuntimeErrorAF("Non-finite complex result is not permitted",location=loc)
            return value
        if isinstance(value,(list,tuple,set,dict,range)):
            if len(value)>100_000: raise RuntimeErrorAF("Collection exceeds configured item limit",location=loc)
            if not isinstance(value, range) and _estimate_value_bytes(value,self.policy.max_value_bytes)>self.policy.max_value_bytes:
                raise RuntimeErrorAF("Value memory budget exceeded",location=loc)
            return value
        if isinstance(value,(_UserFunction,_SafeModule,_AssayFluxModule,_ErrorValue)): return value
        raise RuntimeErrorAF(f"Unsupported runtime value type: {type(value).__name__}",location=loc)
    def _eval(self,node):
        self._step(node.loc)
        try:
            if isinstance(node,A.Lambda):
                synthetic=A.FunctionDef(node.loc,"<lambda>",node.parameters,(A.Return(node.loc,node.body),),None)
                return _UserFunction(synthetic,self.env,self)
            if isinstance(node,A.Literal):
                if isinstance(node.value,tuple) and len(node.value)==2 and node.value[0]=="__fstring__":
                    return self._format_fstring(node.value[1],node.loc)
                return self._guard_value(node.value,node.loc)
            if isinstance(node,A.Variable):
                if node.name in self.env: return self.env[node.name]
                if node.name in self.functions: return self.functions[node.name]
                if node.name in _BUILTINS: return _BUILTINS[node.name]
                raise RuntimeErrorAF(f"Undefined name '{node.name}'",location=node.loc)
            if isinstance(node,A.ListLiteral):
                if len(node.values)>100_000: raise RuntimeErrorAF("Collection exceeds configured item limit",location=node.loc)
                result: Any = []; estimated= sys.getsizeof(result); seen: set[int] = set()
                for child in node.values:
                    value=self._eval(child)
                    estimated += sys.getsizeof(None) + _estimate_value_bytes(value,self.policy.max_value_bytes-estimated,seen)
                    if estimated>self.policy.max_value_bytes: raise RuntimeErrorAF("Value memory budget exceeded",location=node.loc)
                    result.append(value)
                return self._guard_value(result,node.loc)
            if isinstance(node,A.Comprehension):
                iterable=self._eval(node.iterable)
                if not isinstance(iterable,(list,tuple,set,dict,str,range)): raise RuntimeErrorAF("Comprehension requires a bounded built-in iterable",location=node.loc)
                if len(iterable)>100_000: raise RuntimeErrorAF("Comprehension iterable exceeds item limit",location=node.loc)
                old_present=node.name in self.env; old=self.env.get(node.name); was_constant=node.name in self.constants
                self.constants.discard(node.name); result = [] if node.kind=="list" else set() if node.kind=="set" else {}
                estimated=sys.getsizeof(result); seen=set()
                try:
                    for item in iterable:
                        self._step(node.loc); self.env[node.name]=item
                        if node.condition is not None and not _truth(self._eval(node.condition),node.condition.loc): continue
                        if node.kind=="dict":
                            key=self._eval(node.key); value=self._eval(node.element)
                            delta=2*sys.getsizeof(None) + _estimate_value_bytes(key,max(0,self.policy.max_value_bytes-estimated),seen)
                            delta += _estimate_value_bytes(value,max(0,self.policy.max_value_bytes-estimated-delta),seen)
                            if estimated+delta>self.policy.max_value_bytes: raise RuntimeErrorAF("Value memory budget exceeded",location=node.loc)
                            if key not in result and len(result)>=100_000: raise RuntimeErrorAF("Comprehension result exceeds item limit",location=node.loc)
                            result[key]=value
                            estimated+=delta
                        elif node.kind=="set":
                            value=self._eval(node.element)
                            delta=sys.getsizeof(None) + _estimate_value_bytes(value,max(0,self.policy.max_value_bytes-estimated),seen)
                            if estimated+delta>self.policy.max_value_bytes: raise RuntimeErrorAF("Value memory budget exceeded",location=node.loc)
                            if value not in result and len(result)>=100_000: raise RuntimeErrorAF("Comprehension result exceeds item limit",location=node.loc)
                            result.add(value)
                            estimated+=delta
                        else:
                            value=self._eval(node.element)
                            delta=sys.getsizeof(None) + _estimate_value_bytes(value,max(0,self.policy.max_value_bytes-estimated),seen)
                            if estimated+delta>self.policy.max_value_bytes: raise RuntimeErrorAF("Value memory budget exceeded",location=node.loc)
                            if len(result)>=100_000: raise RuntimeErrorAF("Comprehension result exceeds item limit",location=node.loc)
                            result.append(value)
                            estimated+=delta
                finally:
                    if old_present:self.env[node.name]=old
                    else:self.env.pop(node.name,None)
                    if was_constant:self.constants.add(node.name)
                return self._guard_value(result,node.loc)
            if isinstance(node,A.TupleLiteral):
                if len(node.values)>100_000: raise RuntimeErrorAF("Collection exceeds configured item limit",location=node.loc)
                result=[]; estimated=sys.getsizeof(result); seen=set()
                for child in node.values:
                    value=self._eval(child)
                    estimated += sys.getsizeof(None) + _estimate_value_bytes(value,self.policy.max_value_bytes-estimated,seen)
                    if estimated>self.policy.max_value_bytes: raise RuntimeErrorAF("Value memory budget exceeded",location=node.loc)
                    result.append(value)
                return self._guard_value(tuple(result),node.loc)
            if isinstance(node,A.SetLiteral):
                if len(node.values)>100_000: raise RuntimeErrorAF("Collection exceeds configured item limit",location=node.loc)
                result=set(); estimated=sys.getsizeof(result); seen=set()
                for child in node.values:
                    value=self._eval(child)
                    estimated += sys.getsizeof(None) + _estimate_value_bytes(value,self.policy.max_value_bytes-estimated,seen)
                    if estimated>self.policy.max_value_bytes: raise RuntimeErrorAF("Value memory budget exceeded",location=node.loc)
                    result.add(value)
                return self._guard_value(result,node.loc)
            if isinstance(node,A.DictLiteral):
                if len(node.values)>100_000: raise RuntimeErrorAF("Collection exceeds configured item limit",location=node.loc)
                result={}; estimated=sys.getsizeof(result); seen=set()
                for key_node,value_node in node.values:
                    key=self._eval(key_node); value=self._eval(value_node)
                    estimated += 2*sys.getsizeof(None) + _estimate_value_bytes(key,self.policy.max_value_bytes-estimated,seen)
                    estimated += _estimate_value_bytes(value,self.policy.max_value_bytes-estimated,seen)
                    if estimated>self.policy.max_value_bytes: raise RuntimeErrorAF("Value memory budget exceeded",location=node.loc)
                    result[key]=value
                return self._guard_value(result,node.loc)
            if isinstance(node,A.Unary):
                value=self._eval(node.value)
                if node.op=="not": return not _truth(value,node.loc)
                if node.op=="-": return self._guard_value(-value,node.loc)
                if node.op=="+": return self._guard_value(+value,node.loc)
                if node.op=="~": return self._guard_value(~value,node.loc)
            if isinstance(node,A.Binary): return self._binary(node)
            if isinstance(node,A.Compare):
                left=self._eval(node.operands[0])
                for op_name, right_node in zip(node.operators,node.operands[1:], strict=False):
                    right=self._eval(right_node)
                    if op_name=="in": ok=left in right
                    elif op_name=="not in": ok=left not in right
                    elif op_name=="is": ok=left is right
                    elif op_name=="is not": ok=left is not right
                    else:
                        op=_BINOPS.get(op_name)
                        if op is None: raise RuntimeErrorAF(f"Comparison operator '{op_name}' is not supported",location=node.loc)
                        ok=op(left,right)
                    if not ok: return False
                    left=right
                return True
            if isinstance(node,A.Conditional): return self._eval(node.value) if _truth(self._eval(node.condition),node.loc) else self._eval(node.otherwise)
            if isinstance(node,A.Attribute):
                target=self._eval(node.value)
                if isinstance(target,_SafeModule):
                    if node.name.startswith("_"): raise SecurityError("Private Python module attributes are not accessible",location=node.loc)
                    submodule=f"{target.name}.{node.name}"
                    if submodule in self.policy.allowed_python_modules:return _SafeModule(submodule)
                    return _SafeModuleMember(target.name,node.name)
                if isinstance(target,_AssayFluxModule):
                    if node.name.startswith("_"): raise SecurityError("Private module names are not accessible",location=node.loc)
                    if node.name in target.values:return target.values[node.name]
                    if node.name in target.functions:return target.functions[node.name]
                    raise RuntimeErrorAF(f"Module '{target.name}' has no exported name '{node.name}'",location=node.loc)
                if isinstance(target,_ErrorValue):
                    if node.name in {"message","code","category"}: return getattr(target,node.name)
                    if node.name in {"line","column"}: return getattr(target,node.name)
                    raise SecurityError(f"Error attribute '{node.name}' is not exposed",location=node.loc)
                if isinstance(target,dict) and node.name in {"keys","values","items","get"}: return _SafeMethod(target,node.name)
                if isinstance(target,(list,tuple,str)) and node.name in {"count","index","startswith","endswith","upper","lower","strip","split","join","append","extend","pop"}: return _SafeMethod(target,node.name)
                raise SecurityError(f"Attribute access '{node.name}' is not allowed for this value",location=node.loc)
            if isinstance(node,A.Index):
                target=self._eval(node.value); index=self._eval(node.index)
                if not isinstance(index,(int,str,slice)): raise RuntimeErrorAF("Invalid collection index type",location=node.loc)
                try: return self._guard_value(target[index],node.loc)
                except (IndexError,KeyError,TypeError) as exc: raise RuntimeErrorAF("Collection index is invalid",location=node.loc,details=type(exc).__name__) from exc
            if isinstance(node,A.Call): return self._call(node)
        except (RuntimeErrorAF,SecurityError,PythonBridgeError): raise
        except ZeroDivisionError as exc: raise RuntimeErrorAF("Division by zero",location=node.loc) from exc
        except (TypeError,ValueError,OverflowError,IndexError,KeyError,AttributeError) as exc: raise RuntimeErrorAF("Invalid operation or function arguments",location=node.loc,details=type(exc).__name__) from exc
        raise RuntimeErrorAF(f"Unsupported expression node: {type(node).__name__}",location=getattr(node,"loc",SourceLocation()))
    def _binary(self,node):
        left=self._eval(node.left)
        if node.op=="and": return self._eval(node.right) if _truth(left,node.loc) else left
        if node.op=="or": return left if _truth(left,node.loc) else self._eval(node.right)
        right=self._eval(node.right)
        if node.op=="in": return left in right
        if node.op=="not in": return left not in right
        if node.op=="is": return left is right
        if node.op=="is not": return left is not right
        return self._apply_binary(node.op,left,right,node.loc)
    def _apply_binary(self,op_name,left,right,loc):
        if op_name=="@": return self._matrix_multiply(left,right,loc)
        op=_BINOPS.get(op_name)
        if op is None: raise RuntimeErrorAF(f"Operator '{op_name}' is not supported",location=loc)
        if (
            op_name == "**"
            and isinstance(left, int)
            and not isinstance(left, bool)
            and isinstance(right, int)
            and not isinstance(right, bool)
            and right >= 0
            and (
                right > self.policy.max_numeric_bits
                or (abs(left) > 1 and left.bit_length() * right > self.policy.max_numeric_bits)
            )
        ):
            raise RuntimeErrorAF("Power operation would exceed numeric budget", location=loc)
        if op_name == "<<" and isinstance(right, int) and (
            right < 0 or right > self.policy.max_numeric_bits
        ):
            raise RuntimeErrorAF("Shift count exceeds numeric budget", location=loc)
        if op_name == "+" and isinstance(left, str) and isinstance(right, str) and len(left) + len(right) > self.policy.max_output_chars:
            raise RuntimeErrorAF("String concatenation would exceed configured size limit", location=loc)
        if op_name=="+" and isinstance(left,(list,tuple)) and isinstance(right,type(left)):
            if len(left)+len(right)>100_000:
                raise RuntimeErrorAF("Collection concatenation would exceed item limit",location=loc)
            if _estimate_value_bytes((left,right),self.policy.max_value_bytes)>self.policy.max_value_bytes:
                raise RuntimeErrorAF("Collection concatenation would exceed value memory budget",location=loc)
        if op_name=="*" and isinstance(left,(str,list,tuple)) and isinstance(right,int):
            limit=self.policy.max_output_chars if isinstance(left,str) else 100_000
            result_count=len(left)*max(0,right)
            if result_count>limit: raise RuntimeErrorAF("Repetition would exceed value-size budget",location=loc)
            if isinstance(left,(list,tuple)) and result_count:
                source_size=_estimate_value_bytes(left,self.policy.max_value_bytes)
                projected=source_size+result_count*8
                if projected>self.policy.max_value_bytes: raise RuntimeErrorAF("Repetition would exceed value memory budget",location=loc)
        if op_name=="*" and isinstance(right,(str,list,tuple)) and isinstance(left,int):
            limit=self.policy.max_output_chars if isinstance(right,str) else 100_000
            result_count=len(right)*max(0,left)
            if result_count>limit: raise RuntimeErrorAF("Repetition would exceed value-size budget",location=loc)
            if isinstance(right,(list,tuple)) and result_count:
                source_size=_estimate_value_bytes(right,self.policy.max_value_bytes)
                projected=source_size+result_count*8
                if projected>self.policy.max_value_bytes: raise RuntimeErrorAF("Repetition would exceed value memory budget",location=loc)
        if op_name=="|" and isinstance(left,set) and isinstance(right,set):
            result_size=len(left)
            for item in right:
                if item not in left: result_size+=1
                if result_size>100_000:
                    raise RuntimeErrorAF("Set union would exceed collection item limit",location=loc)
        if op_name=="|" and isinstance(left,dict) and isinstance(right,dict):
            result_size=len(left)
            for key in right:
                if key not in left: result_size+=1
                if result_size>100_000:
                    raise RuntimeErrorAF("Map union would exceed collection item limit",location=loc)
        if op_name in {"+","-","*","//","%","**","<<",">>"} and isinstance(left,int) and isinstance(right,int) and not isinstance(left,bool) and not isinstance(right,bool):
            if op_name=="*" and left and right and abs(left).bit_length()+abs(right).bit_length()>self.policy.max_numeric_bits: raise RuntimeErrorAF("Multiplication would exceed numeric budget",location=loc)
            if op_name in {"+","-"} and max(abs(left).bit_length(),abs(right).bit_length())+1>self.policy.max_numeric_bits: raise RuntimeErrorAF("Addition would exceed numeric budget",location=loc)
        result=op(left,right)
        if isinstance(result,(str,list,tuple)) and len(result)>max(self.policy.max_output_chars,100_000): raise RuntimeErrorAF("Operation result exceeds configured size limit",location=loc)
        return self._guard_value(result,loc)
    def _matrix_multiply(self,left,right,loc):
        def vector(value):
            return isinstance(value,(list,tuple)) and all(isinstance(x,(int,float,complex)) and not isinstance(x,bool) for x in value)
        def matrix(value):
            return isinstance(value,(list,tuple)) and all(isinstance(row,(list,tuple)) for row in value) and all(vector(row) for row in value)
        if not (vector(left) or matrix(left)) or not (vector(right) or matrix(right)):
            raise RuntimeErrorAF("Matrix multiplication requires numeric vectors or rectangular matrices",location=loc)
        # Inspect dimensions and budgets before making any input copies or output rows.
        left_is_matrix=bool(left) and isinstance(left[0],(list,tuple))
        right_is_matrix=bool(right) and isinstance(right[0],(list,tuple))
        rows=len(left) if left_is_matrix else 1
        inner=len(left[0]) if left_is_matrix and rows else (len(left) if not left_is_matrix else 0)
        right_inner = len(right)
        cols=len(right[0]) if right_is_matrix and right_inner else (1 if not right_is_matrix else 0)
        if left_is_matrix and left:
            width=len(left[0])
            if any(len(row)!=width for row in left):
                raise RuntimeErrorAF("Left matrix is not rectangular",location=loc)
        if right_is_matrix and right:
            width=len(right[0])
            if any(len(row)!=width for row in right):
                raise RuntimeErrorAF("Right matrix is not rectangular",location=loc)
        if inner!=right_inner:
            raise RuntimeErrorAF("Matrix dimensions do not align for multiplication",location=loc,details=f"left inner dimension {inner}; right inner dimension {right_inner}")
        operations=rows*max(1,cols)*max(1,inner)
        if operations>100_000:
            raise RuntimeErrorAF("Matrix multiplication exceeds operation budget",location=loc)
        output_cells=rows*cols
        estimated_output=64+output_cells*32
        if estimated_output>self.policy.max_value_bytes:
            raise RuntimeErrorAF("Matrix multiplication result would exceed value memory budget",location=loc)
        result=[]
        for i in range(rows):
            row=[]
            for j in range(cols):
                total=0
                for k in range(inner):
                    self._step(loc)
                    left_value=left[i][k] if left_is_matrix else left[k]
                    right_value=right[k][j] if right_is_matrix else right[k]
                    product=self._apply_binary("*",left_value,right_value,loc)
                    total=self._apply_binary("+",total,product,loc)
                row.append(total)
            result.append(row)
        if not left_is_matrix and not right_is_matrix:return self._guard_value(result[0][0] if result and result[0] else 0,loc)
        if not left_is_matrix:return self._guard_value(result[0] if result else [],loc)
        if not right_is_matrix:return self._guard_value([row[0] for row in result],loc)
        return self._guard_value(result,loc)
    def _call(self,node):
        target=self._eval(node.function); args: list[Any]=[]; kwargs: dict[str, Any]={}
        for arg in node.arguments:
            value=self._eval(arg.value)
            if arg.kind=="positional":
                if len(args)>=1_000: raise RuntimeErrorAF("Call positional argument count exceeds limit",location=arg.loc)
                args.append(value)
            elif arg.kind=="keyword":
                if arg.name in kwargs: raise RuntimeErrorAF(f"Duplicate keyword argument '{arg.name}'",location=arg.loc)
                if len(kwargs)>=100_000: raise RuntimeErrorAF("Call keyword argument count exceeds limit",location=arg.loc)
                kwargs[arg.name]=value
            elif arg.kind=="star":
                if not isinstance(value,(list,tuple,range)): raise RuntimeErrorAF("* argument must be a bounded sequence",location=arg.loc)
                if len(args)+len(value)>100_000: raise RuntimeErrorAF("Expanded argument list exceeds limit",location=arg.loc)
                args.extend(value)
            elif arg.kind=="kwstar":
                if not isinstance(value,dict) or not all(isinstance(k,str) for k in value): raise RuntimeErrorAF("** argument must be a string-keyed map",location=arg.loc)
                if set(kwargs)&set(value): raise RuntimeErrorAF("Duplicate keyword argument",location=arg.loc)
                if len(kwargs)+len(value)>100_000: raise RuntimeErrorAF("Expanded keyword argument map exceeds limit",location=arg.loc)
                kwargs.update(value)
        if isinstance(target,_UserFunction):
            if target.owner is not self: return target.owner._call_user(target,args,kwargs,node.loc)
            return self._call_user(target,args,kwargs,node.loc)
        if isinstance(target,_SafeModuleMember):
            return self.python_bridge.call(target.module,target.member,*args,**kwargs)
        if isinstance(target,_SafeMethod):
            allowed={"keys","values","items","get","count","index","startswith","endswith","upper","lower","strip","split","join","append","extend","pop"}
            if target.name not in allowed: raise SecurityError("Method not allowed",location=node.loc)
            method=getattr(target.value,target.name,None)
            if not callable(method): raise RuntimeErrorAF("Value does not support this method",location=node.loc)
            if target.name in {"append","extend","pop"} and not isinstance(target.value,list): raise SecurityError("Mutation method is not permitted on this value",location=node.loc)
            if target.name=="append":
                if len(target.value)>=100_000 or len(args)!=1 or kwargs: raise RuntimeErrorAF("append exceeds collection limits or has invalid arguments",location=node.loc)
                value=self._guard_value(args[0],node.loc)
                estimated=_estimate_value_bytes(target.value,self.policy.max_value_bytes)
                estimated += sys.getsizeof(None) + _estimate_value_bytes(value,self.policy.max_value_bytes-estimated)
                if estimated>self.policy.max_value_bytes: raise RuntimeErrorAF("Value memory budget exceeded",location=node.loc)
                return target.value.append(value)
            if target.name=="extend":
                if len(args)!=1 or kwargs or not isinstance(args[0],(list,tuple,range)): raise RuntimeErrorAF("extend requires one bounded sequence",location=node.loc)
                if len(target.value)+len(args[0])>100_000: raise RuntimeErrorAF("Collection size limit exceeded",location=node.loc)
                estimated=_estimate_value_bytes(target.value,self.policy.max_value_bytes); seen: set[int]=set()
                for value in args[0]:
                    estimated += sys.getsizeof(None) + _estimate_value_bytes(value,self.policy.max_value_bytes-estimated,seen)
                    if estimated>self.policy.max_value_bytes: raise RuntimeErrorAF("Value memory budget exceeded",location=node.loc)
                target.value.extend(args[0]); return None
            if target.name=="join":
                if len(args)!=1 or kwargs or not isinstance(args[0],(list,tuple)):
                    raise RuntimeErrorAF("join requires one bounded sequence of strings",location=node.loc)
                separator=target.value
                if not isinstance(separator,str) or not all(isinstance(item,str) for item in args[0]):
                    raise RuntimeErrorAF("join requires strings",location=node.loc)
                total=max(0,len(args[0])-1)*len(separator)
                for item in args[0]:
                    total+=len(item)
                    if total>self.policy.max_output_chars:
                        raise RuntimeErrorAF("join result exceeds configured output budget",location=node.loc)
                joined=separator.join(args[0])
                return self._guard_value(joined,node.loc)
            if target.name=="split":
                if len(args)>2 or kwargs:
                    raise RuntimeErrorAF("split accepts at most two positional arguments",location=node.loc)
                maxsplit=args[1] if len(args)==2 else -1
                if not isinstance(maxsplit,int) or isinstance(maxsplit,bool):
                    raise RuntimeErrorAF("split maxsplit must be an integer",location=node.loc)
                separator=args[0] if args else None
                if separator is not None and not isinstance(separator,str):
                    raise RuntimeErrorAF("split separator must be a string",location=node.loc)
                if separator=="":
                    raise RuntimeErrorAF("empty split separator",location=node.loc)
                if separator is not None:
                    delimiters=target.value.count(separator)
                else:
                    delimiters=0; in_word=False
                    for char in target.value:
                        if char.isspace(): in_word=False
                        elif not in_word: delimiters+=1; in_word=True
                pieces=(delimiters+1 if separator is not None else delimiters) if maxsplit<0 else min(maxsplit,delimiters)+1
                if pieces>100_000:
                    raise RuntimeErrorAF("split result exceeds collection item limit",location=node.loc)
            result=method(*args,**kwargs)
            if target.name in {"keys","values","items"} and isinstance(target.value, dict): result=list(result)
            return self._guard_value(result,node.loc)
        if target not in _BUILTINS.values() and not callable(target): raise RuntimeErrorAF("Value is not callable",location=node.loc)
        if target not in _BUILTINS.values(): raise SecurityError("Calling arbitrary host callables is prohibited",location=node.loc)
        if target is str:
            if len(args)!=1 or kwargs: raise RuntimeErrorAF("str() requires exactly one positional argument",location=node.loc)
            return self._format_value_bounded(args[0],node.loc,self.policy.max_output_chars)
        # Check known materializing built-ins before asking Python to allocate their result.
        sequence_types=(list,tuple,set,dict,str,range)
        if target is _safe_enumerate and args and isinstance(args[0],sequence_types):
            count=len(args[0])
            if count>100_000: raise RuntimeErrorAF("enumerate input exceeds collection item limit",location=node.loc)
            estimate=64+count*128
            if estimate>self.policy.max_value_bytes: raise RuntimeErrorAF("enumerate result would exceed value memory budget",location=node.loc)
        elif target is _safe_zip and args and all(isinstance(value,sequence_types) for value in args):
            if any(len(value)>100_000 for value in args): raise RuntimeErrorAF("zip input exceeds collection item limit",location=node.loc)
            count=min(len(value) for value in args)
            estimate=64+count*(48+8*len(args))
            if estimate>self.policy.max_value_bytes: raise RuntimeErrorAF("zip result would exceed value memory budget",location=node.loc)
        elif target in {list,tuple,set,sorted,_safe_reversed} and args and isinstance(args[0],sequence_types):
            source=args[0]; count=len(source)
            if count>100_000: raise RuntimeErrorAF("Materializing built-in input exceeds collection item limit",location=node.loc)
            if target is set: per_item=64
            elif target is sorted or target is _safe_reversed: per_item=16
            elif isinstance(source,str): per_item=96
            else: per_item=8
            estimate=64+count*per_item
            if estimate>self.policy.max_value_bytes: raise RuntimeErrorAF("Materialized result would exceed value memory budget",location=node.loc)
        elif target is dict:
            count=0
            if args:
                source=args[0]
                if isinstance(source, (dict, list, tuple, range, str)): count = len(source)
                if count>100_000: raise RuntimeErrorAF("Dictionary input exceeds collection item limit",location=node.loc)
            count+=len(kwargs)
            if count>100_000: raise RuntimeErrorAF("Dictionary result exceeds collection item limit",location=node.loc)
            estimate=64+count*128
            if estimate>self.policy.max_value_bytes: raise RuntimeErrorAF("Dictionary result would exceed value memory budget",location=node.loc)
        try: result=target(*args,**kwargs)
        except Exception as exc: raise RuntimeErrorAF("Built-in call failed",location=node.loc,details=type(exc).__name__) from exc
        return self._guard_value(result,node.loc)
    def _call_user(self,fn,args,kwargs,loc):
        self.call_depth+=1
        if self.call_depth>128: self.call_depth-=1; raise RuntimeErrorAF("Maximum function call depth exceeded",location=loc)
        definition=fn.definition; params=definition.parameters; local=dict(fn.closure); pos=0; has_varargs=None; has_kwargs=None
        try:
            for p in params:
                if p.kind=="varargs": has_varargs=p.name; continue
                if p.kind=="kwargs": has_kwargs=p.name; continue
                if pos<len(args):
                    if p.name in kwargs: raise RuntimeErrorAF(f"Argument '{p.name}' supplied twice",location=loc)
                    local[p.name]=args[pos]; pos+=1
                elif p.name in kwargs: local[p.name]=kwargs.pop(p.name)
                elif p.default is not None:
                    old=self.env; self.env=local
                    try: local[p.name]=self._eval(p.default)
                    finally: self.env=old
                else: raise RuntimeErrorAF(f"Missing required argument '{p.name}'",location=loc)
            if has_varargs: local[has_varargs]=tuple(args[pos:]); pos=len(args)
            if pos<len(args): raise RuntimeErrorAF("Too many positional arguments",location=loc)
            if has_kwargs: local[has_kwargs]=dict(kwargs); kwargs={}
            if kwargs: raise RuntimeErrorAF(f"Unexpected keyword argument '{next(iter(kwargs))}'",location=loc)
            old=self.env; old_declared=self.scope_declared; old_shadowed=self.scope_shadowed; old_constants=set(self.constants)
            local_names={p.name for p in params if p.kind in {"normal","varargs","kwargs"}}
            self.env=local; self.scope_declared=[local_names]; self.scope_shadowed=[{}]
            try:
                try: self._execute(definition.body)
                except _ReturnSignal as signal: return self._guard_value(signal.value,loc)
                return None
            finally: self.env=old; self.scope_declared=old_declared; self.scope_shadowed=old_shadowed; self.constants=old_constants
        finally: self.call_depth-=1
    def _format_value_bounded(self,value,loc,limit,nested=False,seen=None,depth=0):
        """Format interpreter values without first materializing an unbounded repr."""
        if limit < 0: raise RuntimeErrorAF("Output budget exceeded",location=loc)
        if seen is None: seen=set()
        if depth > 64: raise RuntimeErrorAF("Output formatting depth limit exceeded",location=loc)
        text: str | None
        if isinstance(value,str):
            text=repr(value) if nested else value
            if len(text)>limit: raise RuntimeErrorAF("Output budget exceeded",location=loc)
            return text
        if value is None:
            text="null"
        elif isinstance(value,bool):
            text="true" if value else "false"
        elif isinstance(value,(int,float,complex)):
            text=str(value)
        else:
            text=None
        if text is not None:
            if len(text)>limit: raise RuntimeErrorAF("Output budget exceeded",location=loc)
            return text
        if not isinstance(value,(list,tuple,set,frozenset,dict,range)):
            text=f"<{type(value).__name__}>"
            if len(text)>limit: raise RuntimeErrorAF("Output budget exceeded",location=loc)
            return text
        if isinstance(value,range):
            text=repr(value)
            if len(text)>limit: raise RuntimeErrorAF("Output budget exceeded",location=loc)
            return text
        identity=id(value)
        if identity in seen:
            text="[...] " if isinstance(value,(list,tuple)) else "{...}"
            text=text.rstrip()
            if len(text)>limit: raise RuntimeErrorAF("Output budget exceeded",location=loc)
            return text
        seen.add(identity)
        pieces=[]; used=0
        def push(text):
            nonlocal used
            if len(text)>limit-used: raise RuntimeErrorAF("Output budget exceeded",location=loc)
            pieces.append(text); used+=len(text)
        def child(item):
            return self._format_value_bounded(item,loc,limit-used,True,seen,depth+1)
        try:
            if isinstance(value,dict):
                push("{")
                for index,(key,item) in enumerate(value.items()):
                    if index: push(", ")
                    push(child(key)); push(": "); push(child(item))
                push("}")
            elif isinstance(value,(set,frozenset)):
                if not value: push("set()" if isinstance(value,set) else "frozenset()")
                else:
                    push("{" if isinstance(value,set) else "frozenset({")
                    for index,item in enumerate(value):
                        if index: push(", ")
                        push(child(item))
                    push("}" if isinstance(value,set) else "})")
            else:
                is_tuple=isinstance(value,tuple)
                push("(" if is_tuple else "[")
                for index,item in enumerate(value):
                    if index: push(", ")
                    push(child(item))
                if is_tuple and len(value)==1: push(",")
                push(")" if is_tuple else "]")
            return "".join(pieces)
        finally:
            seen.discard(identity)
    def _format_fstring(self,s,loc):
        # Name-only interpolation avoids evaluating Python expressions in strings.
        try: template=__import__('ast').literal_eval(s)
        except Exception as exc: raise RuntimeErrorAF("Invalid formatted string",location=loc) from exc
        out=[]; used=0; i=0
        while i<len(template):
            if template.startswith("{{",i):
                if used>=self.policy.max_output_chars: raise RuntimeErrorAF("Output budget exceeded",location=loc)
                out.append("{"); used+=1; i+=2; continue
            if template.startswith("}}",i):
                if used>=self.policy.max_output_chars: raise RuntimeErrorAF("Output budget exceeded",location=loc)
                out.append("}"); used+=1; i+=2; continue
            if template[i]=="{":
                end=template.find("}",i+1)
                if end<0: raise RuntimeErrorAF("Unclosed formatted-string placeholder",location=loc)
                name=template[i+1:end].strip()
                if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*",name) or name not in self.env: raise RuntimeErrorAF(f"Unknown formatted-string name '{name}'",location=loc)
                rendered=self._format_value_bounded(self.env[name],loc,self.policy.max_output_chars-used)
                out.append(rendered); used+=len(rendered); i=end+1; continue
            if template[i]=="}": raise RuntimeErrorAF("Unmatched closing brace in formatted string",location=loc)
            if used>=self.policy.max_output_chars: raise RuntimeErrorAF("Output budget exceeded",location=loc)
            out.append(template[i]); used+=1; i+=1
        return self._guard_value("".join(out),loc)
    def _declare(self,name,value,loc,constant=False):
        current=self.scope_declared[-1]
        if name in current: raise RuntimeErrorAF(f"Name '{name}' already declared in this scope",location=loc)
        if name in self.env and name not in self.scope_shadowed[-1]: self.scope_shadowed[-1][name]=(self.env[name],name in self.constants)
        self.env[name]=value; current.add(name)
        if constant:self.constants.add(name)
        else:self.constants.discard(name)
    def _execute(self,nodes):
        for node in nodes:
            self._step(node.loc)
            if isinstance(node,A.ProjectDecl): continue
            if isinstance(node,A.LetDecl): self._declare(node.name,self._eval(node.value),node.loc)
            elif isinstance(node,A.ConstantDecl): self._declare(node.name,self._eval(node.value),node.loc,constant=True)
            elif isinstance(node,A.Assign):
                if node.name not in self.env:
                    self._declare(node.name, self._eval(node.value), node.loc)
                    continue
                if node.name in self.constants: raise RuntimeErrorAF(f"Cannot reassign constant '{node.name}'",location=node.loc)
                self.env[node.name]=self._eval(node.value)
            elif isinstance(node,A.AugAssign):
                if node.name not in self.env or node.name in self.constants: raise RuntimeErrorAF(f"Variable '{node.name}' is undeclared or constant",location=node.loc)
                value=self._eval(node.value); op=_BINOPS.get(node.op)
                if op is None: raise RuntimeErrorAF("Unsupported augmented assignment",location=node.loc)
                self.env[node.name]=self._apply_binary(node.op,self.env[node.name],value,node.loc)
            elif isinstance(node,A.Show):
                pieces=[]; remaining=self.policy.max_output_chars-self.output_chars
                for index,expression in enumerate(node.values):
                    value=self._eval(expression)
                    if index:
                        if remaining<1: raise RuntimeErrorAF("Output budget exceeded",location=node.loc)
                        pieces.append(" "); remaining-=1
                    rendered=self._format_value_bounded(value,node.loc,remaining)
                    pieces.append(rendered); remaining-=len(rendered)
                text="".join(pieces)
                if self.output_chars+len(text)>self.policy.max_output_chars: raise RuntimeErrorAF("Output budget exceeded",location=node.loc)
                self.output.append(text); self.output_chars+=len(text)
                if self.output_fn: self.output_fn(text)
            elif isinstance(node,A.ExprStmt): self._eval(node.value)
            elif isinstance(node,A.If):
                selected=next((body for cond,body in node.branches if _truth(self._eval(cond),cond.loc)),node.else_body)
                self._execute_scoped(selected)
            elif isinstance(node,A.While):
                iterations=0
                while _truth(self._eval(node.condition),node.condition.loc):
                    iterations+=1; self.loop_count+=1
                    if iterations>self.policy.max_loop_iterations: raise RuntimeErrorAF("Loop iteration limit exceeded",location=node.loc)
                    try: self._execute_scoped(node.body)
                    except _SkipSignal: continue
                    except _StopSignal: break
            elif isinstance(node,A.For):
                iterable=self._eval(node.iterable)
                if not isinstance(iterable,(list,tuple,set,dict,str,range)): raise RuntimeErrorAF("for loop requires a bounded built-in iterable",location=node.loc)
                if len(iterable)>100_000: raise RuntimeErrorAF("Loop iterable exceeds item limit",location=node.loc)
                old_present=node.name in self.env; old=self.env.get(node.name); count=0
                try:
                    for item in iterable:
                        count+=1; self.loop_count+=1
                        if count>self.policy.max_loop_iterations: raise RuntimeErrorAF("Loop iteration limit exceeded",location=node.loc)
                        self.env[node.name]=item
                        try: self._execute_scoped(node.body)
                        except _SkipSignal: continue
                        except _StopSignal: break
                finally:
                    if old_present: self.env[node.name]=old
                    else: self.env.pop(node.name,None)
            elif isinstance(node,A.Repeat):
                count=self._eval(node.count)
                if not isinstance(count,int) or isinstance(count,bool) or count<0 or count>self.policy.max_loop_iterations: raise RuntimeErrorAF("repeat count must be a non-negative integer within the loop limit",location=node.loc)
                for _ in range(count):
                    self.loop_count+=1
                    try: self._execute_scoped(node.body)
                    except _SkipSignal: continue
                    except _StopSignal: break
            elif isinstance(node,A.FunctionDef):
                if node.name in self._predeclared and self.functions.get(node.name) is not None and self.functions[node.name].definition is node:
                    self._predeclared.discard(node.name); continue
                if node.name in self.env or node.name in self.functions: raise RuntimeErrorAF(f"Function '{node.name}' already declared",location=node.loc)
                self.functions[node.name]=_UserFunction(node,self.env,self)
            elif isinstance(node,A.Return): raise _ReturnSignal(self._eval(node.value) if node.value else None)
            elif isinstance(node,A.Raise):
                value=self._eval(node.value)
                if isinstance(value,_ErrorValue): raise value.original
                raise RuntimeErrorAF(str(value),location=node.loc)
            elif isinstance(node,A.Try): self._execute_try(node)
            elif isinstance(node,A.Stop): raise _StopSignal()
            elif isinstance(node,A.Skip): raise _SkipSignal()
            elif isinstance(node,A.Import):
                local_path=self._find_local_module(node.module)
                if local_path is not None:
                    self._declare(node.alias or node.module.split('.')[-1],self._load_local_module(node.module,local_path,node.loc),node.loc)
                    continue
                module_name=node.module.split('.')[0]
                if is_python_module_hard_denied(node.module): raise SecurityError(f"Python module '{node.module}' is blocked by the hard security policy",location=node.loc)
                if module_name not in self.policy.allowed_python_modules: raise SecurityError(f"Python module '{node.module}' is not approved",location=node.loc)
                if f"python.module:{node.module}" not in self.policy.capabilities: raise SecurityError(f"Import requires explicit capability 'python.module:{node.module}'",location=node.loc)
                self._declare(node.alias or module_name,_SafeModule(node.module),node.loc)
            elif isinstance(node,A.FromImport):
                local_path=self._find_local_module(node.module)
                if local_path is not None:
                    module=self._load_local_module(node.module,local_path,node.loc)
                    for name in node.names:
                        if name.startswith('_'): raise SecurityError("Private module names cannot be imported",location=node.loc)
                        if name in module.values:self._declare(name,module.values[name],node.loc,constant=name in module.constants)
                        elif name in module.functions:self._declare(name,module.functions[name],node.loc)
                        else: raise RuntimeErrorAF(f"Module '{node.module}' has no exported name '{name}'",location=node.loc)
                    continue
                if is_python_module_hard_denied(node.module): raise SecurityError(f"Python module '{node.module}' is blocked by the hard security policy",location=node.loc)
                if node.module not in self.policy.allowed_python_modules: raise SecurityError(f"Python module '{node.module}' is not approved",location=node.loc)
                if f"python.module:{node.module}" not in self.policy.capabilities: raise SecurityError(f"Import requires explicit capability 'python.module:{node.module}'",location=node.loc)
                for name in node.names:
                    if name.startswith("_"): raise SecurityError("Private Python names cannot be imported",location=node.loc)
                    self._declare(name,_SafeModuleMember(node.module,name),node.loc)
            else: raise RuntimeErrorAF(f"Unsupported statement: {type(node).__name__}",location=node.loc)
    def _execute_try(self,node:A.Try):
        if not node.handlers and not node.finally_body:
            raise RuntimeErrorAF("try requires at least one except or finally clause",location=node.loc)
        try:
            try:
                self._execute_scoped(node.body)
            except (RuntimeErrorAF,PythonBridgeError,DatabaseErrorAF,ImportErrorAF) as exc:
                handler=next((h for h in node.handlers if _matches_exception(exc,h.exception_types)),None)
                if handler is None: raise
                error_loc=getattr(exc,"location",node.loc)
                with suppress(OSError):
                    write_report(Diagnostic("AF-RUNTIME-HANDLED","runtime",Severity.WARNING,
                        "A runtime error was caught by an AssayFlux exception handler",error_loc,
                        details=f"{getattr(exc,'code','AF-RUNTIME-001')}: {getattr(exc,'message',str(exc))}",
                        suggestion="Review the handled condition to ensure the recovery is intentional."))
                err=_ErrorValue(exc,getattr(exc,"code","AF-ERROR"),getattr(exc,"message",str(exc)),getattr(exc,"category","runtime"),getattr(error_loc,"line",node.loc.line),getattr(error_loc,"column",node.loc.column))
                self.scope_declared.append(set()); self.scope_shadowed.append({})
                try:
                    if handler.name:self._declare(handler.name,err,handler.loc)
                    self._execute(handler.body)
                finally:
                    declared=self.scope_declared.pop(); shadowed=self.scope_shadowed.pop()
                    for key in declared:self.env.pop(key,None);self.constants.discard(key)
                    for key,(value,was_constant) in shadowed.items():
                        self.env[key]=value
                        if was_constant:self.constants.add(key)
                        else:self.constants.discard(key)
            else:
                if node.else_body:self._execute_scoped(node.else_body)
        finally:
            if node.finally_body:self._execute_scoped(node.finally_body)
    def _find_local_module(self,module_name:str):
        if self.workspace is None:return None
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*",module_name):return None
        relative=Path(*module_name.split('.'))
        for suffix in (".af",".assayflux"):
            candidate=self.workspace/(str(relative)+suffix)
            if candidate.is_symlink(): raise SecurityError("Symbolic-link module imports are not permitted")
            try: resolved=candidate.resolve(strict=True)
            except FileNotFoundError: continue
            except OSError as exc: raise RuntimeErrorAF("Could not resolve module path",details=type(exc).__name__) from exc
            if resolved!=self.workspace and self.workspace not in resolved.parents: raise SecurityError("Module path escapes the project workspace")
            if not resolved.is_file(): continue
            return resolved
        return None
    def _load_local_module(self,module_name:str,path:Path,loc):
        self.python_bridge.capabilities.require("module.import",operation=f"import AssayFlux module {module_name}",location=loc)
        if not self.policy.allow_file_imports: raise SecurityError("Project module imports are disabled",location=loc,suggestion="Enable them explicitly from the trusted CLI with --allow-project-imports.")
        key=str(path.resolve())
        if key in self._shared.module_cache:return self._shared.module_cache[key]
        if key in self._shared.modules_loading: raise RuntimeErrorAF(f"Circular import detected for module '{module_name}'",location=loc)
        if len(self._shared.module_cache)>=256: raise SecurityError("Project module count exceeds the configured safety limit",location=loc)
        if self._shared.import_depth>=64: raise SecurityError("Project module import depth exceeds the configured safety limit",location=loc)
        self._shared.modules_loading.add(key); self._shared.import_depth+=1
        try:
            source=read_source(path,self.policy); program=parse(source,str(path)); check(program)
            child=Interpreter(self.policy,output_fn=self.output_fn,workspace=self.workspace,_shared=self._shared)
            child.output=self.output
            child.env={}; child.constants=set(); child.scope_declared=[set()]; child.scope_shadowed=[{}]; child.functions={}; child._predeclared=set()
            child.run(program,validate=False)
            module=_AssayFluxModule(module_name,dict(child.env),dict(child.functions),frozenset(child.constants))
            self._shared.module_cache[key]=module
            return module
        finally:self._shared.modules_loading.discard(key); self._shared.import_depth-=1
    def _execute_scoped(self,nodes):
        # Assignments to existing names remain visible; declarations shadow
        # outer names only within this block and are restored on exit.
        self.scope_declared.append(set()); self.scope_shadowed.append({})
        try: self._execute(nodes)
        finally:
            declared=self.scope_declared.pop(); shadowed=self.scope_shadowed.pop()
            for key in declared:
                self.env.pop(key,None); self.constants.discard(key)
            for key,(value,was_constant) in shadowed.items():
                self.env[key]=value
                if was_constant:self.constants.add(key)
                else:self.constants.discard(key)
    def run(self,program:A.Program,*,validate:bool=True)->ExecutionResult:
        if validate:
            validate_ast(program); check(program)
        # Top-level functions are registered before execution so calls may refer
        # to functions declared later in the same module.
        seen=set()
        for node in program.statements:
            if isinstance(node,A.FunctionDef):
                if node.name in seen or node.name in self.functions or node.name in self.env:
                    raise RuntimeErrorAF(f"Function '{node.name}' already declared",location=node.loc)
                seen.add(node.name); self.functions[node.name]=_UserFunction(node,self.env,self); self._predeclared.add(node.name)
        try: self._execute(program.statements)
        except _ReturnSignal as exc: raise RuntimeErrorAF("return used outside a function") from exc
        except _StopSignal as exc: raise RuntimeErrorAF("stop used outside a loop") from exc
        except _SkipSignal as exc: raise RuntimeErrorAF("skip used outside a loop") from exc
        return ExecutionResult(self.output[:],self.env.copy(),self.steps)

@dataclass(frozen=True, slots=True)
class _SafeModuleMember:
    module:str; member:str
@dataclass(frozen=True, slots=True)
class _SafeMethod:
    value:Any; name:str

def _truth(value,loc):
    if not isinstance(value,bool): raise RuntimeErrorAF("Conditions must evaluate to boolean",location=loc,suggestion="Use an explicit comparison such as 'count > 0'.")
    return value


def _matches_exception(exc, names):
    if names is None: return True
    for name in names:
        if name in {"Exception","AssayFluxError"}: return True
        if name in {"RuntimeError","RuntimeErrorAF"} and isinstance(exc,RuntimeErrorAF): return True
        if name=="PythonBridgeError" and isinstance(exc,PythonBridgeError): return True
        if name=="DatabaseErrorAF" and isinstance(exc,DatabaseErrorAF): return True
        if name=="ImportErrorAF" and isinstance(exc,ImportErrorAF): return True
        if name in {"TypeError","ValueError","OverflowError","IndexError","KeyError"} and getattr(exc,"details",None)==name: return True
        if name=="ZeroDivisionError" and isinstance(exc,RuntimeErrorAF) and exc.message=="Division by zero": return True
    return False
