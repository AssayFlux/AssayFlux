"""
AssayFlux Semantic Validator
============================

Validates the structure of the AssayFlux AST.

The validator uses the actual node classes defined in
assayflux.ast_nodes.

Responsibilities:
    - Traverse the AssayFlux AST.
    - Validate the structure of supported nodes.
    - Detect duplicate function parameters.
    - Validate return statements inside functions.
    - Validate stop and skip statements inside loops.
    - Preserve source locations in semantic errors.

Important:
    This validator does not replace the parser or interpreter.
    It does not execute programs or evaluate expressions.

    It intentionally does not reject unresolved identifiers,
    because Python imports, built-ins, functions, and runtime
    name resolution must be considered before such a rule
    can be enforced safely.
"""

from __future__ import annotations

from dataclasses import fields, is_dataclass
from typing import Any, Optional

from assayflux.ast_nodes import (
    ASTNode,
    AppDeclaration,
    Assignment,
    BinaryOperation,
    BooleanLiteral,
    ConditionalBranch,
    ConstantDeclaration,
    ErrorNode,
    ExpressionStatement,
    FunctionCall,
    FunctionDefinition,
    Identifier,
    IfStatement,
    ImportStatement,
    MemberAccess,
    NoneLiteral,
    NumberLiteral,
    PassStatement,
    Program,
    RepeatStatement,
    ReturnStatement,
    ShowStatement,
    SkipStatement,
    StopStatement,
    StringLiteral,
    UnaryOperation,
)


class SemanticError(Exception):
    """An AssayFlux semantic validation error."""

    def __init__(
        self,
        message: str,
        line: int = 0,
        column: int = 0,
        filename: str = "<string>",
    ) -> None:
        self.message = message
        self.line = line
        self.column = column
        self.filename = filename

        if line and column:
            rendered = (
                f"[{filename}:{line}:{column}] "
                f"AssayFlux Semantic Error: {message}"
            )
        else:
            rendered = f"AssayFlux Semantic Error: {message}"

        super().__init__(rendered)


class SymbolTable:
    """
    Hierarchical symbol table.

    The table can record symbols and look them up through
    parent scopes.

    It does not impose declaration-before-use rules by itself.
    """

    def __init__(
        self,
        parent: Optional["SymbolTable"] = None,
    ) -> None:
        self.symbols: set[str] = set()
        self.parent = parent

    def define(self, name: str) -> None:
        """Register a name in the current scope."""
        if not isinstance(name, str) or not name:
            raise ValueError("A symbol name must be a non-empty string.")

        self.symbols.add(name)

    def lookup(self, name: str) -> bool:
        """Return whether a name exists in this scope or a parent."""
        if name in self.symbols:
            return True

        if self.parent is not None:
            return self.parent.lookup(name)

        return False

    def contains_local(self, name: str) -> bool:
        """Check only the current scope."""
        return name in self.symbols


