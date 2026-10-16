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
    AppDeclaration,
    Assignment,
    BinaryOperation,
    BooleanLiteral,
    ConstantDeclaration,
    ExpressionStatement,
    FunctionCall,
    FunctionDefinition,
    Identifier,
    IfStatement,
    ImportStatement,
    MemberAccess,
    NoneLiteral,
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
# RUNTIME ERRORS
# ============================================================

class AssayFluxRuntimeError(Exception):
    """Error raised when an AssayFlux program cannot execute."""

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


# ============================================================
# INTERNAL CONTROL SIGNALS
# ============================================================

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
    Internal signal that terminates the current program.

    This derives from BaseException so ordinary Python exception
    handlers do not accidentally intercept the destruction signal.
    The signal is caught by Interpreter.run().
    """


# ============================================================
# FUNCTION VALUES
# ============================================================

@dataclass
class FunctionValue:
    """A user-defined AssayFlux function."""

    definition: FunctionDefinition


# ============================================================
# ENVIRONMENT
# ============================================================

class Environment:
    """
    Stores variables and constants.

    Each environment may have a parent environment. Functions use
    this relationship to access global variables.
    """

    def __init__(
        self,
        parent: Optional["Environment"] = None,
    ):
        self.values: Dict[str, Any] = {}
        self.constants = set()
        self.parent = parent

    def contains(self, name: str) -> bool:
        """Check whether a name exists in this scope or a parent."""
        if name in self.values:
            return True

        if self.parent is not None:
            return self.parent.contains(name)

        return False

    def get(self, name: str) -> Any:
        """Retrieve a variable or function."""
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
        """Create a variable, function, or constant."""
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
        """Assign a variable while enforcing constant protection."""
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


# ============================================================
# INTERPRETER
# ============================================================

class Interpreter:
    """
    Executes AssayFlux programs.

    A destroyed interpreter instance cannot execute another program.
    Create a new Interpreter instance for a new execution.
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

        self.global_environment.define(
            "dispatch",
            dispatch_language,
        )

        self.global_environment.define(
            "input",
            input,
        )

        self.global_environment.define(
            "destroy",
            self.destroy,
        )

    # ========================================================
    # PROGRAM LIFECYCLE
    # ========================================================

    def destroy(self) -> None:
        """
        Terminate the current AssayFlux execution.

        This clears state owned by this interpreter instance.
        It does not delete files, erase the operating system,
        or modify the GitHub repository.
        """
        if self.destroyed:
            raise DestroySignal()

        self.destroyed = True

        self.output.clear()

        self.global_environment.values.clear()
        self.global_environment.constants.clear()

        self.environment = self.global_environment

        self.application_name = None

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
            # Restore the interpreter's top-level environment after
            # destruction has propagated through any active functions.
            self.environment = self.global_environment

            return None

        except (
            LexerError,
            ParserError,
            AssayFluxRuntimeError,
        ):
            raise

        except (
            ZeroDivisionError,
            OverflowError,
        ) as error:
            raise AssayFluxRuntimeError(
                f"Arithmetic operation failed: {error}"
            ) from error

    def execute_program(self, program: Program) -> Any:
        """Execute a parsed program."""
        if self.destroyed:
            return None

        try:
            return self.execute_statements(
                program.statements
            )

        except DestroySignal:
            raise

        except (
            StopSignal,
            SkipSignal,
        ):
            raise AssayFluxRuntimeError(
                "'stop' and 'skip' can only be used "
                "inside a repeat loop."
            )

        except ReturnSignal:
            raise AssayFluxRuntimeError(
                "'return' cannot be used outside a function."
            )

    def execute_statements(self, statements) -> Any:
        """Execute a sequence of statements."""
        result = None

        for statement in statements:
            if self.destroyed:
                raise DestroySignal()

            result = self.execute_statement(statement)

        return result

    # ========================================================
    # STATEMENTS
    # ========================================================

    def execute_statement(self, statement) -> Any:
        """Execute one statement."""
        if self.destroyed:
            raise DestroySignal()

        # ----------------------------------------------------
        # Application declaration
        # ----------------------------------------------------

        if isinstance(statement, AppDeclaration):
            if self.application_name is not None:
                raise AssayFluxRuntimeError(
                    "Application metadata has already been declared.",
                    statement.line,
                    statement.column,
                )

            self.application_name = statement.name

            return statement.name

        # ----------------------------------------------------
        # Expression statement
        # ----------------------------------------------------

        if isinstance(statement, ExpressionStatement):
            return self.evaluate(statement.expression)

        # ----------------------------------------------------
        # Import statement
        # ----------------------------------------------------

        if isinstance(statement, ImportStatement):
            return self.execute_import(statement)

        # ----------------------------------------------------
        # Variable assignment
        # ----------------------------------------------------

        if isinstance(statement, Assignment):
            value = self.evaluate(statement.value)

            self.environment.assign(
                statement.name,
                value,
                statement.line,
                statement.column,
            )

            return value

        # ----------------------------------------------------
        # Constant declaration
        # ----------------------------------------------------

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

        # ----------------------------------------------------
        # Show statement
        #
        # IMPORTANT:
        # The actual AST uses ShowStatement.value.
        # ----------------------------------------------------

        if isinstance(statement, ShowStatement):
            value = self.evaluate(statement.value)

            formatted = self.format_value(value)

            self.output.append(formatted)

            print(formatted)

            return value

        # ----------------------------------------------------
        # Conditional statement
        # ----------------------------------------------------

        if isinstance(statement, IfStatement):
            return self.execute_if(statement)

        # ----------------------------------------------------
        # Repeat statement
        # ----------------------------------------------------

        if isinstance(statement, RepeatStatement):
            return self.execute_repeat(statement)

        # ----------------------------------------------------
        # Loop control
        # ----------------------------------------------------

        if isinstance(statement, StopStatement):
            raise StopSignal()

        if isinstance(statement, SkipStatement):
            raise SkipSignal()

        # ----------------------------------------------------
        # Function definition
        # ----------------------------------------------------

        if isinstance(statement, FunctionDefinition):
            function = FunctionValue(statement)

            self.environment.define(
                statement.name,
                function,
                line=statement.line,
                column=statement.column,
            )

            return function

        # ----------------------------------------------------
        # Return statement
        # ----------------------------------------------------

        if isinstance(statement, ReturnStatement):
            value = None

            if statement.value is not None:
                value = self.evaluate(statement.value)

            raise ReturnSignal(value)

        # ----------------------------------------------------
        # Unsupported statement
        # ----------------------------------------------------

        raise AssayFluxRuntimeError(
            "Unsupported statement type: "
            f"{type(statement).__name__}."
        )

    # ========================================================
    # IMPORTS
    # ========================================================

    def execute_import(
        self,
        statement: ImportStatement,
    ) -> Any:
        """
        Import a Python module.

        IMPORTANT:
        The actual AST field is module_name.
        """
        module_name = statement.module_name

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

        alias = (
            statement.alias
            or module_name.split(".")[0]
        )

        self.environment.define(
            alias,
            module,
            line=statement.line,
            column=statement.column,
        )

        return module

    # ========================================================
    # CONDITIONALS
    # ========================================================

    def execute_if(
        self,
        statement: IfStatement,
    ) -> Any:
        """Execute if, otherwise, and else branches."""
        if self.is_truthy(
            self.evaluate(statement.condition)
        ):
            return self.execute_statements(
                statement.body
            )

        for branch in statement.otherwise_branches:
            if self.is_truthy(
                self.evaluate(branch.condition)
            ):
                # IMPORTANT:
                # ConditionalBranch uses 'statements',
                # not 'body'.
                return self.execute_statements(
                    branch.statements
                )

        if statement.else_body is not None:
            return self.execute_statements(
                statement.else_body
            )

        return None

    # ========================================================
    # REPEAT LOOPS
    # ========================================================

    def execute_repeat(
        self,
        statement: RepeatStatement,
    ) -> Any:
        """
        Execute a repeat loop.

        Supported modes:

        condition:
            Repeat while the condition is true.

        count:
            Execute a fixed number of iterations.

        forever:
            Repeat until stop() or destroy() terminates execution.

        A maximum iteration limit protects against accidental
        unbounded execution.
        """
        result = None
        iterations = 0

        mode = getattr(
            statement,
            "mode",
            "condition",
        )

        condition = getattr(
            statement,
            "condition",
            None,
        )

        count_expression = getattr(
            statement,
            "count",
            None,
        )

        # ----------------------------------------------------
        # Counted repeat
        # ----------------------------------------------------

        if mode == "count":
            if count_expression is not None:
                raw_count = self.evaluate(
                    count_expression
                )

            elif condition is not None:
                # Compatibility with older AST representations.
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

            if isinstance(count, int):
                pass

            elif isinstance(count, float):
                if not math.isfinite(count):
                    raise AssayFluxRuntimeError(
                        "repeat count must be finite.",
                        statement.line,
                        statement.column,
                    )

                if not count.is_integer():
                    raise AssayFluxRuntimeError(
                        "repeat count must be a whole number.",
                        statement.line,
                        statement.column,
                    )

                count = int(count)

            else:
                raise AssayFluxRuntimeError(
                    "repeat count must be a whole number.",
                    statement.line,
                    statement.column,
                )

            if count < 0:
                raise AssayFluxRuntimeError(
                    "repeat count cannot be negative.",
                    statement.line,
                    statement.column,
                )

            if count > self.max_loop_iterations:
                raise AssayFluxRuntimeError(
                    "repeat count exceeds the safety limit "
                    f"of {self.max_loop_iterations}.",
                    statement.line,
                    statement.column,
                )

            for _ in range(count):
                if self.destroyed:
                    raise DestroySignal()

                try:
                    result = self.execute_statements(
                        statement.body
                    )

                except SkipSignal:
                    # Continue with the next iteration.
                    pass

                except StopSignal:
                    # Exit this repeat loop.
                    break

                iterations += 1

            return result

        # ----------------------------------------------------
        # Condition-controlled or infinite repeat
        # ----------------------------------------------------

        if mode not in (
            "condition",
            "forever",
        ):
            raise AssayFluxRuntimeError(
                f"Unknown repeat mode '{mode}'.",
                statement.line,
                statement.column,
            )

        while True:
            if self.destroyed:
                raise DestroySignal()

            # Condition-controlled mode.
            if (
                mode == "condition"
                and condition is not None
            ):
                if not self.is_truthy(
                    self.evaluate(condition)
                ):
                    break

            # A condition-less repeat is treated as infinite
            # for compatibility with older AST nodes.

            if iterations >= self.max_loop_iterations:
                raise AssayFluxRuntimeError(
                    "repeat loop exceeded the safety limit "
                    f"of {self.max_loop_iterations} iterations.",
                    statement.line,
                    statement.column,
                )

            try:
                result = self.execute_statements(
                    statement.body
                )

            except SkipSignal:
                # Skip the rest of this iteration.
                pass

            except StopSignal:
                # Stop the nearest active loop.
                break

            iterations += 1

        return result

    # ========================================================
    # EXPRESSIONS
    # ========================================================

    def evaluate(self, expression) -> Any:
        """Evaluate an expression node."""
        if self.destroyed:
            raise DestroySignal()

        # ----------------------------------------------------
        # Literals
        # ----------------------------------------------------

        if isinstance(expression, NumberLiteral):
            return expression.value

        if isinstance(expression, StringLiteral):
            return expression.value

        if isinstance(expression, BooleanLiteral):
            return expression.value

        if isinstance(expression, NoneLiteral):
            return None

        # ----------------------------------------------------
        # Identifier
        # ----------------------------------------------------

        if isinstance(expression, Identifier):
            return self.environment.get(
                expression.name
            )

        # ----------------------------------------------------
        # Unary operation
        # ----------------------------------------------------

        if isinstance(expression, UnaryOperation):
            value = self.evaluate(
                expression.operand
            )

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

            if expression.operator in (
                "not",
                "!",
            ):
                return not self.is_truthy(value)

            raise AssayFluxRuntimeError(
                "Unsupported unary operator "
                f"'{expression.operator}'.",
                expression.line,
                expression.column,
            )

        # ----------------------------------------------------
        # Binary operation
        # ----------------------------------------------------

        if isinstance(expression, BinaryOperation):
            return self.evaluate_binary(expression)

        # ----------------------------------------------------
        # Member access
        # ----------------------------------------------------

        if isinstance(expression, MemberAccess):
            return self.evaluate_member_access(
                expression
            )

        # ----------------------------------------------------
        # Function call
        # ----------------------------------------------------

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
            "Unsupported expression type: "
            f"{type(expression).__name__}."
        )

    # ========================================================
    # BINARY OPERATIONS
    # ========================================================

    def evaluate_binary(
        self,
        expression: BinaryOperation,
    ) -> Any:
        """Evaluate binary operations with short-circuit logic."""
        operator = expression.operator

        left = self.evaluate(
            expression.left
        )

        # ----------------------------------------------------
        # Logical AND
        # ----------------------------------------------------

        if operator in (
            "and",
            "&&",
        ):
            if not self.is_truthy(left):
                return False

            right = self.evaluate(
                expression.right
            )

            return self.is_truthy(right)

        # ----------------------------------------------------
        # Logical OR
        # ----------------------------------------------------

        if operator in (
            "or",
            "||",
        ):
            if self.is_truthy(left):
                return True

            right = self.evaluate(
                expression.right
            )

            return self.is_truthy(right)

        right = self.evaluate(
            expression.right
        )

        try:
            # Addition also permits Python-supported
            # concatenation, such as strings.
            if operator == "+":
                return left + right

            if operator == "-":
                return (
                    self.require_number(
                        left,
                        "subtraction",
                        expression.line,
                        expression.column,
                    )
                    -
                    self.require_number(
                        right,
                        "subtraction",
                        expression.line,
                        expression.column,
                    )
                )

            if operator == "*":
                return (
                    self.require_number(
                        left,
                        "multiplication",
                        expression.line,
                        expression.column,
                    )
                    *
                    self.require_number(
                        right,
                        "multiplication",
                        expression.line,
                        expression.column,
                    )
                )

            if operator == "/":
                return (
                    self.require_number(
                        left,
                        "division",
                        expression.line,
                        expression.column,
                    )
                    /
                    self.require_number(
                        right,
                        "division",
                        expression.line,
                        expression.column,
                    )
                )

            if operator == "%":
                return (
                    self.require_number(
                        left,
                        "remainder",
                        expression.line,
                        expression.column,
                    )
                    %
                    self.require_number(
                        right,
                        "remainder",
                        expression.line,
                        expression.column,
                    )
                )

            if operator == "**":
                base = self.require_number(
                    left,
                    "exponentiation",
                    expression.line,
                    expression.column,
                )

                exponent = self.require_number(
                    right,
                    "exponentiation",
                    expression.line,
                    expression.column,
                )

                if abs(exponent) > 10_000:
                    raise AssayFluxRuntimeError(
                        "Exponent exceeds the safety limit.",
                        expression.line,
                        expression.column,
                    )

                return base ** exponent

            if operator == "==":
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
                expression.line,
                expression.column,
            ) from error

        raise AssayFluxRuntimeError(
            f"Unsupported binary operator '{operator}'.",
            expression.line,
            expression.column,
        )
    # ========================================================
    # MEMBER ACCESS
    # ========================================================

    def evaluate_member_access(
        self,
        expression: MemberAccess,
    ) -> Any:
        """Evaluate member access on an object or module."""
        target = self.evaluate(
            expression.object
        )

        try:
            return getattr(
                target,
                expression.member,
            )

        except DestroySignal:
            raise

        except Exception as error:
            raise AssayFluxRuntimeError(
                f"Cannot access member '{expression.member}': "
                f"{type(error).__name__}: {error}",
                expression.line,
                expression.column,
            ) from error

    # ========================================================
    # FUNCTION CALLS
    # ========================================================

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

        # ----------------------------------------------------
        # Qualified Python function, such as math.sqrt()
        # ----------------------------------------------------

        if "." in name:
            parts = name.split(".")

            value = self.environment.get(
                parts[0]
            )

            for part in parts[1:]:
                try:
                    value = getattr(
                        value,
                        part,
                    )

                except DestroySignal:
                    raise

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

        # ----------------------------------------------------
        # Unqualified function
        # ----------------------------------------------------

        function = self.environment.get(name)

        # ----------------------------------------------------
        # AssayFlux-defined function
        # ----------------------------------------------------

        if isinstance(function, FunctionValue):
            definition = function.definition

            if len(arguments) != len(
                definition.parameters
            ):
                raise AssayFluxRuntimeError(
                    f"Function '{name}' expects "
                    f"{len(definition.parameters)} argument(s), "
                    f"but received {len(arguments)}.",
                    line,
                    column,
                )

            if self.call_depth >= self.max_call_depth:
                raise AssayFluxRuntimeError(
                    "Maximum function call depth of "
                    f"{self.max_call_depth} exceeded.",
                    line,
                    column,
                )

            local_environment = Environment(
                self.global_environment
            )

            for parameter, argument in zip(
                definition.parameters,
                arguments,
            ):
                local_environment.define(
                    parameter,
                    argument,
                )

            previous_environment = self.environment

            self.environment = local_environment
            self.call_depth += 1

            try:
                self.execute_statements(
                    definition.body
                )

            except ReturnSignal as signal:
                return signal.value

            finally:
                # Always restore the previous scope, including
                # when a runtime error or destroy signal occurs.
                self.environment = previous_environment
                self.call_depth -= 1

            return None

        # ----------------------------------------------------
        # Exposed Python callable
        # ----------------------------------------------------

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

    # ========================================================
    # HELPER METHODS
    # ========================================================

    @staticmethod
    def is_truthy(value: Any) -> bool:
        """Convert a value to a Boolean truth value."""
        return bool(value)

    @staticmethod
    def require_number(
        value: Any,
        operation: str,
        line: int = 0,
        column: int = 0,
    ) -> Any:
        """Validate numeric operands."""
        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
        ):
            raise AssayFluxRuntimeError(
                f"{operation} requires a number, "
                f"but received {type(value).__name__}.",
                line,
                column,
            )

        if (
            isinstance(value, float)
            and not math.isfinite(value)
        ):
            raise AssayFluxRuntimeError(
                f"{operation} does not accept NaN or infinity.",
                line,
                column,
            )

        return value

    @staticmethod
    def format_value(value: Any) -> str:
        """Format values for AssayFlux output."""
        if value is True:
            return "true"

        if value is False:
            return "false"

        if value is None:
            return "none"

        return str(value)