"""
AssayFlux Scientific Systems
Tree-Walking Interpreter

Executes the AST produced by assayflux.parser.

Implemented core features:
    Variables and constants
    Numeric, string, and Boolean values
    Arithmetic and comparison operators
    Short-circuit logical expressions
    show output
    if / otherwise / else
    repeat count / condition / forever
    stop and skip
    Function definitions, calls, parameters, and return
    Python module imports
    Dotted member access
    pass
    Runtime diagnostics

The interpreter does not use eval() or exec() to evaluate
AssayFlux expressions.

Version: 1.0.0
"""

from __future__ import annotations

import builtins
import importlib
import math
import operator
import sys

from dataclasses import dataclass
from typing import Any, Callable, Iterable, Optional

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

from assayflux.lexer import Lexer, LexerError
from assayflux.parser import Parser, ParserError


INTERPRETER_VERSION = "1.0.0"


# ============================================================
# Runtime Errors
# ============================================================

class RuntimeError(Exception):
    """An AssayFlux runtime error with optional source location."""

    def __init__(
        self,
        message: str,
        line: Optional[int] = None,
        column: Optional[int] = None,
        filename: str = "<string>",
    ):
        self.message = message
        self.line = line
        self.column = column
        self.filename = filename

        if line is not None and column is not None:
            rendered = (
                f"[{filename}:{line}:{column}] "
                f"AssayFlux Runtime Error: {message}"
            )
        else:
            rendered = f"AssayFlux Runtime Error: {message}"

        super().__init__(rendered)


# ============================================================
# Environments
# ============================================================

class Environment:
    """
    A lexical environment for variables, functions, and constants.

    Each function invocation receives a local environment.
    Global declarations remain accessible through parent scopes.
    """

    def __init__(
        self,
        parent: Optional["Environment"] = None,
        *,
        function_scope: bool = False,
    ):
        self.values: dict[str, Any] = {}
        self.constants: set[str] = set()
        self.parent = parent
        self.function_scope = function_scope

    def resolve(self, name: str) -> Optional["Environment"]:
        if name in self.values:
            return self

        if self.parent is not None:
            return self.parent.resolve(name)

        return None

    def is_constant(self, name: str) -> bool:
        if name in self.constants:
            return True

        if self.parent is not None:
            return self.parent.is_constant(name)

        return False

    def get(self, name: str) -> Any:
        if name in self.values:
            return self.values[name]

        if self.parent is not None:
            return self.parent.get(name)

        raise RuntimeError(f"Undefined name {name!r}.")

    def define(self, name: str, value: Any) -> None:
        if not isinstance(name, str) or not name.isidentifier():
            raise RuntimeError(f"Invalid identifier {name!r}.")

        if name in self.constants:
            raise RuntimeError(
                f"Cannot redefine constant {name!r}."
            )

        self.values[name] = value

    def define_constant(self, name: str, value: Any) -> None:
        if not isinstance(name, str) or not name.isidentifier():
            raise RuntimeError(
                f"Invalid constant name {name!r}."
            )

        if name in self.values or self.is_constant(name):
            raise RuntimeError(
                f"Name {name!r} is already defined."
            )

        self.values[name] = value
        self.constants.add(name)

    def assign(self, name: str, value: Any) -> None:
        """
        Assign a variable.

        At global scope, an assignment updates an existing variable
        or creates a new one.

        In a function, assignments create local bindings unless
        the name already exists locally. Outer constants cannot
        be overwritten.
        """

        if self.function_scope:
            if name in self.constants:
                raise RuntimeError(
                    f"Cannot reassign constant {name!r}."
                )

            if name in self.values:
                self.values[name] = value
                return

            if (
                self.parent is not None
                and self.parent.is_constant(name)
            ):
                raise RuntimeError(
                    f"Cannot reassign constant {name!r}."
                )

            self.values[name] = value
            return

        target = self.resolve(name)

        if target is None:
            self.values[name] = value
            return

        if name in target.constants:
            raise RuntimeError(
                f"Cannot reassign constant {name!r}."
            )

        target.values[name] = value


