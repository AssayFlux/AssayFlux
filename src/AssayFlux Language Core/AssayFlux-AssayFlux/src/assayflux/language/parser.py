"""Lark parser using the canonical AssayFlux grammar and source-located AST."""
from __future__ import annotations

import ast as py_ast
from pathlib import Path
from typing import ClassVar

from lark import Lark, Token, Transformer, v_args
from lark.exceptions import UnexpectedInput, VisitError
from lark.indenter import Indenter

from assayflux.diagnostics.model import AstError, ParseError, SourceLocation

from . import ast_nodes as A
from .ast_validator import validate_ast


class AssayFluxIndenter(Indenter):
    NL_type = "_NL"
    OPEN_PAREN_types: ClassVar[list[str]] = ["LPAR", "LSQB", "LBRACE"]
    CLOSE_PAREN_types: ClassVar[list[str]] = ["RPAR", "RSQB", "RBRACE"]
    INDENT_type = "_INDENT"
    DEDENT_type = "_DEDENT"
    tab_len = 8

_GRAMMAR = Path(__file__).with_name("grammar.lark").read_text(encoding="utf-8")
_PARSER = Lark(_GRAMMAR, parser="lalr", lexer="contextual", postlex=AssayFluxIndenter(),
               propagate_positions=True, maybe_placeholders=False, start="start")

def _loc(obj, filename: str) -> SourceLocation:
    return SourceLocation(filename, getattr(obj, "line", 1) or 1, getattr(obj, "column", 1) or 1,
                          getattr(obj, "end_line", None), getattr(obj, "end_column", None))
def _rule_loc(meta, filename):
    return SourceLocation(filename, getattr(meta,"line",1) or 1, getattr(meta,"column",1) or 1, getattr(meta,"end_line",None), getattr(meta,"end_column",None))

def _unquote(s: str) -> str:
    try: return py_ast.literal_eval(s)
    except (ValueError, SyntaxError) as exc: raise ParseError("Invalid string literal", details=type(exc).__name__) from exc

