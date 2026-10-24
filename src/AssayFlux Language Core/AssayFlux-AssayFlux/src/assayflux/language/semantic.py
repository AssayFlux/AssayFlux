"""Conservative semantic checks: name resolution, constants, and known value types."""
from __future__ import annotations

from assayflux.diagnostics.model import TypeCheckError

from . import ast_nodes as A

_BUILTINS={"range","len","abs","min","max","sum","round","str","int","float","bool","list","tuple","dict","set","enumerate","zip","sorted","reversed","all","any","divmod","pow"}
_NUM={"number","complex","unknown"}

def _infer(node, env, known_functions, imports):
    if isinstance(node,A.Literal):
        v=node.value
        if isinstance(v,tuple) and len(v)==2 and v[0]=="__fstring__": return "string"
        if v is None:return "null"
        if isinstance(v,bool):return "bool"
        if isinstance(v,complex):return "complex"
        if isinstance(v,(int,float)):return "number"
        if isinstance(v,str):return "string"
    if isinstance(node,A.Variable):
        if node.name in env:return env[node.name][0]
        if node.name in known_functions or node.name in _BUILTINS:return "callable"
        raise TypeCheckError(f"Undefined name '{node.name}'",location=node.loc,suggestion="Declare the name or import an approved module before using it.")
    if isinstance(node,(A.ListLiteral,A.TupleLiteral,A.SetLiteral)):
        for item in node.values:_infer(item,env,known_functions,imports)
        return "collection"
    if isinstance(node,A.Comprehension):
        iterable_type=_infer(node.iterable,env,known_functions,imports)
        local=dict(env); local[node.name]=( "unknown",False)
        if node.condition is not None:
            condition_type=_infer(node.condition,local,known_functions,imports)
            if condition_type not in {"bool","unknown"}: raise TypeCheckError("Comprehension filter must be boolean",location=node.condition.loc)
        _infer(node.element,local,known_functions,imports)
        if node.key is not None:_infer(node.key,local,known_functions,imports)
        if iterable_type not in {"collection","mapping","string","unknown"}: raise TypeCheckError("Comprehension requires an iterable",location=node.iterable.loc)
        return "mapping" if node.kind=="dict" else "collection"
    if isinstance(node,A.DictLiteral):
        for k,v in node.values:_infer(k,env,known_functions,imports);_infer(v,env,known_functions,imports)
        return "mapping"
    if isinstance(node,A.Unary):
        t=_infer(node.value,env,known_functions,imports)
        if node.op in {"-","+","~"} and t not in _NUM:raise TypeCheckError(f"Unary '{node.op}' requires a numeric operand",location=node.loc)
        if node.op=="~" and t=="complex":raise TypeCheckError("Bitwise inversion does not support complex numbers",location=node.loc)
        if node.op=="not" and t not in {"bool","unknown"}:raise TypeCheckError("'not' requires a boolean",location=node.loc)
        return "bool" if node.op=="not" else ("complex" if t=="complex" else "number")
    if isinstance(node,A.Compare):
        types=[_infer(item,env,known_functions,imports) for item in node.operands]
        for index,op in enumerate(node.operators):
            if op in {"<",">","<=",">="} and "complex" in {types[index],types[index+1]}:
                raise TypeCheckError("Ordered comparisons do not support complex numbers",location=node.loc)
        return "bool"
    if isinstance(node,A.Binary):
        left_type=_infer(node.left,env,known_functions,imports);right_type=_infer(node.right,env,known_functions,imports)
        if node.op in {"and","or"}:return "unknown"
        if node.op in {"==","!=","<",">","<=",">=","in","not in","is","is not"}:return "bool"
        if node.op=="@":
            if left_type not in {"collection","unknown"} or right_type not in {"collection","unknown"}: raise TypeCheckError("Matrix multiplication requires collection operands",location=node.loc)
            return "unknown"
        if node.op=="+" and left_type==right_type and left_type in {"string","collection"}:return left_type
        if node.op=="+" and "unknown" in {left_type,right_type}: return "unknown"
        if node.op=="*" and ((l in {"string","collection"} and r in _NUM) or (r in {"string","collection"} and l in _NUM)):
            return l if l in {"string","collection"} else r
        if l not in _NUM or r not in _NUM:raise TypeCheckError(f"Operator '{node.op}' expects compatible numeric operands",location=node.loc)
        if node.op in {"//","%","&","|","^","<<",">>"} and "complex" in {l,r}:
            raise TypeCheckError(f"Operator '{node.op}=' does not support complex numbers",location=node.loc)
        return "complex" if "complex" in {l,r} else "number"
    if isinstance(node,A.Conditional):
        _infer(node.condition,env,known_functions,imports);a=_infer(node.value,env,known_functions,imports);b=_infer(node.otherwise,env,known_functions,imports)
        return a if a==b else "unknown"
    if isinstance(node,A.Attribute):
        base_type=_infer(node.value,env,known_functions,imports)
        if base_type=="error" and node.name in {"message","code","category"}:return "string"
        if base_type=="error" and node.name in {"line","column"}:return "number"
        return "callable"
    if isinstance(node,A.Index):_infer(node.value,env,known_functions,imports);_infer(node.index,env,known_functions,imports);return "unknown"
    if isinstance(node,A.Lambda):
        _validate_signature(node)
        local=dict(env)
        for parameter in node.parameters:
            if parameter.default is not None:_infer(parameter.default,env,known_functions,imports)
            local[parameter.name]=(_annotation_type(parameter.annotation),False)
        _infer(node.body,local,known_functions,imports)
        return "callable"
    if isinstance(node,A.Call):
        seen_keyword=False
        for arg in node.arguments:
            if arg.kind in {"keyword","kwstar"}: seen_keyword=True
            elif arg.kind=="positional" and seen_keyword: raise TypeCheckError("Positional argument cannot follow a keyword argument",location=arg.loc)
            _infer(arg.value,env,known_functions,imports)
        _infer(node.function,env,known_functions,imports)
        if isinstance(node.function,A.Variable) and node.function.name in known_functions:
            definition=known_functions[node.function.name]
            params=list(definition.parameters); normal=[p for p in params if p.kind=="normal"]
            by_name={p.name:p for p in normal}; assigned={}; positional_index=0; has_varargs=any(p.kind=="varargs" for p in params); has_kwargs=any(p.kind=="kwargs" for p in params); dynamic=False
            for arg in node.arguments:
                if arg.kind in {"star","kwstar"}: dynamic=True; continue
                if arg.kind=="positional":
                    if positional_index<len(normal): param=normal[positional_index]; positional_index+=1
                    elif has_varargs: continue
                    else: raise TypeCheckError(f"Too many positional arguments for '{definition.name}'",location=arg.loc)
                    if param.name in assigned: raise TypeCheckError(f"Argument '{param.name}' supplied more than once",location=arg.loc)
                    assigned[param.name]=arg.value
                elif arg.kind=="keyword":
                    if arg.name not in by_name:
                        if has_kwargs: continue
                        raise TypeCheckError(f"Unexpected keyword argument '{arg.name}' for '{definition.name}'",location=arg.loc)
                    if arg.name in assigned: raise TypeCheckError(f"Argument '{arg.name}' supplied more than once",location=arg.loc)
                    assigned[arg.name]=arg.value
            for param in normal:
                if param.name not in assigned and param.default is None and not dynamic:
                    raise TypeCheckError(f"Missing required argument '{param.name}' for '{definition.name}'",location=node.loc)
                if param.name in assigned:
                    actual=_infer(assigned[param.name],env,known_functions,imports); expected=_annotation_type(param.annotation)
                    if expected!="unknown" and actual not in {expected,"unknown"}:
                        raise TypeCheckError(f"Argument '{param.name}' expects {expected}, received {actual}",location=assigned[param.name].loc)
            return _annotation_type(definition.return_type)
        if isinstance(node.function,A.Variable) and node.function.name in {"len","abs","min","max","sum","round","str","int","float","bool"}:
            return {"len":"number","str":"string","bool":"bool","int":"number","float":"number"}.get(node.function.name,"unknown")
        return "unknown"
    raise TypeCheckError(f"Semantic checker does not support expression node '{type(node).__name__}'",location=getattr(node,"loc",None))

