"""Immutable source-located AST for the implemented AssayFlux core."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from assayflux.diagnostics.model import SourceLocation


@dataclass(frozen=True, slots=True)
class Node: loc: SourceLocation
@dataclass(frozen=True, slots=True)
class Program(Node): statements: tuple[Node, ...]
@dataclass(frozen=True, slots=True)
class ProjectDecl(Node): name: str
@dataclass(frozen=True, slots=True)
class LetDecl(Node): name: str; value: Node
@dataclass(frozen=True, slots=True)
class ConstantDecl(Node): name: str; value: Node
@dataclass(frozen=True, slots=True)
class Assign(Node): name: str; value: Node
@dataclass(frozen=True, slots=True)
class AugAssign(Node): name: str; op: str; value: Node
@dataclass(frozen=True, slots=True)
class Show(Node): values: tuple[Node, ...]
@dataclass(frozen=True, slots=True)
class If(Node): branches: tuple[tuple[Node, tuple[Node, ...]], ...]; else_body: tuple[Node, ...]
@dataclass(frozen=True, slots=True)
class While(Node): condition: Node; body: tuple[Node, ...]
@dataclass(frozen=True, slots=True)
class For(Node): name: str; iterable: Node; body: tuple[Node, ...]
@dataclass(frozen=True, slots=True)
class Repeat(Node): count: Node; body: tuple[Node, ...]
@dataclass(frozen=True, slots=True)
class Parameter(Node): name: str; default: Node | None = None; kind: str = "normal"; annotation: str | None = None
@dataclass(frozen=True, slots=True)
class FunctionDef(Node): name: str; parameters: tuple[Parameter, ...]; body: tuple[Node, ...]; return_type: str | None = None
@dataclass(frozen=True, slots=True)
class Return(Node): value: Node | None
@dataclass(frozen=True, slots=True)
class Stop(Node): pass
@dataclass(frozen=True, slots=True)
class Skip(Node): pass
@dataclass(frozen=True, slots=True)
class Import(Node): module: str; alias: str | None = None
@dataclass(frozen=True, slots=True)
class FromImport(Node): module: str; names: tuple[str, ...]
@dataclass(frozen=True, slots=True)
class ExprStmt(Node): value: Node
@dataclass(frozen=True, slots=True)
class Literal(Node): value: Any
@dataclass(frozen=True, slots=True)
class Variable(Node): name: str
@dataclass(frozen=True, slots=True)
class Unary(Node): op: str; value: Node
@dataclass(frozen=True, slots=True)
class Binary(Node): left: Node; op: str; right: Node
@dataclass(frozen=True, slots=True)
class Conditional(Node): value: Node; condition: Node; otherwise: Node
@dataclass(frozen=True, slots=True)
class ListLiteral(Node): values: tuple[Node, ...]
@dataclass(frozen=True, slots=True)
class TupleLiteral(Node): values: tuple[Node, ...]
@dataclass(frozen=True, slots=True)
class SetLiteral(Node): values: tuple[Node, ...]
@dataclass(frozen=True, slots=True)
class DictLiteral(Node): values: tuple[tuple[Node, Node], ...]
@dataclass(frozen=True, slots=True)
class CallArg(Node): value: Node; name: str | None = None; kind: str = "positional"
@dataclass(frozen=True, slots=True)
class Call(Node): function: Node; arguments: tuple[CallArg, ...]
@dataclass(frozen=True, slots=True)
class Attribute(Node): value: Node; name: str
@dataclass(frozen=True, slots=True)
class Index(Node): value: Node; index: Node

@dataclass(frozen=True, slots=True)
class Compare(Node): operands: tuple[Node, ...]; operators: tuple[str, ...]

@dataclass(frozen=True, slots=True)
class ExceptHandler(Node): exception_types: tuple[str, ...] | None; name: str | None; body: tuple[Node, ...]
@dataclass(frozen=True, slots=True)
class Try(Node): body: tuple[Node, ...]; handlers: tuple[ExceptHandler, ...]; else_body: tuple[Node, ...]; finally_body: tuple[Node, ...]
@dataclass(frozen=True, slots=True)
class Raise(Node): value: Node

@dataclass(frozen=True, slots=True)
class Comprehension(Node): kind: str; element: Node; key: Node | None; name: str; iterable: Node; condition: Node | None = None

@dataclass(frozen=True, slots=True)
class Lambda(Node): parameters: tuple[Parameter, ...]; body: Node
