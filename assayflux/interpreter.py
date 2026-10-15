"""
AssayFlux Scientific Systems
Interpreter Implementation

Executes AssayFlux programs and integrates with Python libraries.

Version: 0.1.0
"""

import importlib
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from assayflux.interop import dispatch as dispatch_language

from assayflux.ast_nodes import (
    Assignment,
    BinaryOperation,
    BooleanLiteral,
    ConstantDeclaration,
    FunctionCall,
    FunctionDefinition,
    Identifier,
    IfStatement,
    ImportStatement,
    MemberAccess,
    NumberLiteral,
    Program,
    RepeatStatement,
    ReturnStatement,
    ShowStatement,
    SkipStatement,
    StopStatement,
    StringLiteral,
    UnaryOperation,
)
from assayflux.lexer import LexerError
from assayflux.parser import ParserError, parse


class AssayFluxRuntimeError(Exception):
    """Error raised during AssayFlux execution."""

    def __init__(
        self,
        message: str,
        line: int = 0,
        column: int = 0,
    ):
        self.message = message
        self.line = line
        self.column = column

        if line:
            formatted = (
                f"AssayFlux Runtime Error at line {line}, "
                f"column {column}: {message}"
            )
        else:
            formatted = f"AssayFlux Runtime Error: {message}"

        super().__init__(formatted)


class ReturnSignal(Exception):
    """Internal signal for returning from a function."""

    def __init__(self, value: Any):
        self.value = value


class StopSignal(Exception):
    """Internal signal for stopping a repeat loop."""


class SkipSignal(Exception):
    """Internal signal for skipping a repeat iteration."""


@dataclass
class FunctionValue:
    """A function declared in AssayFlux."""

    definition: FunctionDefinition


class Environment:
    """Stores variables and constants."""

    def __init__(
        self,
        parent: Optional["Environment"] = None,
    ):
        self.values: Dict[str, Any] = {}
        self.constants = set()
        self.parent = parent

    def contains(self, name: str) -> bool:
        if name in self.values:
            return True

        if self.parent is not None:
            return self.parent.contains(name)

        return False

    def get(self, name: str) -> Any:
        if name in self.values:
            return self.values[name]

        if self.parent is not None:
            return self.parent.get(name)

        raise AssayFluxRuntimeError(
            f"Undefined variable or function '{name}'."
        )

    def define(
        self,
        name: str,
        value: Any,
        constant: bool = False,
        line: int = 0,
        column: int = 0,
    ):
        if name in self.values:
            raise AssayFluxRuntimeError(
                f"'{name}' is already defined in this scope.",
                line,
                column,
            )

        self.values[name] = value

        if constant:
            self.constants.add(name)

    def assign(
        self,
        name: str,
        value: Any,
        line: int = 0,
        column: int = 0,
    ):
        if name in self.values:
            if name in self.constants:
                raise AssayFluxRuntimeError(
                    f"Cannot reassign constant '{name}'.",
                    line,
                    column,
                )

            self.values[name] = value
            return

        if self.parent is not None and self.parent.contains(name):
            self.parent.assign(
                name,
                value,
                line,
                column,
            )
            return

        self.values[name] = value