def _annotation_type(name):
    return {"int":"number","float":"number","complex":"complex","str":"string","bool":"bool","list":"collection","tuple":"collection","set":"collection","dict":"mapping","None":"null","Any":"unknown"}.get(name or "unknown", "unknown")

def _validate_signature(definition):
    seen_names=set(); seen_default=False; seen_varargs=False; seen_kwargs=False
    for parameter in definition.parameters:
        if parameter.name in seen_names: raise TypeCheckError(f"Duplicate parameter '{parameter.name}'",location=parameter.loc)
        seen_names.add(parameter.name)
        if seen_kwargs: raise TypeCheckError("No parameter may follow **kwargs",location=parameter.loc)
        if parameter.kind=="kwargs": seen_kwargs=True; continue
        if parameter.kind=="varargs":
            if seen_varargs: raise TypeCheckError("Only one *args parameter is allowed",location=parameter.loc)
            seen_varargs=True; continue
        if seen_varargs: raise TypeCheckError("Parameters after *args are not supported by this grammar",location=parameter.loc)
        if parameter.default is not None: seen_default=True
        elif seen_default: raise TypeCheckError("A required parameter cannot follow a parameter with a default",location=parameter.loc)

def _collect_returns(nodes):
    found=[]
    for node in nodes:
        if isinstance(node,A.Return): found.append(node)
        elif isinstance(node,A.FunctionDef): continue
        elif isinstance(node,A.If):
            for _,body in node.branches: found.extend(_collect_returns(body))
            found.extend(_collect_returns(node.else_body))
        elif isinstance(node,(A.While,A.For,A.Repeat)): found.extend(_collect_returns(node.body))
    return found