class _BuildAST(Transformer):
    def __init__(self, filename): super().__init__(); self.filename = filename
    def start(self, items): return A.Program(SourceLocation(self.filename), tuple(x for x in items if isinstance(x, A.Node)))
    @v_args(meta=True)
    def project_decl(self, meta, xs): return A.ProjectDecl(_rule_loc(meta,self.filename), _unquote(str(xs[0])))
    @v_args(meta=True)
    def let_decl(self, meta, xs): return A.LetDecl(_rule_loc(meta,self.filename), str(xs[0]), xs[1])
    @v_args(meta=True)
    def constant_decl(self, meta, xs): return A.ConstantDecl(_rule_loc(meta,self.filename), str(xs[0]), xs[1])
    @v_args(meta=True)
    def assign_stmt(self, meta, xs): return A.Assign(_rule_loc(meta,self.filename), str(xs[0]), xs[1])
    @v_args(meta=True)
    def aug_assign(self, meta, xs): return A.AugAssign(_rule_loc(meta,self.filename), str(xs[0]), str(xs[1])[:-1], xs[2])
    @v_args(meta=True)
    def show_stmt(self, meta, xs):
        values = xs[0] if xs else ()
        return A.Show(_rule_loc(meta,self.filename), tuple(values))
    def expr_list(self, xs): return tuple(xs)
    def block(self, xs): return tuple(x for x in xs if isinstance(x, A.Node))
    @v_args(meta=True)
    def if_stmt(self, meta, xs):
        cond=next(x for x in xs if isinstance(x,A.Node))
        tuples=[x for x in xs if isinstance(x,tuple)]
        body=next((x for x in tuples if all(isinstance(n,A.Node) and not isinstance(n,A.Parameter) for n in x)),())
        branches=[(cond,body)]; else_body=()
        for item in xs:
            if isinstance(item,tuple) and item and item[0]=="otherwise": branches.append((item[1],item[2]))
            elif isinstance(item,tuple) and item and item[0]=="else": else_body=item[1]
        return A.If(_rule_loc(meta,self.filename),tuple(branches),else_body)
    def otherwise_branch(self, xs):
        cond=next(x for x in xs if isinstance(x,A.Node))
        body=next((x for x in xs if isinstance(x,tuple) and all(isinstance(n,A.Node) and not isinstance(n,A.Parameter) for n in x)),())
        return ("otherwise",cond,body)
    def else_branch(self, xs):
        body=next((x for x in xs if isinstance(x,tuple) and all(isinstance(n,A.Node) and not isinstance(n,A.Parameter) for n in x)),())
        return ("else",body)
    @v_args(meta=True)
    def while_stmt(self, meta, xs):
        cond=next(x for x in xs if isinstance(x,A.Node))
        body=next((x for x in xs if isinstance(x,tuple) and all(isinstance(n,A.Node) and not isinstance(n,A.Parameter) for n in x)),())
        return A.While(_rule_loc(meta,self.filename),cond,body)
    @v_args(meta=True)
    def for_stmt(self, meta, xs):
        name=next(x for x in xs if isinstance(x,Token) and x.type=="NAME")
        expr=next(x for x in xs if isinstance(x,A.Node) and not isinstance(x,A.Parameter))
        body=next((x for x in xs if isinstance(x,tuple) and all(isinstance(n,A.Node) and not isinstance(n,A.Parameter) for n in x)),())
        return A.For(_rule_loc(meta,self.filename),str(name),expr,body)
    @v_args(meta=True)
    def repeat_stmt(self, meta, xs):
        expr=next(x for x in xs if isinstance(x,A.Node) and not isinstance(x,A.Parameter))
        body=next((x for x in xs if isinstance(x,tuple) and all(isinstance(n,A.Node) and not isinstance(n,A.Parameter) for n in x)),())
        return A.Repeat(_rule_loc(meta,self.filename),expr,body)
    @v_args(meta=True)
    def counted_loop(self,meta,xs):
        token=next(x for x in xs if isinstance(x,Token) and x.type=="NUMBER")
        if not str(token).isdigit(): raise ParseError("The `N times` loop count must be a non-negative integer",location=_loc(token,self.filename))
        count=int(str(token))
        if count.bit_length()>4096: raise ParseError("Counted-loop count exceeds numeric limit",location=_loc(token,self.filename))
        body=next((x for x in xs if isinstance(x,tuple) and all(isinstance(n,A.Node) and not isinstance(n,A.Parameter) for n in x)),())
        loc=_rule_loc(meta,self.filename)
        return A.Repeat(loc,A.Literal(_loc(token,self.filename),count),body)
    @v_args(meta=True)
    def function_def(self, meta, xs):
        name=next(x for x in xs if isinstance(x,Token) and x.type=="NAME")
        params=next((x for x in xs if isinstance(x,tuple) and all(isinstance(p,A.Parameter) for p in x)),())
        body=next((x for x in xs if isinstance(x,tuple) and all(isinstance(n,A.Node) and not isinstance(n,A.Parameter) for n in x)),())
        annotation=next((x for x in xs if isinstance(x,str) and not isinstance(x,Token)),None)
        return A.FunctionDef(_rule_loc(meta,self.filename),str(name),tuple(params),body,annotation)
    def parameters(self,xs): return tuple(xs)
    def lambda_parameters(self,xs): return tuple(xs)
    def lambda_parameter(self,xs):
        name=next(x for x in xs if isinstance(x,Token) and x.type=="NAME")
        default=next((x for x in xs if isinstance(x,A.Node)),None)
        return A.Parameter(_loc(name,self.filename),str(name),default,"normal",None)
    def lambda_expr(self,xs):
        params=next((x for x in xs if isinstance(x,tuple) and all(isinstance(p,A.Parameter) for p in x)),())
        body=next(x for x in xs if isinstance(x,A.Node) and not isinstance(x,A.Parameter))
        return A.Lambda(_node_loc(body,self.filename),tuple(params),body)
    def normal_parameter(self,xs):
        name=next(x for x in xs if isinstance(x,Token) and x.type=="NAME")
        default=next((x for x in xs if isinstance(x,A.Node)),None)
        annotation=next((str(x) for x in xs if isinstance(x,str) and not isinstance(x,Token)),None)
        return A.Parameter(_loc(name,self.filename),str(name),default,"normal",annotation)
    def args_parameter(self,xs): return A.Parameter(_loc(xs[0],self.filename),str(xs[0]),None,"varargs")
    def kwargs_parameter(self,xs): return A.Parameter(_loc(xs[0],self.filename),str(xs[0]),None,"kwargs")
    def type_expr(self,xs): return str(xs[0])
    @v_args(meta=True)
    def return_stmt(self,meta,xs): return A.Return(_rule_loc(meta,self.filename),xs[0] if xs else None)
    @v_args(meta=True)
    def stop_stmt(self,meta,xs): return A.Stop(_rule_loc(meta,self.filename))
    @v_args(meta=True)
    def skip_stmt(self,meta,xs): return A.Skip(_rule_loc(meta,self.filename))
    def dotted_name(self,xs): return ".".join(map(str,xs))
    @v_args(meta=True)
    def import_stmt(self,meta,xs):
        module=next(x for x in xs if isinstance(x,str))
        alias=next((str(x) for x in xs if isinstance(x,Token) and x.type=="NAME" and str(x)!=module.split(".")[-1]),None)
        return A.Import(_rule_loc(meta,self.filename),module,alias)
    def import_names(self,xs): return tuple(str(x) for x in xs)
    @v_args(meta=True)
    def from_import_stmt(self,meta,xs): return A.FromImport(_rule_loc(meta,self.filename),xs[0],xs[1])
    def exception_types(self,xs): return tuple(str(x) for x in xs)
    @v_args(meta=True)
    def except_clause(self,meta,xs):
        types=next((x for x in xs if isinstance(x,tuple) and all(isinstance(n,str) for n in x)),None)
        name=next((str(x) for x in xs if isinstance(x,Token) and x.type=="NAME"),None)
        body=next((x for x in xs if isinstance(x,tuple) and all(isinstance(n,A.Node) and not isinstance(n,A.Parameter) for n in x)),())
        return A.ExceptHandler(_rule_loc(meta,self.filename),types,name,body)
    def try_else_clause(self,xs):
        body=next((x for x in xs if isinstance(x,tuple) and all(isinstance(n,A.Node) and not isinstance(n,A.Parameter) for n in x)),())
        return ("try_else",body)
    def finally_clause(self,xs):
        body=next((x for x in xs if isinstance(x,tuple) and all(isinstance(n,A.Node) and not isinstance(n,A.Parameter) for n in x)),())
        return ("finally",body)
    @v_args(meta=True)
    def try_stmt(self,meta,xs):
        blocks=[x for x in xs if isinstance(x,tuple) and all(isinstance(n,A.Node) and not isinstance(n,A.Parameter) for n in x)]
        body=blocks[0] if blocks else ()
        handlers=tuple(x for x in xs if isinstance(x,A.ExceptHandler))
        else_body=next((x[1] for x in xs if isinstance(x,tuple) and x and x[0]=="try_else"),())
        finally_body=next((x[1] for x in xs if isinstance(x,tuple) and x and x[0]=="finally"),())
        return A.Try(_rule_loc(meta,self.filename),body,handlers,else_body,finally_body)
    @v_args(meta=True)
    def raise_stmt(self,meta,xs): return A.Raise(_rule_loc(meta,self.filename),xs[0])
    @v_args(meta=True)
    def expr_stmt(self,meta,xs): return A.ExprStmt(_rule_loc(meta,self.filename),xs[0])
    def number(self,xs):
        s=str(xs[0])
        if len(s)>1024: raise ParseError("Numeric literal exceeds configured limit",location=_loc(xs[0],self.filename))
        try: val=complex(s) if "j" in s.lower() else float(s) if any(c in s.lower() for c in ".e") else int(s,0) if s.lower().startswith(("0x","0o","0b")) else int(s)
        except ValueError as exc: raise ParseError("Invalid numeric literal",location=_loc(xs[0],self.filename)) from exc
        return A.Literal(_loc(xs[0],self.filename),val)
    def string(self,xs): return A.Literal(_loc(xs[0],self.filename),_unquote(str(xs[0])))
    def fstring(self,xs): return A.Literal(_loc(xs[0],self.filename),("__fstring__",str(xs[0])[1:]))
    def true(self,xs): return A.Literal(_loc(xs[0],self.filename),True)
    def false(self,xs): return A.Literal(_loc(xs[0],self.filename),False)
    def none(self,xs): return A.Literal(_loc(xs[0],self.filename),None)
    def variable(self,xs): return A.Variable(_loc(xs[0],self.filename),str(xs[0]))
    def grouped(self,xs): return xs[0]
    def list_literal(self,xs):
        if xs and isinstance(xs[0],A.Comprehension): return xs[0]
        return A.ListLiteral(SourceLocation(self.filename),tuple(xs[0] if xs else ()))
    def list_comprehension(self,xs):
        nodes=[x for x in xs if isinstance(x,A.Node)]; name=next(x for x in xs if isinstance(x,Token) and x.type=="NAME")
        return A.Comprehension(_node_loc(nodes[0],self.filename),"list",nodes[0],None,str(name),nodes[1],nodes[2] if len(nodes)>2 else None)
    def set_comprehension(self,xs):
        nodes=[x for x in xs if isinstance(x,A.Node)]; name=next(x for x in xs if isinstance(x,Token) and x.type=="NAME")
        return A.Comprehension(_node_loc(nodes[0],self.filename),"set",nodes[0],None,str(name),nodes[1],nodes[2] if len(nodes)>2 else None)
    def dict_comprehension(self,xs):
        nodes=[x for x in xs if isinstance(x,A.Node)]; name=next(x for x in xs if isinstance(x,Token) and x.type=="NAME")
        return A.Comprehension(_node_loc(nodes[0],self.filename),"dict",nodes[1],nodes[0],str(name),nodes[2],nodes[3] if len(nodes)>3 else None)
    def empty_tuple(self,xs): return A.TupleLiteral(SourceLocation(self.filename),())
    def tuple_literal(self,xs): return A.TupleLiteral(SourceLocation(self.filename),tuple(x for x in xs if isinstance(x, (A.Node, tuple)) for x in (x if isinstance(x,tuple) else (x,))))
    def dict_item(self,xs): return ("dict",xs[0],xs[1])
    def set_item(self,xs): return ("set",xs[0])
    def dict_or_set_items(self,xs): return tuple(xs)
    def comprehension_clause(self,xs):
        name=next(x for x in xs if isinstance(x,Token) and x.type=="NAME")
        nodes=[x for x in xs if isinstance(x,A.Node)]
        return ("comprehension",str(name),nodes[0],nodes[1] if len(nodes)>1 else None)
    def dict_or_set(self,xs):
        if not xs: return A.DictLiteral(SourceLocation(self.filename),())
        items=xs[0]
        if len(xs)>1 and isinstance(xs[1],tuple) and xs[1] and xs[1][0]=="comprehension":
            if len(items)!=1: raise ParseError("A comprehension must contain exactly one entry",location=SourceLocation(self.filename))
            _,name,iterable,condition=xs[1]
            first=items[0]
            if first[0]=="dict":
                return A.Comprehension(_node_loc(first[1],self.filename),"dict",first[2],first[1],name,iterable,condition)
            return A.Comprehension(_node_loc(first[1],self.filename),"set",first[1],None,name,iterable,condition)
        if items and all(x[0]=="dict" for x in items): return A.DictLiteral(SourceLocation(self.filename),tuple((x[1],x[2]) for x in items))
        if any(x[0]=="dict" for x in items): raise ParseError("Cannot mix set and dictionary entries",location=SourceLocation(self.filename))
        return A.SetLiteral(SourceLocation(self.filename),tuple(x[1] for x in items))
    def unary(self,xs): return A.Unary(_node_loc(xs[-1],self.filename),str(xs[0]),xs[-1])
    def fold_binary(self,xs): return _fold(xs,self.filename)
    def comparison(self,xs):
        if len(xs)==1: return xs[0]
        return A.Compare(_node_loc(xs[0],self.filename),tuple(xs[::2]),tuple(str(x) for x in xs[1::2]))
    def power_expr(self,xs): return _fold(xs,self.filename)
    def conditional(self,xs): return A.Conditional(_node_loc(xs[0],self.filename),xs[0],xs[1],xs[2]) if len(xs)==3 else xs[0]
    def positional_argument(self,xs): return A.CallArg(_node_loc(xs[0],self.filename),xs[0])
    def keyword_argument(self,xs): return A.CallArg(_loc(xs[0],self.filename),xs[1],str(xs[0]),"keyword")
    def star_argument(self,xs): return A.CallArg(_node_loc(xs[0],self.filename),xs[0],None,"star")
    def kwstar_argument(self,xs): return A.CallArg(_node_loc(xs[0],self.filename),xs[0],None,"kwstar")
    def arguments(self,xs): return tuple(xs)
    def call_part(self,xs): return ("call",xs[0] if xs else ())
    def attr_part(self,xs): return ("attr",str(xs[0]))
    def index_part(self,xs): return ("index",xs[0])
    def postfix_expr(self,xs):
        node=xs[0]
        for part in xs[1:]:
            if part[0]=="call": node=A.Call(_node_loc(node,self.filename),node,tuple(part[1]))
            elif part[0]=="attr": node=A.Attribute(_node_loc(node,self.filename),node,part[1])
            elif part[0]=="index": node=A.Index(_node_loc(node,self.filename),node,part[1])
        return node

