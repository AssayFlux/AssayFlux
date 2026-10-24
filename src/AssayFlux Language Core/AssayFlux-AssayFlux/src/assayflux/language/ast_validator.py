"""Structural checkpoint for untrusted or transformed ASTs."""
from __future__ import annotations

from dataclasses import fields

from assayflux.diagnostics.model import AstError

from . import ast_nodes as A

_ALLOWED = {
    getattr(A, name)
    for name in dir(A)
    if isinstance(getattr(A, name), type)
    and issubclass(getattr(A, name), A.Node)
}
_MAX_DEPTH = 256
_MAX_NODES = 200_000


def validate_ast(root: A.Program) -> A.Program:
    if type(root) is not A.Program:
        raise AstError("AST root must be a Program node")

    seen = 0

    def visit(node, depth):
        nonlocal seen
        if type(node) not in _ALLOWED:
            raise AstError(
                f"Unsupported AST node type: {type(node).__name__}",
                location=getattr(node, "loc", None),
            )

        seen += 1
        if seen > _MAX_NODES:
            raise AstError("AST node count exceeds safety limit", location=node.loc)
        if depth > _MAX_DEPTH:
            raise AstError("AST nesting depth exceeds safety limit", location=node.loc)

        for field in fields(node):
            if field.name == "loc":
                continue
            value = getattr(node, field.name)
            if isinstance(value, A.Node):
                visit(value, depth + 1)
            elif isinstance(value, tuple):
                stack = list(value)
                while stack:
                    item = stack.pop()
                    if isinstance(item, A.Node):
                        visit(item, depth + 1)
                    elif isinstance(item, tuple):
                        stack.extend(item)

        if (
            not isinstance(node.loc.line, int)
            or node.loc.line < 1
            or not isinstance(node.loc.column, int)
            or node.loc.column < 1
        ):
            raise AstError("AST node has invalid source coordinates", location=node.loc)

    visit(root, 0)
    return root
