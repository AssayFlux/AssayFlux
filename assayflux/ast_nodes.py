"""
AssayFlux Scientific Systems
Abstract Syntax Tree (AST) Nodes

The AST is the shared structural contract between the
AssayFlux lexer, parser, interpreter, and future compiler.

Design principles:
    - Preserve existing public node names.
    - Preserve existing field names used by the parser.
    - Store source positions on every node.
    - Represent syntax structurally rather than as source text.
    - Use lists with independent default values.
    - Keep parsing separate from execution.
    - Support the canonical AssayFlux core grammar.

Canonical syntax includes:
    show expression
    constant NAME = expression
    app "Application Name"

    if condition:
        statements
    otherwise condition:
        statements
    else:
        statements
    end

    f.function_name(parameters):
        statements
    end

    repeat expression:
        statements
    end

    repeat count expression:
        statements
    end

    repeat while condition:
        statements
    end

    repeat forever:
        statements
    end

    stop
    skip
    pass
    return expression

Version: 0.4.0
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, List, Optional


AST_VERSION = "0.4.0"


# ============================================================
# Base Nodes
# ============================================================

@dataclass
class ASTNode:
    """
    Base class for every node in the abstract syntax tree.

    Attributes:
        line:
            One-based source line number.

        column:
            One-based source column number.

    All concrete nodes inherit source-position information.
    """

    line: int = 0
    column: int = 0


@dataclass
class Expression(ASTNode):
    """
    Base class for expressions.

    Expressions represent values that can be evaluated.

    Examples:
        10
        "AssayFlux"
        true
        temperature + 5
        math.sqrt(25)
    """


@dataclass
class Statement(ASTNode):
    """
    Base class for statements.

    Statements represent declarations, assignments,
    output operations, control flow, and other actions.
    """


# ============================================================
# Program
# ============================================================

@dataclass
class Program(ASTNode):
    """
    A complete parsed AssayFlux program.

    Attributes:
        statements:
            Top-level statements in source order.
    """

    statements: List[Statement] = field(default_factory=list)


# ============================================================
# Literal Values
# ============================================================

@dataclass
class NumberLiteral(Expression):
    """
    A numeric literal.

    The lexer and parser currently support numeric values
    accepted by the parser's numeric-literal implementation.

    Examples:
        10
        3.14
        0xFF
        2j
    """

    value: Any = 0


@dataclass
class StringLiteral(Expression):
    """
    A string literal.

    The value contains the decoded string value supplied
    by the lexer.

    Examples:
        "AssayFlux"
        'Scientific Systems'
    """

    value: str = ""


@dataclass
class BooleanLiteral(Expression):
    """
    A Boolean literal.

    Canonical AssayFlux spellings:
        true
        false
    """

    value: bool = False


@dataclass
class NoneLiteral(Expression):
    """
    Represents an absent value.

    This node is retained for compatibility and future
    grammar support. Its presence does not mean that the
    current parser accepts a None literal.
    """

    value: None = None


# ============================================================
# Identifiers and Declarations
# ============================================================

@dataclass
class Identifier(Expression):
    """
    A variable or identifier reference.

    Example:
        temperature
    """

    name: str = ""


@dataclass
class Assignment(Statement):
    """
    Assignment to a variable.

    Example:
        temperature = 25

    The current parser supports simple identifier assignment.
    Attribute assignment and indexed assignment require
    explicit parser and interpreter support.
    """

    name: str = ""
    value: Optional[Expression] = None


@dataclass
class ConstantDeclaration(Statement):
    """
    Declaration of a constant.

    Example:
        constant MAXIMUM = 100

    The AST records the declaration. Constant immutability,
    reassignment checks, and protection against indirect
    mutation must be enforced by the interpreter or runtime.
    """

    name: str = ""
    value: Optional[Expression] = None


@dataclass
class AppDeclaration(Statement):
    """
    Application metadata declaration.

    Example:
        app "AssayFlux Scientific Systems"
    """

    name: str = ""


@dataclass
class ExpressionStatement(Statement):
    """
    An expression evaluated as a statement.

    Example:
        calculate_result()
    """

    expression: Optional[Expression] = None


@dataclass
class PassStatement(Statement):
    """
    An explicit no-operation statement.

    Example:
        pass

    The parser must construct this node when it accepts
    the pass keyword. The interpreter should implement it
    as a no-operation statement.
    """


# ============================================================
# Operators and Expressions
# ============================================================

@dataclass
class BinaryOperation(Expression):
    """
    A binary operation.

    Examples:
        a + b
        temperature >= 25
        enabled and ready

    Attributes:
        left:
            Left operand.

        operator:
            Operator spelling.

        right:
            Right operand.
    """

    left: Optional[Expression] = None
    operator: str = ""
    right: Optional[Expression] = None


@dataclass
class UnaryOperation(Expression):
    """
    A unary operation.

    Examples:
        -temperature
        +value
        not enabled
    """

    operator: str = ""
    operand: Optional[Expression] = None


@dataclass
class FunctionCall(Expression):
    """
    A function call.

    The current parser stores the callable name as a string.

    Examples:
        calculate(10, 20)
        math.sqrt(25)

    Attributes:
        name:
            Function name or dotted member path.

        arguments:
            Arguments in source order.
    """

    name: str = ""
    arguments: List[Expression] = field(default_factory=list)


@dataclass
class MemberAccess(Expression):
    """
    Access to a member of an object or module.

    Example:
        math.sqrt

    Attributes:
        object:
            Expression providing the object.

        member:
            Member name.
    """

    object: Optional[Expression] = None
    member: str = ""


# ============================================================
# Output
# ============================================================

@dataclass
class ShowStatement(Statement):
    """
    Display the result of an expression.

    Example:
        show "Hello, AssayFlux"
    """

    value: Optional[Expression] = None


# ============================================================
# Conditional Statements
# ============================================================

@dataclass
class ConditionalBranch(ASTNode):
    """
    One conditional branch belonging to an IfStatement.

    This represents an otherwise-condition branch.

    Attributes:
        condition:
            Expression evaluated to determine whether
            this branch should execute.

        statements:
            Statements inside the branch.
    """

    condition: Optional[Expression] = None
    statements: List[Statement] = field(default_factory=list)


@dataclass
class IfStatement(Statement):
    """
    An if/otherwise/else conditional statement.

    Canonical example:

        if temperature > 30:
            show "Hot"
        otherwise temperature > 20:
            show "Warm"
        else:
            show "Cool"
        end

    Attributes:
        condition:
            Initial if condition.

        body:
            Statements belonging to the initial if branch.

        otherwise_branches:
            Ordered list of ConditionalBranch nodes.

        else_body:
            Statements belonging to the optional else branch.
            None means that no else branch was provided.
    """

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
    An AssayFlux repeat loop.

    Supported canonical modes:

        condition:
            Repeat while condition evaluates to true.

        count:
            Repeat a specified number of times.

        forever:
            Continue until stopped or interrupted.

    Attributes:
        condition:
            Condition expression for condition mode.

        body:
            Statements executed by the loop.

        mode:
            Loop mode: "condition", "count", or "forever".

        count:
            Expression providing the repetition count
            when mode is "count".

    Examples:

        repeat 5:
            show "Repeated"
        end

        repeat count 5:
            show "Repeated"
        end

        repeat while ready:
            show "Waiting"
        end

        repeat forever:
            stop
        end
    """

    condition: Optional[Expression] = None

    body: List[Statement] = field(default_factory=list)

    mode: str = "condition"

    count: Optional[Expression] = None