def check(program:A.Program)->list[str]:
    env:dict[str,tuple[str,bool]]={};warnings=[];function_depth=0;loop_depth=0;return_type_stack=[];known_functions={};imports=set()
    def collect_functions(nodes):
        seen_here=set()
        for item in nodes:
            if isinstance(item,A.FunctionDef):
                if item.name in seen_here: raise TypeCheckError(f"Function '{item.name}' is declared more than once in the same scope",location=item.loc)
                _validate_signature(item)
                seen_here.add(item.name); known_functions.setdefault(item.name,item); collect_functions(item.body)
            elif isinstance(item,A.If):
                for _,body in item.branches: collect_functions(body)
                collect_functions(item.else_body)
            elif isinstance(item,(A.While,A.For,A.Repeat)): collect_functions(item.body)
            elif isinstance(item,A.Try):
                collect_functions(item.body)
                for handler in item.handlers: collect_functions(handler.body)
                collect_functions(item.else_body); collect_functions(item.finally_body)
    collect_functions(program.statements)
    def statements(nodes, local=False):
        nonlocal function_depth, loop_depth
        for node in nodes:
            if isinstance(node,A.ProjectDecl):continue
            if isinstance(node,A.Import):
                name=node.alias or node.module.split('.')[-1]
                if name in env and not local: raise TypeCheckError(f"Name '{name}' is already declared",location=node.loc)
                if name in known_functions and not local: raise TypeCheckError(f"Import name '{name}' conflicts with a function",location=node.loc)
                env[name]=("module",False); continue
            if isinstance(node,A.FromImport):
                for name in node.names:
                    if name in env and not local: raise TypeCheckError(f"Name '{name}' is already declared",location=node.loc)
                    if name in known_functions and not local: raise TypeCheckError(f"Import name '{name}' conflicts with a function",location=node.loc)
                    env[name]=("callable",False)
                continue
            if isinstance(node,(A.LetDecl,A.ConstantDecl)):
                if node.name in env and not local:raise TypeCheckError(f"Name '{node.name}' is already declared",location=node.loc)
                if node.name in known_functions and not local: raise TypeCheckError(f"Name '{node.name}' conflicts with a function",location=node.loc)
                typ=_infer(node.value,env,known_functions,imports);env[node.name]=(typ,isinstance(node,A.ConstantDecl));continue
            if isinstance(node,A.Assign):
                if node.name not in env:
                    env[node.name] = (_infer(node.value,env,known_functions,imports),False)
                    continue
                typ,constant=env[node.name]
                if constant:raise TypeCheckError(f"Cannot reassign constant '{node.name}'",location=node.loc)
                got=_infer(node.value,env,known_functions,imports)
                if typ not in {"unknown",got} and got!="unknown" and not (typ=="number" and got=="number"):
                    raise TypeCheckError(f"Assignment changes '{node.name}' from {typ} to {got}",location=node.loc)
                continue
            if isinstance(node,A.AugAssign):
                if node.name not in env:raise TypeCheckError(f"Cannot assign to undeclared variable '{node.name}'",location=node.loc)
                target_type,constant=env[node.name]
                if constant:raise TypeCheckError(f"Cannot reassign constant '{node.name}'",location=node.loc)
                value_type=_infer(node.value,env,known_functions,imports)
                if node.op == "+":
                    numeric = target_type in _NUM and value_type in _NUM
                    same_sequence = target_type == value_type and target_type in {"string","collection"}
                    if not (numeric or same_sequence or "unknown" in {target_type,value_type}):
                        raise TypeCheckError(
                            f"Operator '+=' cannot combine {target_type} and {value_type}",
                            location=node.loc,
                        )
                elif node.op == "*" and target_type in {"string","collection"}:
                    if value_type not in {"number","unknown"}:
                        raise TypeCheckError(
                            f"Operator '*=' requires a numeric repeat count, received {value_type}",
                            location=node.loc,
                        )
                else:
                    if target_type not in _NUM or value_type not in _NUM:
                        raise TypeCheckError(
                            f"Operator '{node.op}' expects numeric operands",
                            location=node.loc,
                        )
                    if node.op in {"//","%"} and "complex" in {target_type,value_type}:
                        raise TypeCheckError(
                            f"Operator '{node.op}' does not support complex numbers",
                            location=node.loc,
                        )
                continue
            if isinstance(node,A.Show):
                for x in node.values:_infer(x,env,known_functions,imports)
                continue
            if isinstance(node,A.ExprStmt):_infer(node.value,env,known_functions,imports);continue
            if isinstance(node,A.If):
                for cond,body in node.branches:
                    typ=_infer(cond,env,known_functions,imports)
                    if typ not in {"bool","unknown"}: raise TypeCheckError("if condition should be boolean",location=cond.loc)
                    old=env.copy();statements(body,True);env.clear();env.update(old)
                old=env.copy();statements(node.else_body,True);env.clear();env.update(old);continue
            if isinstance(node,(A.While,A.For,A.Repeat)):
                if isinstance(node,A.While):
                    typ=_infer(node.condition,env,known_functions,imports)
                    if typ not in {"bool","unknown"}:raise TypeCheckError("while condition should be boolean",location=node.condition.loc)
                    body=node.body;loop_name=None
                elif isinstance(node,A.For):
                    iterable_type=_infer(node.iterable,env,known_functions,imports)
                    if iterable_type not in {"collection","mapping","string","unknown"}:
                        raise TypeCheckError(
                            f"for loop requires an iterable, received {iterable_type}",
                            location=node.iterable.loc,
                            suggestion="Use a list, tuple, set, mapping, string, or bounded iterable such as range(...).",
                        )
                    body=node.body;loop_name=node.name
                else:
                    _infer(node.count,env,known_functions,imports);body=node.body;loop_name=None
                old=env.copy()
                if loop_name:env[loop_name]=("unknown",False)
                loop_depth+=1
                try: statements(body,True)
                finally: loop_depth-=1;env.clear();env.update(old)
                continue
            if isinstance(node,A.FunctionDef):
                old=env.copy()
                for p in node.parameters:
                    if p.default is not None:
                        default_type=_infer(p.default,env,known_functions,imports); expected_default=_annotation_type(p.annotation)
                        if expected_default!="unknown" and default_type not in {expected_default,"unknown"}: raise TypeCheckError(f"Default for parameter '{p.name}' expects {expected_default}, received {default_type}",location=p.loc)
                localenv={p.name:(_annotation_type(p.annotation),False) for p in node.parameters if p.kind=="normal"}
                localenv.update({p.name:("collection" if p.kind=="varargs" else "mapping",False) for p in node.parameters if p.kind in {"varargs","kwargs"}})
                env.clear();env.update(old);env.update(localenv)
                function_depth+=1; return_type_stack.append(_annotation_type(node.return_type))
                try: statements(node.body,True)
                finally: function_depth-=1; return_type_stack.pop(); env.clear();env.update(old)
                continue
            if isinstance(node,A.Return):
                if function_depth==0: raise TypeCheckError("return used outside a function",location=node.loc)
                actual=_infer(node.value,env,known_functions,imports) if node.value is not None else "null"
                expected=return_type_stack[-1] if return_type_stack else "unknown"
                if expected!="unknown" and actual not in {expected,"unknown"}:
                    raise TypeCheckError(f"Function return type expects {expected}, received {actual}",location=node.loc)
                continue
            if isinstance(node,A.Raise):
                raised_type=_infer(node.value,env,known_functions,imports)
                if raised_type not in {"string","error","unknown"}: raise TypeCheckError("raise expects an error value or a message string",location=node.loc)
                continue
            if isinstance(node,A.Try):
                if not node.handlers and not node.finally_body: raise TypeCheckError("try requires at least one except or finally clause",location=node.loc)
                if node.else_body and not node.handlers: raise TypeCheckError("try-else requires at least one except clause",location=node.loc)
                allowed_exceptions={"Exception","AssayFluxError","RuntimeError","RuntimeErrorAF","PythonBridgeError","DatabaseErrorAF","ImportErrorAF","TypeError","ValueError","OverflowError","IndexError","KeyError","ZeroDivisionError"}
                old=env.copy(); statements(node.body,True); env.clear();env.update(old)
                for handler in node.handlers:
                    if handler.exception_types is not None:
                        for name in handler.exception_types:
                            if name not in allowed_exceptions: raise TypeCheckError(f"Exception type '{name}' is not catchable by AssayFlux",location=handler.loc,suggestion="Security errors are intentionally not catchable.")
                    old=env.copy()
                    if handler.name: env[handler.name]=("error",False)
                    statements(handler.body,True); env.clear();env.update(old)
                if node.else_body:
                    old=env.copy(); statements(node.else_body,True); env.clear();env.update(old)
                if node.finally_body:
                    old=env.copy(); statements(node.finally_body,True); env.clear();env.update(old)
                continue
            if isinstance(node,(A.Stop,A.Skip)):
                if loop_depth==0: raise TypeCheckError(f"{'stop' if isinstance(node,A.Stop) else 'skip'} used outside a loop",location=node.loc)
                continue
            raise TypeCheckError(f"Semantic checker does not support statement '{type(node).__name__}'",location=node.loc)
    statements(program.statements)
    return warnings
