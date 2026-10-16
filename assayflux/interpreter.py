"""
AssayFlux Scientific Systems
Interpreter Implementation

Executes AssayFlux programs and integrates with Python libraries.

Version: 0.3.0
"""

import importlib
import math
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from assayflux.interop import dispatch as dispatch_language

from assayflux.ast_nodes import (
    Assignment,
    AppDeclaration,
    ExpressionStatement,
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


# ============================================================
# Errors and internal control signals
# ============================================================

class AssayFluxRuntimeError(Exception):
    """Error raised when an AssayFlux program cannot execute."""

    def __init__(self, message: str, line: int = 0, column: int = 0):
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
    """Internal signal for stopping the nearest repeat loop."""


class SkipSignal(Exception):
    """Internal signal for skipping the current repeat iteration."""


class DestroySignal(BaseException):
    """
    Internal signal that terminates the current AssayFlux execution.

    BaseException is used so ordinary `except Exception` handlers in
    imported Python functions do not accidentally swallow this signal.
    The interpreter catches it at the program boundary.
    """


@dataclass
class FunctionValue:
    """A user-defined AssayFlux function."""

    definition: FunctionDefinition


# ============================================================
# Environment and constants
# ============================================================

class Environment:
    """Stores variables, constants, and parent-scope relationships."""

    def __init__(self, parent: Optional["Environment"] = None):
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
    ) -> None:
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
    ) -> None:
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
            self.parent.assign(name, value, line, column)
            return

        self.values[name] = value


# ============================================================
# Interpreter
# ============================================================

