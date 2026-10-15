"""
AssayFlux Scientific Systems
Abstract Syntax Tree (AST) Nodes

AST nodes represent the structure of AssayFlux programs.

Version: 0.2.0
"""

from dataclasses import dataclass, field
from typing import Any, List, Optional, Tuple


# ============================================================
# Base Node
# ============================================================

@dataclass
class ASTNode:
    """Base class for all AssayFlux AST nodes."""

    line: int = 0
    column: int = 0


@dataclass
class Expression(ASTNode):
    """Base class for expression nodes."""


@dataclass
class Statement(ASTNode):
    """Base class for statement nodes."""


# ============================================================
# Program
# ============================================================

@dataclass
class Program(ASTNode):
    """Represents a complete AssayFlux program."""

    statements: List[Statement] = field(default_factory=list)


# ============================================================
# Literal Values
# ============================================================

@dataclass
class NumberLiteral(Expression):
    """Represents an integer or floating-point literal."""

    value: Any = 0


@dataclass
class StringLiteral(Expression):
    """Represents a string literal."""

    value: str = ""


@dataclass
class BooleanLiteral(Expression):
    """Represents true or false."""

    value: bool = False


@dataclass
class NoneLiteral(Expression):
    """Represents an absent value, if supported by the language."""

    value: None = None


# ============================================================
# Variables
# ============================================================

@dataclass
class Identifier(Expression):
    """Represents a variable or identifier name."""

    name: str = ""


@dataclass
class Assignment(Statement):
    """Represents a variable assignment."""

    name: str = ""
    value: Optional[Expression] = None


@dataclass
class AppDeclaration(Statement):
    """Declares application metadata using app "Name"."""

    name: str = ""


@dataclass
class ExpressionStatement(Statement):
    """Evaluates an expression for its side effects."""

    expression: Optional[Expression] = None


@dataclass
class ConstantDeclaration(Statement):
    """Represents a constant declaration."""

    name: str = ""
    value: Optional[Expression] = None


# ============================================================
# Operators and Expressions
# ============================================================

@dataclass
class BinaryOperation(Expression):
    """Represents a binary operation such as a + b."""

    left: Optional[Expression] = None
    operator: str = ""
    right: Optional[Expression] = None


@dataclass
class UnaryOperation(Expression):
    """Represents a unary operation such as -value."""

    operator: str = ""
    operand: Optional[Expression] = None


@dataclass
class FunctionCall(Expression):
    """Represents a function call."""

    name: str = ""
    arguments: List[Expression] = field(default_factory=list)


@dataclass
class MemberAccess(Expression):
    """Represents member access such as module.function."""

    object: Optional[Expression] = None
    member: str = ""


# ============================================================
# Output
# ============================================================

@dataclass
class ShowStatement(Statement):
    """Represents the AssayFlux show statement."""

    value: Optional[Expression] = None


# ============================================================
# Conditional Statements
# ============================================================

@dataclass
class ConditionalBranch(ASTNode):
    """Represents one condition and its statements."""

    condition: Optional[Expression] = None
    statements: List[Statement] = field(default_factory=list)


@dataclass
class IfStatement(Statement):
    """Represents if, otherwise, and else branches."""

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
    """Represents a condition-controlled repeat loop."""

    condition: Optional[Expression] = None
    body: List[Statement] = field(default_factory=list)


@dataclass
class StopStatement(Statement):
    """Represents stop, which exits the nearest enclosing loop."""


@dataclass
class SkipStatement(Statement):
    """Represents skip, which advances the nearest enclosing loop."""


# ============================================================
# Functions
# ============================================================

@dataclass
class FunctionDefinition(Statement):
    """Represents a function definition such as f.add(a, b)."""

    name: str = ""
    parameters: List[str] = field(default_factory=list)
    body: List[Statement] = field(default_factory=list)


@dataclass
class ReturnStatement(Statement):
    """Represents a return statement."""

    value: Optional[Expression] = None


# ============================================================
# Imports
# ============================================================

@dataclass
class ImportStatement(Statement):
    """Represents a module import."""

    module_name: str = ""
    alias: Optional[str] = None


# ============================================================
# Error Representation
# ============================================================

@dataclass
class ErrorNode(ASTNode):
    """Represents an error recovered during parsing."""

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