"""
AssayFlux Scientific Systems
Abstract Syntax Tree (AST) Nodes

AST nodes represent the structure of AssayFlux programs.

Version: 0.3.0
"""

from dataclasses import dataclass, field
from typing import Any, List, Optional


# ============================================================
# Base Nodes
# ============================================================

@dataclass
class ASTNode:
    """Base class for all AssayFlux AST nodes."""

    line: int = 0
    column: int = 0


@dataclass
class Expression(ASTNode):
    """Base class for expressions."""


@dataclass
class Statement(ASTNode):
    """Base class for statements."""


# ============================================================
# Program
# ============================================================

@dataclass
class Program(ASTNode):
    """A complete AssayFlux program."""

    statements: List[Statement] = field(default_factory=list)


# ============================================================
# Literal Values
# ============================================================

@dataclass
class NumberLiteral(Expression):
    """An integer or floating-point literal."""

    value: Any = 0


@dataclass
class StringLiteral(Expression):
    """A string literal."""

    value: str = ""


@dataclass
class BooleanLiteral(Expression):
    """A Boolean literal."""

    value: bool = False


@dataclass
class NoneLiteral(Expression):
    """An absent value."""

    value: None = None


# ============================================================
# Variables and Declarations
# ============================================================

@dataclass
class Identifier(Expression):
    """A variable or identifier."""

    name: str = ""


@dataclass
class Assignment(Statement):
    """An assignment to a variable."""

    name: str = ""
    value: Optional[Expression] = None


@dataclass
class ConstantDeclaration(Statement):
    """A declaration of a constant value."""

    name: str = ""
    value: Optional[Expression] = None


@dataclass
class AppDeclaration(Statement):
    """Application metadata declared using app "Name"."""

    name: str = ""


@dataclass
class ExpressionStatement(Statement):
    """An expression evaluated for its side effects."""

    expression: Optional[Expression] = None


# ============================================================
# Operators and Expressions
# ============================================================

@dataclass
class BinaryOperation(Expression):
    """A binary operation, such as a + b."""

    left: Optional[Expression] = None
    operator: str = ""
    right: Optional[Expression] = None


@dataclass
class UnaryOperation(Expression):
    """A unary operation, such as -value."""

    operator: str = ""
    operand: Optional[Expression] = None


@dataclass
class FunctionCall(Expression):
    """A function call."""

    name: str = ""
    arguments: List[Expression] = field(default_factory=list)


@dataclass
class MemberAccess(Expression):
    """Member access, such as math.sqrt."""

    object: Optional[Expression] = None
    member: str = ""


# ============================================================
# Output
# ============================================================

@dataclass
class ShowStatement(Statement):
    """A statement that displays a value."""

    value: Optional[Expression] = None


# ============================================================
# Conditional Statements
# ============================================================

@dataclass
class ConditionalBranch(ASTNode):
    """A conditional branch and its statements."""

    condition: Optional[Expression] = None
    statements: List[Statement] = field(default_factory=list)


@dataclass
class IfStatement(Statement):
    """An if/otherwise/else statement."""

    condition: Optional[Expression] = None

    body: List[Statement] = field(default_factory=list)

    otherwise_branches: List[ConditionalBranch] = field(
        default_factory=list
    )

    else_body: Optional[List[Statement]] = None


# ============================================================
# Repetition and Loop Control
# ============================================================

@dataclass
class RepeatStatement(Statement):
    """
    Represents an AssayFlux repeat loop.

    Supported modes will include:

    condition:
        Repeat while the condition evaluates to true.

    count:
        Repeat a specified number of times.

    forever:
        Repeat until stopped or interrupted.

    The parser and interpreter will validate and implement
    the selected mode.
    """

    condition: Optional[Expression] = None

    body: List[Statement] = field(default_factory=list)

    mode: str = "condition"

    count: Optional[Expression] = None


@dataclass
class StopStatement(Statement):
    """Exit the nearest enclosing repeat loop."""


@dataclass
class SkipStatement(Statement):
    """Skip to the next iteration of the nearest repeat loop."""


# ============================================================
# Functions
# ============================================================

@dataclass
class FunctionDefinition(Statement):
    """A function declaration, such as f.add(a, b)."""

    name: str = ""

    parameters: List[str] = field(default_factory=list)

    body: List[Statement] = field(default_factory=list)


@dataclass
class ReturnStatement(Statement):
    """Return a value from a function."""

    value: Optional[Expression] = None


# ============================================================
# Imports
# ============================================================

@dataclass
class ImportStatement(Statement):
    """Import a Python module."""

    module_name: str = ""

    alias: Optional[str] = None


# ============================================================
# Error Representation
# ============================================================

@dataclass
class ErrorNode(ASTNode):
    """An error recovered during parsing."""

    message: str = ""


# ============================================================
# Public Exports
# ============================================================

__all__ = [
    "ASTNode",
    "Expression",
    "Statement",
    "Program",
    "NumberLiteral",
    "StringLiteral",
    "BooleanLiteral",
    "NoneLiteral",
    "Identifier",
    "Assignment",
    "ConstantDeclaration",
    "AppDeclaration",
    "ExpressionStatement",
    "BinaryOperation",
    "UnaryOperation",
    "FunctionCall",
    "MemberAccess",
    "ShowStatement",
    "ConditionalBranch",
    "IfStatement",
    "RepeatStatement",
    "StopStatement",
    "SkipStatement",
    "FunctionDefinition",
    "ReturnStatement",
    "ImportStatement",
    "ErrorNode",
]