class Interpreter:
    """
    Executes AssayFlux programs.

    Calling destroy() permanently disables this interpreter instance.
    Create a new Interpreter instance to start a separate execution.
    """

    def __init__(self):
        self.global_environment = Environment()
        self.environment = self.global_environment

        self.output: List[str] = []
        self.call_depth = 0
        self.max_call_depth = 200
        self.max_loop_iterations = 1_000_000

        self.application_name = None
        self.destroyed = False

        self.global_environment.define("dispatch", dispatch_language)
        self.global_environment.define("input", input)
        self.global_environment.define("destroy", self.destroy)

    # --------------------------------------------------------
    # Program lifecycle
    # --------------------------------------------------------

    def destroy(self) -> None:
        """
        Stop execution and clear this interpreter's in-memory state.

        This affects only this Interpreter instance. It does not delete
        files, modify the operating system, or erase repository contents.
        """
        if self.destroyed:
            return

        self.destroyed = True
        self.output.clear()

        # Clear stored variables and constants.
        self.global_environment.values.clear()
        self.global_environment.constants.clear()

        # Drop references to the previous environment.
        self.environment = self.global_environment
        self.application_name = None

        # Raise a control signal to terminate active execution.
        raise DestroySignal()

    def run(self, source: str) -> Any:
        """Parse and execute AssayFlux source code."""
        if self.destroyed:
            raise AssayFluxRuntimeError(
                "This interpreter has been destroyed. "
                "Create a new Interpreter instance to run another program."
            )

        try:
            program = parse(source)
            return self.execute_program(program)

        except DestroySignal:
            # Destruction is an intentional termination, not a runtime error.
            return None

        except (LexerError, ParserError, AssayFluxRuntimeError):
            raise

        except (ZeroDivisionError, OverflowError) as error:
            raise AssayFluxRuntimeError(
                f"Arithmetic operation failed: {error}"
            ) from error

    def execute_program(self, program: Program) -> Any:
        """Execute a parsed program."""
        if self.destroyed:
            return None

        try:
            return self.execute_statements(program.statements)

        except DestroySignal:
            raise

        except (StopSignal, SkipSignal):
            raise AssayFluxRuntimeError(
                "'stop' and 'skip' can only be used inside a repeat loop."
            )

        except ReturnSignal:
            raise AssayFluxRuntimeError(
                "'return' cannot be used outside a function."
            )

    def execute_statements(self, statements) -> Any:
        """Execute statements in sequence."""
        result = None

        for statement in statements:
            if self.destroyed:
                raise DestroySignal()

            result = self.execute_statement(statement)

        return result

    # --------------------------------------------------------
    # Statements
    # --------------------------------------------------------

    def execute_statement(self, statement) -> Any:
        """Execute a single AST statement."""
        if self.destroyed:
            raise DestroySignal()

        if isinstance(statement, AppDeclaration):
            if self.application_name is not None:
                raise AssayFluxRuntimeError(
                    "Application metadata has already been declared.",
                    statement.line,
                    statement.column,
                )

            self.application_name = statement.name
            return statement.name

        if isinstance(statement, ExpressionStatement):
            return self.evaluate(statement.expression)

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
            value = self.evaluate(statement.expression)
            formatted = self.format_value(value)

            self.output.append(formatted)
            print(formatted)

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
            value = None

            if statement.value is not None:
                value = self.evaluate(statement.value)

            raise ReturnSignal(value)

        raise AssayFluxRuntimeError(
            f"Unsupported statement type: {type(statement).__name__}."
        )

    # --------------------------------------------------------
    # Imports
    # --------------------------------------------------------

    def execute_import(self, statement: ImportStatement) -> Any:
        """Import a Python module into the current environment."""
        module_name = statement.module

        try:
            module = importlib.import_module(module_name)
        except DestroySignal:
            raise
        except Exception as error:
            raise AssayFluxRuntimeError(
                f"Could not import '{module_name}': "
                f"{type(error).__name__}: {error}",
                statement.line,
                statement.column,
            ) from error

        alias = statement.alias or module_name.split(".")[0]

        self.environment.define(
            alias,
            module,
            line=statement.line,
            column=statement.column,
        )

        return module

    # --------------------------------------------------------
    # Conditions and loops
    # --------------------------------------------------------

    def execute_if(self, statement: IfStatement) -> Any:
        """Execute a conditional statement."""
        if self.is_truthy(self.evaluate(statement.condition)):
            return self.execute_statements(statement.body)

        for branch in statement.otherwise_branches:
            if self.is_truthy(self.evaluate(branch.condition)):
                return self.execute_statements(branch.body)

        if statement.else_body is not None:
            return self.execute_statements(statement.else_body)

        return None

    def execute_repeat(self, statement: RepeatStatement) -> Any:
        """
        Execute a repeat loop.

        Supported AST modes:
          - count: execute a fixed number of iterations
          - forever: continue until stop() or destroy()
          - condition: continue while the condition is true

        A condition-less loop is treated as an infinite loop for compatibility
        with AST nodes created before the mode field was introduced.
        """
        result = None
        iterations = 0

        mode = getattr(statement, "mode", "condition")
        count_expression = getattr(statement, "count", None)
        condition = getattr(statement, "condition", None)

        if mode == "count":
            if count_expression is not None:
                raw_count = self.evaluate(count_expression)
            elif condition is not None:
                # Backwards compatibility with older AST representations.
                raw_count = self.evaluate(condition)
            else:
                raise AssayFluxRuntimeError(
                    "A counted repeat loop requires a count.",
                    statement.line,
                    statement.column,
                )

            count = self.require_number(
                raw_count,
                "repeat count",
                statement.line,
                statement.column,
            )

            if isinstance(count, bool) or not float(count).is_integer():
                raise AssayFluxRuntimeError(
                    "repeat count must be a whole number.",
                    statement.line,
                    statement.column,
                )

            count = int(count)

            if count < 0:
                raise AssayFluxRuntimeError(
                    "repeat count cannot be negative.",
                    statement.line,
                    statement.column,
                )

            if count > self.max_loop_iterations:
                raise AssayFluxRuntimeError(
                    f"repeat count exceeds the safety limit of "
                    f"{self.max_loop_iterations}.",
                    statement.line,
                    statement.column,
                )

            for _ in range(count):
                if self.destroyed:
                    raise DestroySignal()

                try:
                    result = self.execute_statements(statement.body)
                except SkipSignal:
                    pass
                except StopSignal:
                    break

                iterations += 1

            return result

        if mode not in ("condition", "forever"):
            raise AssayFluxRuntimeError(
                f"Unknown repeat mode '{mode}'.",
                statement.line,
                statement.column,
            )

        while True:
            if self.destroyed:
                raise DestroySignal()

            if mode == "condition" and condition is not None:
                if not self.is_truthy(self.evaluate(condition)):
                    break
            elif mode == "condition" and condition is None:
                # Preserve older syntax: repeat with no condition means forever.
                pass

            if iterations >= self.max_loop_iterations:
                raise AssayFluxRuntimeError(
                    f"repeat loop exceeded the safety limit of "
                    f"{self.max_loop_iterations} iterations.",
                    statement.line,
                    statement.column,
                )

            try:
                result = self.execute_statements(statement.body)
            except SkipSignal:
                pass
            except StopSignal:
                break

            iterations += 1

        return result

    # --------------------------------------------------------
    # Expressions
    # --------------------------------------------------------

    def evaluate(self, expression) -> Any:
        """Evaluate an expression node."""
        if self.destroyed:
            raise DestroySignal()

        if isinstance(expression, NumberLiteral):
            return expression.value

        if isinstance(expression, StringLiteral):
            return expression.value

        if isinstance(expression, BooleanLiteral):
            return expression.value

        if isinstance(expression, Identifier):
            return self.environment.get(expression.name)

        if isinstance(expression, UnaryOperation):
            value = self.evaluate(expression.operand)

            if expression.operator == "-":
                return -self.require_number(
                    value,
                    "unary minus",
                    expression.line,
                    expression.column,
                )

            if expression.operator == "+":
                return self.require_number(
                    value,
                    "unary plus",
                    expression.line,
                    expression.column,
                )

            if expression.operator in ("not", "!"):
                return not self.is_truthy(value)

            raise AssayFluxRuntimeError(
                f"Unsupported unary operator '{expression.operator}'.",
                expression.line,
                expression.column,
            )

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
            f"Unsupported expression type: {type(expression).__name__}."
        )

    def evaluate_binary(self, expression: BinaryOperation) -> Any:
        """Evaluate a binary expression with short-circuit boolean operators."""
        operator = expression.operator

        left = self.evaluate(expression.left)

        if operator in ("and", "&&"):
            if not self.is_truthy(left):
                return False

            right = self.evaluate(expression.right)
            return self.is_truthy(right)

        if operator in ("or", "||"):
            if self.is_truthy(left):
                return True

            right = self.evaluate(expression.right)
            return self.is_truthy(right)

        right = self.evaluate(expression.right)

        try:
            if operator == "+":
                return left + right

            if operator == "-":
                return self.require_number(left, "subtraction") - self.require_number(
                    right, "subtraction"
                )

            if operator == "*":
                return self.require_number(left, "multiplication") * self.require_number(
                    right, "multiplication"
                )

            if operator == "/":
                return self.require_number(left, "division") / self.require_number(
                    right, "division"
                )

            if operator == "%":
                return self.require_number(left, "remainder") % self.require_number(
                    right, "remainder"
                )

            if operator == "**":
                exponent = self.require_number(right, "exponentiation")

                if abs(exponent) > 10_000:
                    raise AssayFluxRuntimeError(
                        "Exponent exceeds the safety limit."
                    )

                return self.require_number(
                    left, "exponentiation"
                ) ** exponent

            if operator in ("==", "="):
                return left == right

            if operator == "!=":
                return left != right

            if operator == "<":
                return left < right

            if operator == "<=":
                return left <= right

            if operator == ">":
                return left > right

            if operator == ">=":
                return left >= right

        except DestroySignal:
            raise
        except AssayFluxRuntimeError:
            raise
        except Exception as error:
            raise AssayFluxRuntimeError(
                f"Operator '{operator}' failed: "
                f"{type(error).__name__}: {error}",
                getattr(expression, "line", 0),
                getattr(expression, "column", 0),
            ) from error

        raise AssayFluxRuntimeError(
            f"Unsupported binary operator '{operator}'.",
            getattr(expression, "line", 0),
            getattr(expression, "column", 0),
        )

    def evaluate_member_access(self, expression: MemberAccess) -> Any:
        """Evaluate access to a Python module or object's member."""
        target = self.evaluate(expression.object)

        try:
            return getattr(target, expression.member)
        except Exception as error:
            raise AssayFluxRuntimeError(
                f"Cannot access member '{expression.member}': "
                f"{type(error).__name__}: {error}",
                expression.line,
                expression.column,
            ) from error

    # --------------------------------------------------------
    # Function calls
    # --------------------------------------------------------

    def call_function(
        self,
        name: str,
        arguments: List[Any],
        line: int = 0,
        column: int = 0,
    ) -> Any:
        """Call an AssayFlux function or an exposed Python callable."""
        if self.destroyed:
            raise DestroySignal()

        # Qualified calls, such as math.sqrt(...).
        if "." in name:
            parts = name.split(".")
            value = self.environment.get(parts[0])

            for part in parts[1:]:
                try:
                    value = getattr(value, part)
                except Exception as error:
                    raise AssayFluxRuntimeError(
                        f"Cannot resolve '{name}': "
                        f"{type(error).__name__}: {error}",
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
            except DestroySignal:
                raise
            except Exception as error:
                raise AssayFluxRuntimeError(
                    f"Python function '{name}' failed: "
                    f"{type(error).__name__}: {error}",
                    line,
                    column,
                ) from error

        function = self.environment.get(name)

        if isinstance(function, FunctionValue):
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
                    f"Maximum function call depth of "
                    f"{self.max_call_depth} exceeded.",
                    line,
                    column,
                )

            local_environment = Environment(self.global_environment)

            for parameter, argument in zip(
                definition.parameters,
                arguments,
            ):
                local_environment.define(parameter, argument)

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

        if callable(function):
            try:
                return function(*arguments)
            except DestroySignal:
                raise
            except Exception as error:
                raise AssayFluxRuntimeError(
                    f"Built-in function '{name}' failed: "
                    f"{type(error).__name__}: {error}",
                    line,
                    column,
                ) from error

        raise AssayFluxRuntimeError(
            f"'{name}' is not a function.",
            line,
            column,
        )

    # --------------------------------------------------------
    # Helpers
    # --------------------------------------------------------

    @staticmethod
    def is_truthy(value: Any) -> bool:
        """Convert a value to an AssayFlux truth value."""
        return bool(value)

    @staticmethod
    def require_number(
        value: Any,
        operation: str,
        line: int = 0,
        column: int = 0,
    ) -> Any:
        """Validate numeric operands and reject booleans."""
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise AssayFluxRuntimeError(
                f"{operation} requires a number, "
                f"but received {type(value).__name__}.",
                line,
                column,
            )

        if isinstance(value, float) and not math.isfinite(value):
            raise AssayFluxRuntimeError(
                f"{operation} does not accept NaN or infinity.",
                line,
                column,
            )

        return value

    @staticmethod
    def format_value(value: Any) -> str:
        """Format values for display."""
        if value is True:
            return "true"

        if value is False:
            return "false"

        if value is None:
            return "none"

        return str(value)