@dataclass
class StopStatement(Statement):
    """
    Exit the nearest enclosing repeat loop.

    Canonical syntax:
        stop
    """


@dataclass
class SkipStatement(Statement):
    """
    Skip the remainder of the current repeat iteration.

    Canonical syntax:
        skip
    """


# ============================================================
# Functions
# ============================================================

@dataclass
class FunctionDefinition(Statement):
    """
    A function declaration.

    Canonical syntax:

        f.add(a, b):
            return a + b
        end

    Attributes:
        name:
            Declared function name without the f. prefix.

        parameters:
            Parameter names in declaration order.

        body:
            Statements belonging to the function.
    """

    name: str = ""

    parameters: List[str] = field(default_factory=list)

    body: List[Statement] = field(default_factory=list)


@dataclass
class ReturnStatement(Statement):
    """
    Return from a function.

    Attributes:
        value:
            Expression to return.

            None represents a return without an explicit value.

    Examples:
        return
        return result
    """

    value: Optional[Expression] = None


# ============================================================
# Imports
# ============================================================

@dataclass
class ImportStatement(Statement):
    """
    Import a module.

    Example:
        import math

    Attributes:
        module_name:
            Module path, potentially containing dots.

        alias:
            Optional import alias.

    The current parser and interpreter determine the exact
    supported import syntax and runtime behavior.
    """

    module_name: str = ""

    alias: Optional[str] = None


# ============================================================
# Error Representation
# ============================================================

@dataclass
class ErrorNode(ASTNode):
    """
    Represents a syntax error when a future parser mode
    supports error recovery.

    Attributes:
        message:
            Human-readable description of the error.

    The current parser may raise ParserError instead of
    inserting ErrorNode objects into the AST.
    """

    message: str = ""


# ============================================================
# Public Exports
# ============================================================

__all__ = [
    "AST_VERSION",
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
    "PassStatement",
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