def _extract_block(items):
    return next((x for x in items if isinstance(x,tuple) and all(isinstance(n,A.Node) and not isinstance(n,A.Parameter) for n in x)),())
def _node_loc(node, filename): return getattr(node,"loc",SourceLocation(filename))
def _fold(items, filename):
    if not items: raise AstError("Empty expression while building AST")
    node=items[0]
    for i in range(1,len(items),2): node=A.Binary(_node_loc(node,filename),node,str(items[i]),items[i+1])
    return node

def parse(source: str, filename: str="<memory>") -> A.Program:
    if not isinstance(source,str): raise ParseError("Source must be text",location=SourceLocation(filename))
    try: source_size=len(source.encode("utf-8",errors="strict"))
    except UnicodeEncodeError as exc: raise ParseError("Source contains invalid Unicode surrogate data",location=SourceLocation(filename)) from exc
    if source_size>1_000_000: raise ParseError("Source exceeds parser limit",location=SourceLocation(filename))
    if "\x00" in source: raise ParseError("Source contains a NUL character",location=SourceLocation(filename))
    source=source.replace("\r\n","\n").replace("\r","\n")
    # Tabs are rejected in indentation to keep locations and nesting deterministic.
    for line_no,line in enumerate(source.splitlines(),1):
        prefix=line[:len(line)-len(line.lstrip(" \t"))]
        if "\t" in prefix: raise ParseError("Tabs are not allowed in indentation",location=SourceLocation(filename,line_no,1),suggestion="Use four spaces per indentation level.")
    try:
        tree=_PARSER.parse(source)
        result=_BuildAST(filename).transform(tree)
    except RecursionError as exc: raise ParseError("Expression nesting is too deep",location=SourceLocation(filename),suggestion="Simplify deeply nested expressions.") from exc
    except UnexpectedInput as exc:
        expected=", ".join(sorted(getattr(exc,"expected",()) or ()))
        raise ParseError("Invalid AssayFlux syntax",location=SourceLocation(filename,exc.line or 1,exc.column or 1),details=f"Unexpected input. Expected: {expected or 'a valid statement or expression'}",suggestion="Check indentation, colons, matching 'end' keywords, quotes, and operators.") from exc
    except VisitError as exc:
        orig=exc.orig_exc
        if isinstance(orig,(ParseError,AstError)): raise orig
        raise AstError("Could not construct a valid syntax tree",location=SourceLocation(filename),details=type(orig).__name__) from orig
    if not isinstance(result,A.Program): raise AstError("Parser did not produce a Program node",location=SourceLocation(filename))
    return validate_ast(result)