class Interpreter:
    """Executes AssayFlux programs."""

    def __init__(self):
        self.global_environment = Environment()
        self.environment = self.global_environment
        self.output: List[str] = []
        self.call_depth = 0
        self.max_call_depth = 200

        # Register unified language dispatch as a built-in.
        self.global_environment.define(
            "dispatch",
            dispatch_language,
        )

    def run(self, source: str) -> Any:
        """Parse and execute AssayFlux source code."""

        try:
            program = parse(source)
            return self.execute_program(program)

        except (
            LexerError,
            ParserError,
            AssayFluxRuntimeError,
        ):
            raise

        except (ZeroDivisionError, OverflowError) as error:
            raise AssayFluxRuntimeError(
                f"Arithmetic operation failed: {error}"
            ) from error

    def execute_program(self, program: Program) -> Any:
        """Execute a complete program."""

        try:
            return self.execute_statements(program.statements)

        except (StopSignal, SkipSignal):
            raise AssayFluxRuntimeError(
                "'stop' and 'skip' can only be used inside a repeat loop."
            )

        except ReturnSignal:
            raise AssayFluxRuntimeError(
                "'return' cannot be used outside a function."
            )

    def execute_statements(self, statements: List[Any]) -> Any:
        """Execute statements in order."""

        result = None

        for statement in statements:
            result = self.execute_statement(statement)

        return result

    def execute_statement(self, statement: Any) -> Any:
        """Execute one statement."""

        if isinstance(statement, ImportStatement):
            return self.execute_import(statement)

        if isinstance(statement, Assignment):
            value = self.evaluate(statement.value)

            self.environment.assign(
                statement.name,
                value,
                statement.line,
                statement.column,
            )

            return value

        if isinstance(statement, ConstantDeclaration):
            value = self.evaluate(statement.value)

            self.environment.define(
                statement.name,
                value,
                constant=True,
                line=statement.line,
                column=statement.column,
            )

            return value

        if isinstance(statement, ShowStatement):
            value = self.evaluate(statement.value)
            text = self.format_value(value)

            self.output.append(text)
            print(text)

            return value

        if isinstance(statement, IfStatement):
            return self.execute_if(statement)

        if isinstance(statement, RepeatStatement):
            return self.execute_repeat(statement)

        if isinstance(statement, StopStatement):
            raise StopSignal()

        if isinstance(statement, SkipStatement):
            raise SkipSignal()

        if isinstance(statement, FunctionDefinition):
            function = FunctionValue(statement)

            self.environment.define(
                statement.name,
                function,
                line=statement.line,
                column=statement.column,
            )

            return function

        if isinstance(statement, ReturnStatement):
            value = (
                self.evaluate(statement.value)
                if statement.value is not None
                else None
            )

            raise ReturnSignal(value)

        raise AssayFluxRuntimeError(
            f"Unsupported statement type: "
            f"{type(statement).__name__}.",
            getattr(statement, "line", 0),
            getattr(statement, "column", 0),
        )

    def execute_import(self, statement: ImportStatement) -> Any:
        """Import an installed Python module."""

        module_name = statement.module_name

        try:
            module = importlib.import_module(module_name)

        except ImportError as error:
            raise AssayFluxRuntimeError(
                f"Cannot import Python module '{module_name}': {error}",
                statement.line,
                statement.column,
            ) from error

        variable_name = statement.alias or module_name

        self.environment.define(
            variable_name,
            module,
            line=statement.line,
            column=statement.column,
        )

        return module

    def execute_if(self, statement: IfStatement) -> Any:
        """Execute conditional branches."""

        if self.is_truthy(self.evaluate(statement.condition)):
            return self.execute_statements(statement.body)

        for branch in statement.otherwise_branches:
            if self.is_truthy(self.evaluate(branch.condition)):
                return self.execute_statements(branch.statements)

        if statement.else_body is not None:
            return self.execute_statements(statement.else_body)

        return None

    def execute_repeat(self, statement: RepeatStatement) -> Any:
        """Execute a repeat loop."""

        if statement.count is None:
            count = None
        else:
            count_value = self.evaluate(statement.count)

            if isinstance(count_value, bool) or not isinstance(
                count_value, int
            ):
                raise AssayFluxRuntimeError(
                    "The repeat count must be an integer.",
                    statement.line,
                    statement.column,
                )

            if count_value < 0:
                raise AssayFluxRuntimeError(
                    "The repeat count cannot be negative.",
                    statement.line,
                    statement.column,
                )

            count = count_value

        result = None
        iteration = 0

        while count is None or iteration < count:
            try:
                result = self.execute_statements(statement.body)

            except SkipSignal:
                pass

            except StopSignal:
                break

            iteration += 1

        return result

    def evaluate(self, expression: Any) -> Any:
        """Evaluate an expression."""

        if expression is None:
            return None

        if isinstance(expression, NumberLiteral):
            return expression.value

        if isinstance(expression, StringLiteral):
            return expression.value

        if isinstance(expression, BooleanLiteral):
            return expression.value

        if isinstance(expression, Identifier):
            return self.environment.get(expression.name)

        if isinstance(expression, UnaryOperation):
            return self.evaluate_unary(expression)

        if isinstance(expression, BinaryOperation):
            return self.evaluate_binary(expression)

        if isinstance(expression, MemberAccess):
            return self.evaluate_member_access(expression)

        if isinstance(expression, FunctionCall):
            arguments = [
                self.evaluate(argument)
                for argument in expression.arguments
            ]

            return self.call_function(
                expression.name,
                arguments,
                expression.line,
                expression.column,
            )

        raise AssayFluxRuntimeError(
            f"Unsupported expression type: "
            f"{type(expression).__name__}.",
            getattr(expression, "line", 0),
            getattr(expression, "column", 0),
        )

    def evaluate_unary(self, expression: UnaryOperation) -> Any:
        """Evaluate unary operators."""

        value = self.evaluate(expression.operand)
        operator = expression.operator

        if operator == "-":
            self.require_number(value, expression)
            return -value

        if operator == "+":
            self.require_number(value, expression)
            return +value

        if operator == "not":
            return not self.is_truthy(value)

        raise AssayFluxRuntimeError(
            f"Unsupported unary operator '{operator}'.",
            expression.line,
            expression.column,
        )

    def evaluate_binary(self, expression: BinaryOperation) -> Any:
        """Evaluate binary operators."""

        operator = expression.operator
        left = self.evaluate(expression.left)

        if operator == "and":
            if not self.is_truthy(left):
                return False

            return self.is_truthy(
                self.evaluate(expression.right)
            )

        if operator == "or":
            if self.is_truthy(left):
                return True

            return self.is_truthy(
                self.evaluate(expression.right)
            )

        right = self.evaluate(expression.right)

        try:
            if operator == "+":
                if isinstance(left, str) and isinstance(right, str):
                    return left + right

                self.require_number(left, expression)
                self.require_number(right, expression)
                return left + right

            if operator == "-":
                self.require_number(left, expression)
                self.require_number(right, expression)
                return left - right

            if operator == "*":
                self.require_number(left, expression)
                self.require_number(right, expression)
                return left * right

            if operator == "/":
                self.require_number(left, expression)
                self.require_number(right, expression)

                if right == 0:
                    raise AssayFluxRuntimeError(
                        "Division by zero is not allowed.",
                        expression.line,
                        expression.column,
                    )

                return left / right

            if operator == "%":
                self.require_number(left, expression)
                self.require_number(right, expression)

                if right == 0:
                    raise AssayFluxRuntimeError(
                        "Remainder by zero is not allowed.",
                        expression.line,
                        expression.column,
                    )

                return left % right

            if operator == "==":
                return left == right

            if operator == "!=":
                return left != right

            if operator == ">":
                return left > right

            if operator == "<":
                return left < right

            if operator == ">=":
                return left >= right

            if operator == "<=":
                return left <= right

        except AssayFluxRuntimeError:
            raise

        except (TypeError, ValueError, OverflowError) as error:
            raise AssayFluxRuntimeError(
                f"Cannot apply operator '{operator}': {error}",
                expression.line,
                expression.column,
            ) from error

        raise AssayFluxRuntimeError(
            f"Unsupported binary operator '{operator}'.",
            expression.line,
            expression.column,
        )

    def evaluate_member_access(
        self,
        expression: MemberAccess,
    ) -> Any:
        """Read an object's member or a dictionary entry."""

        obj = self.evaluate(expression.object)
        member = expression.member

        if isinstance(obj, dict):
            if member not in obj:
                raise AssayFluxRuntimeError(
                    f"Dictionary has no key '{member}'.",
                    expression.line,
                    expression.column,
                )

            return obj[member]

        try:
            return getattr(obj, member)

        except AttributeError as error:
            raise AssayFluxRuntimeError(
                f"Object of type '{type(obj).__name__}' "
                f"has no member '{member}'.",
                expression.line,
                expression.column,
            ) from error

    def call_function(
        self,
        name: str,
        arguments: List[Any],
        line: int = 0,
        column: int = 0,
    ) -> Any:
        """Call an AssayFlux function or an imported Python function."""

        # Qualified calls, such as math.sqrt or numpy.array.
        if "." in name:
            parts = name.split(".")

            if any(not part for part in parts):
                raise AssayFluxRuntimeError(
                    f"Invalid qualified function name '{name}'.",
                    line,
                    column,
                )

            value = self.environment.get(parts[0])

            for member in parts[1:]:
                try:
                    value = getattr(value, member)

                except AttributeError as error:
                    raise AssayFluxRuntimeError(
                        f"Function '{name}' could not be resolved: "
                        f"missing member '{member}'.",
                        line,
                        column,
                    ) from error

            if not callable(value):
                raise AssayFluxRuntimeError(
                    f"'{name}' is not callable.",
                    line,
                    column,
                )

            try:
                return value(*arguments)

            except Exception as error:
                raise AssayFluxRuntimeError(
                    f"Python function '{name}' failed: "
                    f"{type(error).__name__}: {error}",
                    line,
                    column,
                ) from error

        # Ordinary AssayFlux-defined functions.
        function = self.environment.get(name)

        # Built-in Python callables, including dispatch.
        if callable(function):
            try:
                return function(*arguments)

            except Exception as error:
                raise AssayFluxRuntimeError(
                    f"Built-in function '{name}' failed: "
                    f"{type(error).__name__}: {error}",
                    line,
                    column,
                ) from error

        if not isinstance(function, FunctionValue):
            raise AssayFluxRuntimeError(
                f"'{name}' is not a callable AssayFlux function.",
                line,
                column,
            )

        definition = function.definition

        if len(arguments) != len(definition.parameters):
            raise AssayFluxRuntimeError(
                f"Function '{name}' expects "
                f"{len(definition.parameters)} argument(s), "
                f"but received {len(arguments)}.",
                line,
                column,
            )

        if self.call_depth >= self.max_call_depth:
            raise AssayFluxRuntimeError(
                "Maximum function call depth exceeded.",
                line,
                column,
            )

        local_environment = Environment(
            parent=self.global_environment
        )

        for parameter, value in zip(
            definition.parameters,
            arguments,
        ):
            local_environment.define(parameter, value)

        previous_environment = self.environment
        self.environment = local_environment
        self.call_depth += 1

        try:
            self.execute_statements(definition.body)

        except ReturnSignal as signal:
            return signal.value

        finally:
            self.environment = previous_environment
            self.call_depth -= 1

        return None

    @staticmethod
    def require_number(value: Any, expression: Any):
        """Require an integer or floating-point value."""

        if isinstance(value, bool) or not isinstance(
            value, (int, float)
        ):
            raise AssayFluxRuntimeError(
                f"Expected a number, received "
                f"{type(value).__name__}.",
                getattr(expression, "line", 0),
                getattr(expression, "column", 0),
            )

    @staticmethod
    def is_truthy(value: Any) -> bool:
        """Evaluate the truthiness of a value."""

        return bool(value)

    @staticmethod
    def format_value(value: Any) -> str:
        """Format a value for the show statement."""

        if value is True:
            return "true"

        if value is False:
            return "false"

        if value is None:
            return "none"

        return str(value)


def execute(source: str) -> Any:
    """Convenience function for executing AssayFlux code."""

    return Interpreter().run(source)


__all__ = [
    "AssayFluxRuntimeError",
    "Environment",
    "FunctionValue",
    "Interpreter",
    "execute",
]