# ============================================================
# Internal Control-Flow Signals
# ============================================================

@dataclass
class _UserFunction:
    declaration: FunctionDefinition
    closure: Environment
    interpreter: "Interpreter"

    def __call__(self, *arguments: Any) -> Any:
        return self.interpreter._call_user_function(
            self,
            arguments,
        )


class _ReturnSignal(BaseException):
    def __init__(self, value: Any):
        self.value = value


class _StopSignal(BaseException):
    pass


class _SkipSignal(BaseException):
    pass


# ============================================================
# Operator Tables
# ============================================================

_BINARY_OPERATORS: dict[str, Callable[[Any, Any], Any]] = {
    "+": operator.add,
    "-": operator.sub,
    "*": operator.mul,
    "/": operator.truediv,
    "//": operator.floordiv,
    "%": operator.mod,
    "**": operator.pow,
    "==": operator.eq,
    "!=": operator.ne,
    "<": operator.lt,
    "<=": operator.le,
    ">": operator.gt,
    ">=": operator.ge,
}

_UNARY_OPERATORS: dict[str, Callable[[Any], Any]] = {
    "+": operator.pos,
    "-": operator.neg,
    "not": operator.not_,
}


# ============================================================
# Interpreter
# ============================================================

class Interpreter:
    """
    Execute AssayFlux source or a parsed Program.

    Example:

        interpreter = Interpreter()
        interpreter.run('show "Hello, AssayFlux"')

    Public compatibility attributes:
        global_environment
        global_env
        current_env
        output

    State persists between calls to run().
    """

    def __init__(
        self,
        *,
        max_loop_iterations: int = 100_000,
        output_stream=None,
    ):
        if (
            isinstance(max_loop_iterations, bool)
            or not isinstance(max_loop_iterations, int)
            or max_loop_iterations < 1
        ):
            raise ValueError(
                "max_loop_iterations must be a positive integer."
            )

        self.global_environment = Environment()

        # Compatibility with the original interpreter interface.
        self.global_env = self.global_environment
        self.current_env = self.global_environment

        self.output: list[str] = []
        self.app_name: Optional[str] = None

        self.max_loop_iterations = max_loop_iterations
        self.output_stream = output_stream

        self.filename = "<string>"
        self._call_depth = 0
        self.max_call_depth = 1_000

        self._install_builtins()

    # --------------------------------------------------------
    # Built-in names
    # --------------------------------------------------------

    def _install_builtins(self) -> None:
        """
        Install selected Python built-ins.

        This is not a security sandbox. Imported Python modules
        and exposed callables may have unrestricted capabilities.
        """

        safe_builtins = {
            "abs": builtins.abs,
            "all": builtins.all,
            "any": builtins.any,
            "bool": builtins.bool,
            "dict": builtins.dict,
            "enumerate": builtins.enumerate,
            "float": builtins.float,
            "int": builtins.int,
            "len": builtins.len,
            "list": builtins.list,
            "max": builtins.max,
            "min": builtins.min,
            "pow": builtins.pow,
            "range": builtins.range,
            "repr": builtins.repr,
            "round": builtins.round,
            "set": builtins.set,
            "sorted": builtins.sorted,
            "str": builtins.str,
            "sum": builtins.sum,
            "tuple": builtins.tuple,
            "type": builtins.type,
            "zip": builtins.zip,
            "isinstance": builtins.isinstance,
            "print": builtins.print,
        }

        for name, value in safe_builtins.items():
            self.global_environment.define(name, value)

        self.global_environment.define("math", math)

        try:
            from assayflux.interop import dispatch
        except (ImportError, AttributeError):
            dispatch = None

        if dispatch is not None:
            self.global_environment.define("dispatch", dispatch)

    # --------------------------------------------------------
    # Public API
    # --------------------------------------------------------

    def run(
        self,
        source: str,
        filename: str = "<string>",
    ) -> list[Any]:
        """Tokenize, parse, and execute AssayFlux source."""

        if not isinstance(source, str):
            raise TypeError(
                "Interpreter.run(source) expects a string."
            )

        previous_filename = self.filename
        self.filename = filename

        try:
            tokens = Lexer(
                source,
                filename=filename,
            ).tokenize()

            program = Parser(tokens).parse()

            return self.interpret(program)

        except (LexerError, ParserError):
            raise

        finally:
            self.filename = previous_filename

    def interpret(self, ast_nodes: Any) -> list[Any]:
        """
        Execute a Program or a sequence of AST statements.

        Supports both the newer Program API and the older
        interpret(ast_nodes) interface.
        """

        if isinstance(ast_nodes, Program):
            statements = ast_nodes.statements

        elif isinstance(ast_nodes, (list, tuple)):
            statements = ast_nodes

        else:
            raise TypeError(
                "interpret() expects a Program or a list/tuple "
                "of AST statements."
            )

        results = []

        for statement in statements:
            results.append(self.visit(statement))

        return results

    def visit(self, node: Any) -> Any:
        """Dispatch an AST node to its visitor."""

        if node is None:
            return None

        method = getattr(
            self,
            f"visit_{type(node).__name__}",
            None,
        )

        if method is None:
            raise RuntimeError(
                f"Unsupported AST node {type(node).__name__}.",
                getattr(node, "line", None),
                getattr(node, "column", None),
                self.filename,
            )

        try:
            return method(node)

        except (
            RuntimeError,
            _ReturnSignal,
            _StopSignal,
            _SkipSignal,
        ):
            raise

        except Exception as error:
            raise RuntimeError(
                f"{type(error).__name__}: {error}",
                getattr(node, "line", None),
                getattr(node, "column", None),
                self.filename,
            ) from error

    def _env(self) -> Environment:
        return self.current_env

    def _write_output(self, value: Any) -> None:
        rendered = str(value)
        self.output.append(rendered)

        stream = (
            self.output_stream
            if self.output_stream is not None
            else sys.stdout
        )

        print(rendered, file=stream)

    # --------------------------------------------------------
    # Statement visitors
    # --------------------------------------------------------

    def visit_Program(self, node: Program) -> list[Any]:
        return self.interpret(node)

    def visit_AppDeclaration(
        self,
        node: AppDeclaration,
    ) -> str:
        self.app_name = node.name
        return node.name

    def visit_PassStatement(
        self,
        node: PassStatement,
    ) -> None:
        return None

    def visit_ExpressionStatement(
        self,
        node: ExpressionStatement,
    ) -> Any:
        return self.visit(node.expression)

    def visit_ShowStatement(
        self,
        node: ShowStatement,
    ) -> Any:
        value = self.visit(node.value)
        self._write_output(value)
        return value

    def visit_Assignment(
        self,
        node: Assignment,
    ) -> Any:
        value = self.visit(node.value)
        self._env().assign(node.name, value)
        return value

    def visit_ConstantDeclaration(
        self,
        node: ConstantDeclaration,
    ) -> Any:
        value = self.visit(node.value)

        self._env().define_constant(
            node.name,
            value,
        )

        return value

    def visit_ImportStatement(
        self,
        node: ImportStatement,
    ) -> Any:
        try:
            module = importlib.import_module(
                node.module_name
            )

        except Exception as error:
            raise RuntimeError(
                f"Could not import module {node.module_name!r}: "
                f"{type(error).__name__}: {error}",
                node.line,
                node.column,
                self.filename,
            ) from error

        binding = (
            node.alias
            or node.module_name.split(".")[0]
        )

        # Match Python's ordinary dotted-import binding behavior.
        if node.alias is None and "." in node.module_name:
            root_name = node.module_name.split(".")[0]

            try:
                module = importlib.import_module(root_name)
            except Exception:
                module = importlib.import_module(
                    node.module_name
                )

        self._env().define(binding, module)
        return module

    def visit_FunctionDefinition(
        self,
        node: FunctionDefinition,
    ) -> _UserFunction:
        function = _UserFunction(
            declaration=node,
            closure=self._env(),
            interpreter=self,
        )

        self._env().define(
            node.name,
            function,
        )

        return function

    def visit_ReturnStatement(
        self,
        node: ReturnStatement,
    ) -> None:
        raise _ReturnSignal(
            self.visit(node.value)
        )

    def visit_StopStatement(
        self,
        node: StopStatement,
    ) -> None:
        raise _StopSignal()

    def visit_SkipStatement(
        self,
        node: SkipStatement,
    ) -> None:
        raise _SkipSignal()

    def visit_IfStatement(
        self,
        node: IfStatement,
    ) -> Any:
        if self._truthy(self.visit(node.condition)):
            return self._execute_block(node.body)

        for branch in node.otherwise_branches:
            if self._truthy(self.visit(branch.condition)):
                return self._execute_block(
                    branch.statements
                )

        if node.else_body is not None:
            return self._execute_block(node.else_body)

        return None

    def visit_RepeatStatement(
        self,
        node: RepeatStatement,
    ) -> Any:
        if node.mode == "count":
            count_value = self.visit(node.count)

            if (
                isinstance(count_value, bool)
                or not isinstance(count_value, int)
            ):
                raise RuntimeError(
                    "A repeat count must evaluate to an integer.",
                    node.line,
                    node.column,
                    self.filename,
                )

            if count_value < 0:
                raise RuntimeError(
                    "A repeat count cannot be negative.",
                    node.line,
                    node.column,
                    self.filename,
                )

            if count_value > self.max_loop_iterations:
                raise RuntimeError(
                    "Repeat count exceeds the configured limit "
                    f"of {self.max_loop_iterations}.",
                    node.line,
                    node.column,
                    self.filename,
                )

            last_value = None

            for _ in range(count_value):
                try:
                    last_value = self._execute_block(node.body)

                except _SkipSignal:
                    continue

                except _StopSignal:
                    break

            return last_value

        if node.mode not in {"condition", "forever"}:
            raise RuntimeError(
                f"Unknown repeat mode {node.mode!r}.",
                node.line,
                node.column,
                self.filename,
            )

        last_value = None
        iterations = 0

        while (
            node.mode == "forever"
            or self._truthy(self.visit(node.condition))
        ):
            iterations += 1

            if iterations > self.max_loop_iterations:
                raise RuntimeError(
                    "Repeat loop exceeded the configured "
                    "iteration limit. Use stop or configure "
                    "max_loop_iterations if appropriate.",
                    node.line,
                    node.column,
                    self.filename,
                )

            try:
                last_value = self._execute_block(node.body)

            except _SkipSignal:
                continue

            except _StopSignal:
                break

        return last_value

    # --------------------------------------------------------
    # Literal and identifier visitors
    # --------------------------------------------------------

    def visit_NumberLiteral(
        self,
        node: NumberLiteral,
    ) -> Any:
        return node.value

    def visit_StringLiteral(
        self,
        node: StringLiteral,
    ) -> str:
        return node.value

    def visit_BooleanLiteral(
        self,
        node: BooleanLiteral,
    ) -> bool:
        return node.value

    def visit_NoneLiteral(
        self,
        node: NoneLiteral,
    ) -> None:
        return None

    def visit_Identifier(
        self,
        node: Identifier,
    ) -> Any:
        return self._env().get(node.name)
    def visit_FunctionCall(
        self,
        node: FunctionCall,
    ) -> Any:
        """Evaluate and execute a function call."""

        function = self._resolve_callable(
            node.name,
            node,
        )

        arguments = tuple(
            self.visit(argument)
            for argument in node.arguments
        )

        if not callable(function):
            raise RuntimeError(
                f"{node.name!r} is not callable.",
                node.line,
                node.column,
                self.filename,
            )

        try:
            return function(*arguments)

        except RuntimeError:
            raise

        except Exception as error:
            raise RuntimeError(
                f"Function call {node.name!r} failed: "
                f"{type(error).__name__}: {error}",
                node.line,
                node.column,
                self.filename,
            ) from error
    def visit_MemberAccess(
        self,
        node: MemberAccess,
    ) -> Any:
        owner = self.visit(node.object)

        try:
            return getattr(owner, node.member)

        except AttributeError as error:
            raise RuntimeError(
                f"Object has no member {node.member!r}.",
                node.line,
                node.column,
                self.filename,
            ) from error
   # --------------------------------------------------------
    # Unary and binary expressions
    # --------------------------------------------------------

    def visit_UnaryOperation(
        self,
        node: UnaryOperation,
    ) -> Any:
        function = _UNARY_OPERATORS.get(node.operator)

        if function is None:
            raise RuntimeError(
                f"Unsupported unary operator {node.operator!r}.",
                node.line,
                node.column,
                self.filename,
            )

        value = self.visit(node.operand)

        try:
            return function(value)

        except Exception as error:
            raise RuntimeError(
                f"Unary operator {node.operator!r} failed: "
                f"{type(error).__name__}: {error}",
                node.line,
                node.column,
                self.filename,
            ) from error

    def visit_BinaryOperation(
        self,
        node: BinaryOperation,
    ) -> Any:
        # Preserve Python-like short-circuit semantics.
        if node.operator == "and":
            left = self.visit(node.left)

            if self._truthy(left):
                return self.visit(node.right)

            return left

        if node.operator == "or":
            left = self.visit(node.left)

            if self._truthy(left):
                return left

            return self.visit(node.right)

        function = _BINARY_OPERATORS.get(node.operator)

        if function is None:
            raise RuntimeError(
                f"Unsupported binary operator {node.operator!r}.",
                node.line,
                node.column,
                self.filename,
            )

        left = self.visit(node.left)
        right = self.visit(node.right)

        try:
            return function(left, right)

        except Exception as error:
            raise RuntimeError(
                f"Operator {node.operator!r} failed: "
                f"{type(error).__name__}: {error}",
                node.line,
                node.column,
                self.filename,
            ) from error

    # --------------------------------------------------------
    # Execution helpers
    # --------------------------------------------------------

    @staticmethod
    def _truthy(value: Any) -> bool:
        return bool(value)

    def _execute_block(
        self,
        statements: Iterable[Any],
    ) -> Any:
        last_value = None

        for statement in statements:
            last_value = self.visit(statement)

        return last_value

    def _resolve_callable(
        self,
        name: str,
        node: Any,
    ) -> Any:
        parts = name.split(".")

        try:
            value = self._env().get(parts[0])

            for part in parts[1:]:
                value = getattr(value, part)

            return value

        except RuntimeError:
            raise

        except AttributeError as error:
            raise RuntimeError(
                f"Cannot resolve callable {name!r}: {error}",
                getattr(node, "line", None),
                getattr(node, "column", None),
                self.filename,
            ) from error

    def _call_user_function(
        self,
        function: _UserFunction,
        arguments: tuple[Any, ...],
    ) -> Any:
        declaration = function.declaration

        if len(arguments) != len(declaration.parameters):
            raise RuntimeError(
                f"Function {declaration.name!r} expects "
                f"{len(declaration.parameters)} argument(s), "
                f"received {len(arguments)}.",
                declaration.line,
                declaration.column,
                self.filename,
            )

        if self._call_depth >= self.max_call_depth:
            raise RuntimeError(
                "Maximum function call depth exceeded.",
                declaration.line,
                declaration.column,
                self.filename,
            )

        local = Environment(
            function.closure,
            function_scope=True,
        )

        for parameter, value in zip(
            declaration.parameters,
            arguments,
        ):
            local.define(parameter, value)

        previous_env = self.current_env
        self.current_env = local
        self._call_depth += 1

        try:
            try:
                self._execute_block(declaration.body)

            except _ReturnSignal as signal:
                return signal.value

            return None

        finally:
            self._call_depth -= 1
            self.current_env = previous_env


__all__ = [
    "INTERPRETER_VERSION",
    "RuntimeError",
    "Environment",
    "Interpreter",
]