class SemanticValidator:
    """
    Validate an AssayFlux AST.

    Example:

        validator = SemanticValidator()
        validator.validate(program)

    A successful validation returns True.

    Invalid structures raise SemanticError.
    """

    def __init__(
        self,
        filename: str = "<string>",
    ) -> None:
        self.filename = filename
        self.current_scope = SymbolTable()

        self.function_depth = 0
        self.loop_depth = 0

    def enter_scope(self) -> None:
        """Create a nested symbol scope."""
        self.current_scope = SymbolTable(
            parent=self.current_scope
        )

    def exit_scope(self) -> None:
        """Return to the parent symbol scope."""
        if self.current_scope.parent is not None:
            self.current_scope = self.current_scope.parent

    def _error(
        self,
        message: str,
        node: Optional[ASTNode] = None,
    ) -> None:
        """Raise an error with the node's source location."""
        raise SemanticError(
            message=message,
            line=getattr(node, "line", 0),
            column=getattr(node, "column", 0),
            filename=self.filename,
        )

    def validate(self, node: ASTNode) -> bool:
        """
        Validate an AST node or complete Program.

        Validation state is reset for every invocation.
        """
        if not isinstance(node, ASTNode):
            raise TypeError(
                "SemanticValidator.validate() expects an ASTNode."
            )

        self.current_scope = SymbolTable()
        self.function_depth = 0
        self.loop_depth = 0

        self.visit(node)
        return True

    def visit(self, node: Any) -> Any:
        """Dispatch an AST node to its matching visitor."""
        if node is None:
            return None

        if isinstance(node, list):
            for item in node:
                self.visit(item)
            return None

        if not isinstance(node, ASTNode):
            self._error(
                f"Unexpected non-AST value: {type(node).__name__}."
            )

        visitor = getattr(
            self,
            f"visit_{type(node).__name__}",
            None,
        )

        if visitor is None:
            self._error(
                f"Unsupported AST node: {type(node).__name__}.",
                node,
            )

        return visitor(node)

    def _visit_fields(self, node: ASTNode) -> None:
        """
        Visit AST-valued dataclass fields.

        This helper is used only for nodes whose fields do not
        require special scope or control-flow handling.
        """
        if not is_dataclass(node):
            self._error(
                f"AST node {type(node).__name__} is not a dataclass.",
                node,
            )

        for item in fields(node):
            if item.name in {"line", "column"}:
                continue

            value = getattr(node, item.name)

            if isinstance(value, ASTNode):
                self.visit(value)

            elif isinstance(value, list):
                for child in value:
                    if isinstance(child, ASTNode):
                        self.visit(child)

    # --------------------------------------------------------
    # Program
    # --------------------------------------------------------

    def visit_Program(self, node: Program) -> None:
        for statement in node.statements:
            self.visit(statement)

    # --------------------------------------------------------
    # Literals and identifiers
    # --------------------------------------------------------

    def visit_NumberLiteral(self, node: NumberLiteral) -> None:
        return None

    def visit_StringLiteral(self, node: StringLiteral) -> None:
        return None

    def visit_BooleanLiteral(self, node: BooleanLiteral) -> None:
        return None

    def visit_NoneLiteral(self, node: NoneLiteral) -> None:
        return None

    def visit_Identifier(self, node: Identifier) -> None:
        # Name resolution remains the responsibility of the
        # runtime until its complete rules are formally defined.
        return None

    # --------------------------------------------------------
    # Declarations and assignments
    # --------------------------------------------------------

    def visit_AppDeclaration(
        self,
        node: AppDeclaration,
    ) -> None:
        return None

    def visit_Assignment(self, node: Assignment) -> None:
        self.visit(node.value)

    def visit_ConstantDeclaration(
        self,
        node: ConstantDeclaration,
    ) -> None:
        self.visit(node.value)

    def visit_ImportStatement(
        self,
        node: ImportStatement,
    ) -> None:
        if not node.module_name:
            self._error(
                "An import statement requires a module name.",
                node,
            )

    # --------------------------------------------------------
    # Expressions
    # --------------------------------------------------------

    def visit_BinaryOperation(
        self,
        node: BinaryOperation,
    ) -> None:
        if node.left is None or node.right is None:
            self._error(
                "A binary operation requires two operands.",
                node,
            )

        self.visit(node.left)
        self.visit(node.right)

    def visit_UnaryOperation(
        self,
        node: UnaryOperation,
    ) -> None:
        if node.operand is None:
            self._error(
                "A unary operation requires an operand.",
                node,
            )

        self.visit(node.operand)

    def visit_FunctionCall(self, node: FunctionCall) -> None:
        if not node.name:
            self._error(
                "A function call requires a function name.",
                node,
            )

        for argument in node.arguments:
            self.visit(argument)

    def visit_MemberAccess(self, node: MemberAccess) -> None:
        if node.object is None:
            self._error(
                "Member access requires an object expression.",
                node,
            )

        if not node.member:
            self._error(
                "Member access requires a member name.",
                node,
            )

        self.visit(node.object)

    # --------------------------------------------------------
    # Statements
    # --------------------------------------------------------

    def visit_ExpressionStatement(
        self,
        node: ExpressionStatement,
    ) -> None:
        self.visit(node.expression)

    def visit_ShowStatement(
        self,
        node: ShowStatement,
    ) -> None:
        self.visit(node.value)

    def visit_PassStatement(
        self,
        node: PassStatement,
    ) -> None:
        return None

    def visit_ErrorNode(self, node: ErrorNode) -> None:
        self._error(
            f"Cannot validate an error node: {node.message}",
            node,
        )

    # --------------------------------------------------------
    # Conditional statements
    # --------------------------------------------------------

    def visit_ConditionalBranch(
        self,
        node: ConditionalBranch,
    ) -> None:
        if node.condition is None:
            self._error(
                "An otherwise branch requires a condition.",
                node,
            )

        self.visit(node.condition)

        for statement in node.statements:
            self.visit(statement)

    def visit_IfStatement(self, node: IfStatement) -> None:
        if node.condition is None:
            self._error(
                "An if statement requires a condition.",
                node,
            )

        self.visit(node.condition)

        for statement in node.body:
            self.visit(statement)

        for branch in node.otherwise_branches:
            self.visit(branch)

        if node.else_body is not None:
            for statement in node.else_body:
                self.visit(statement)

    # --------------------------------------------------------
    # Loops
    # --------------------------------------------------------

    def visit_RepeatStatement(
        self,
        node: RepeatStatement,
    ) -> None:
        allowed_modes = {
            "condition",
            "count",
            "forever",
        }

        if node.mode not in allowed_modes:
            self._error(
                f"Unsupported repeat mode {node.mode!r}.",
                node,
            )

        if node.mode == "count":
            if node.count is None:
                self._error(
                    "A count-based repeat loop requires a count.",
                    node,
                )

            self.visit(node.count)

        elif node.mode == "condition":
            if node.condition is None:
                self._error(
                    "A condition-based repeat loop requires a condition.",
                    node,
                )

            self.visit(node.condition)

        self.loop_depth += 1

        try:
            for statement in node.body:
                self.visit(statement)
        finally:
            self.loop_depth -= 1

    def visit_StopStatement(
        self,
        node: StopStatement,
    ) -> None:
        if self.loop_depth == 0:
            self._error(
                "'stop' outside a repeat loop is not allowed.",
                node,
            )

    def visit_SkipStatement(
        self,
        node: SkipStatement,
    ) -> None:
        if self.loop_depth == 0:
            self._error(
                "'skip' outside a repeat loop is not allowed.",
                node,
            )

    # --------------------------------------------------------
    # Functions
    # --------------------------------------------------------

    def visit_FunctionDefinition(
        self,
        node: FunctionDefinition,
    ) -> None:
        if not node.name:
            self._error(
                "A function definition requires a name.",
                node,
            )

        if len(node.parameters) != len(set(node.parameters)):
            self._error(
                f"Function {node.name!r} has duplicate parameters.",
                node,
            )

        self.enter_scope()
        self.function_depth += 1

        try:
            for parameter in node.parameters:
                if not isinstance(parameter, str) or not parameter:
                    self._error(
                        "Function parameters must have non-empty names.",
                        node,
                    )

                self.current_scope.define(parameter)

            for statement in node.body:
                self.visit(statement)

        finally:
            self.function_depth -= 1
            self.exit_scope()

    def visit_ReturnStatement(
        self,
        node: ReturnStatement,
    ) -> None:
        if self.function_depth == 0:
            self._error(
                "'return' outside a function is not allowed.",
                node,
            )

        self.visit(node.value)