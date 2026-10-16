"""
AssayFlux Scientific Systems
Master Test Suite

Tests:
    Package imports
    Lexer and tokenization
    Parser and AST generation
    Interpreter execution
    Variables and constants
    Arithmetic and comparisons
    Boolean logic
    Conditional statements
    Functions and return values
    Loops and control flow
    Syntax errors
    Runtime errors
    Language adapter registration
    Language aliases
    Runtime availability
    Python interoperability
    SQL interoperability
    HTML and CSS adapters
    Execution result contracts

Run:
    python -m unittest discover -s tests -v

Or:
    pytest -v
"""

import importlib
import unittest


# ============================================================
# Core imports
# ============================================================

from assayflux.lexer import Lexer
from assayflux.parser import Parser
from assayflux.interpreter import Interpreter

from assayflux.interop.adapters.master_adapter import MasterAdapter
from assayflux.interop.loader import (
    available_languages,
    get_adapter,
    normalize_language,
)
from assayflux.interop.runtime import (
    dispatch,
    execute_code,
)


# ============================================================
# Test helpers
# ============================================================

class AssayFluxTestCase(unittest.TestCase):
    """Shared helpers for the master test suite."""

    def execute_assayflux(self, source):
        """
        Run AssayFlux source and return the interpreter
        so tests can inspect its output and environment.
        """
        interpreter = Interpreter()
        interpreter.run(source)
        return interpreter

    def get_variable(self, interpreter, name):
        """Retrieve a variable from the global environment."""
        return interpreter.global_environment.get(name)

    def assert_interpreter_runs(self, source):
        """Assert that a program executes without an exception."""
        interpreter = Interpreter()
        interpreter.run(source)
        return interpreter


# ============================================================
# Package and module integrity
# ============================================================

class TestPackageIntegrity(AssayFluxTestCase):

    def test_package_imports(self):
        modules = [
            "assayflux",
            "assayflux.lexer",
            "assayflux.parser",
            "assayflux.ast_nodes",
            "assayflux.interpreter",
            "assayflux.interop",
            "assayflux.interop.base",
            "assayflux.interop.loader",
            "assayflux.interop.registry",
            "assayflux.interop.runtime",
            "assayflux.interop.adapters.master_adapter",
            "assayflux.interop.adapters.universal_adapter",
        ]

        for module_name in modules:
            with self.subTest(module=module_name):
                module = importlib.import_module(module_name)
                self.assertIsNotNone(module)

    def test_interpreter_can_be_created(self):
        interpreter = Interpreter()
        self.assertIsNotNone(interpreter)

    def test_master_adapter_can_be_created(self):
        adapter = MasterAdapter("python")
        self.assertEqual(adapter.language, "python")


# ============================================================
# Lexer
# ============================================================

class TestLexer(AssayFluxTestCase):

    def tokenize(self, source):
        return Lexer(source).tokenize()

    def test_integer_literal(self):
        tokens = self.tokenize("42")
        self.assertEqual(tokens[0].value, "42")

    def test_decimal_literal(self):
        tokens = self.tokenize("3.14")
        self.assertEqual(tokens[0].value, "3.14")

    def test_identifier(self):
        tokens = self.tokenize("result")
        self.assertEqual(tokens[0].value, "result")

    def test_addition_operator(self):
        tokens = self.tokenize("2 + 3")
        values = [token.value for token in tokens]
        self.assertIn("+", values)

    def test_comparison_operators(self):
        tokens = self.tokenize("a == b")
        values = [token.value for token in tokens]
        self.assertIn("==", values)

    def test_not_equal_operator(self):
        tokens = self.tokenize("a != b")
        values = [token.value for token in tokens]
        self.assertIn("!=", values)

    def test_string_literal(self):
        tokens = self.tokenize('show "AssayFlux"')
        values = [token.value for token in tokens]
        self.assertIn("AssayFlux", values)

    def test_single_quoted_string(self):
        tokens = self.tokenize("show 'AssayFlux'")
        values = [token.value for token in tokens]
        self.assertIn("AssayFlux", values)

    def test_custom_keywords(self):
        source = (
            "constant VALUE = 10\n"
            "show VALUE\n"
        )

        tokens = self.tokenize(source)
        values = [token.value for token in tokens]

        for keyword in ("constant", "show"):
            with self.subTest(keyword=keyword):
                self.assertIn(keyword, values)

    def test_indentation_tokens(self):
        source = (
            "if true:\n"
            "    show 1\n"
            "end\n"
        )

        tokens = self.tokenize(source)
        token_types = [token.type for token in tokens]

        self.assertIn("INDENT", token_types)
        self.assertIn("DEDENT", token_types)

    def test_end_of_file_token(self):
        tokens = self.tokenize("show 1")
        self.assertEqual(tokens[-1].type, "EOF")


# ============================================================
# Parser
# ============================================================

class TestParser(AssayFluxTestCase):

    def parse_source(self, source):
        tokens = Lexer(source).tokenize()
        return Parser(tokens).parse()

    def test_simple_program(self):
        program = self.parse_source("show 10")
        self.assertIsNotNone(program)

    def test_variable_assignment(self):
        program = self.parse_source("result = 10")
        self.assertIsNotNone(program)

    def test_constant_declaration(self):
        program = self.parse_source(
            "constant BASE = 10"
        )
        self.assertIsNotNone(program)

    def test_arithmetic_expression(self):
        program = self.parse_source(
            "result = 2 + 3 * 4"
        )
        self.assertIsNotNone(program)

    def test_conditional_statement(self):
        source = (
            "if true:\n"
            "    show 1\n"
            "end\n"
        )

        program = self.parse_source(source)
        self.assertIsNotNone(program)

    def test_otherwise_statement(self):
        source = (
            "if false:\n"
            "    show 1\n"
            "otherwise true:\n"
            "    show 2\n"
            "else:\n"
            "    show 3\n"
            "end\n"
        )

        program = self.parse_source(source)
        self.assertIsNotNone(program)

    def test_function_definition(self):
        source = (
            "f.add(a, b):\n"
            "    return a + b\n"
            "end\n"
        )

        program = self.parse_source(source)
        self.assertIsNotNone(program)

    def test_repeat_statement(self):
        source = (
            "repeat 3:\n"
            "    show 1\n"
            "end\n"
        )

        program = self.parse_source(source)
        self.assertIsNotNone(program)


# ============================================================
# Interpreter: variables and values
# ============================================================

class TestInterpreterValues(AssayFluxTestCase):

    def test_integer_variable(self):
        interpreter = self.execute_assayflux(
            "answer = 42"
        )

        self.assertEqual(
            self.get_variable(interpreter, "answer"),
            42,
        )

    def test_decimal_variable(self):
        interpreter = self.execute_assayflux(
            "answer = 3.5"
        )

        self.assertEqual(
            self.get_variable(interpreter, "answer"),
            3.5,
        )

    def test_string_variable(self):
        interpreter = self.execute_assayflux(
            'message = "AssayFlux"'
        )

        self.assertEqual(
            self.get_variable(interpreter, "message"),
            "AssayFlux",
        )

    def test_boolean_true(self):
        interpreter = self.execute_assayflux(
            "result = true"
        )

        self.assertIs(
            self.get_variable(interpreter, "result"),
            True,
        )

    def test_boolean_false(self):
        interpreter = self.execute_assayflux(
            "result = false"
        )

        self.assertIs(
            self.get_variable(interpreter, "result"),
            False,
        )

    def test_arithmetic_result_remains_numeric(self):
        interpreter = self.execute_assayflux(
            "result = 10 + 5"
        )

        result = self.get_variable(
            interpreter,
            "result",
        )

        self.assertEqual(result, 15)
        self.assertIsInstance(result, int)

    def test_constant_declaration(self):
        interpreter = self.execute_assayflux(
            "constant BASE = 100"
        )

        self.assertEqual(
            self.get_variable(interpreter, "BASE"),
            100,
        )


# ============================================================
# Interpreter: operators
# ============================================================

class TestInterpreterOperators(AssayFluxTestCase):

    def test_addition(self):
        interpreter = self.execute_assayflux(
            "result = 10 + 5"
        )
        self.assertEqual(
            self.get_variable(interpreter, "result"),
            15,
        )

    def test_subtraction(self):
        interpreter = self.execute_assayflux(
            "result = 10 - 5"
        )
        self.assertEqual(
            self.get_variable(interpreter, "result"),
            5,
        )

    def test_multiplication(self):
        interpreter = self.execute_assayflux(
            "result = 10 * 5"
        )
        self.assertEqual(
            self.get_variable(interpreter, "result"),
            50,
        )

    def test_division(self):
        interpreter = self.execute_assayflux(
            "result = 10 / 2"
        )
        self.assertEqual(
            self.get_variable(interpreter, "result"),
            5,
        )

    def test_remainder(self):
        interpreter = self.execute_assayflux(
            "result = 10 % 3"
        )
        self.assertEqual(
            self.get_variable(interpreter, "result"),
            1,
        )

    def test_exponentiation(self):
        interpreter = self.execute_assayflux(
            "result = 2 ** 3"
        )
        self.assertEqual(
            self.get_variable(interpreter, "result"),
            8,
        )

    def test_comparison(self):
        interpreter = self.execute_assayflux(
            "result = 10 > 5"
        )
        self.assertIs(
            self.get_variable(interpreter, "result"),
            True,
        )

    def test_not_equal(self):
        interpreter = self.execute_assayflux(
            "result = 10 != 5"
        )
        self.assertIs(
            self.get_variable(interpreter, "result"),
            True,
        )

    def test_logical_and(self):
        interpreter = self.execute_assayflux(
            "result = true and true"
        )
        self.assertIs(
            self.get_variable(interpreter, "result"),
            True,
        )

    def test_logical_or(self):
        interpreter = self.execute_assayflux(
            "result = false or true"
        )
        self.assertIs(
            self.get_variable(interpreter, "result"),
            True,
        )


# ============================================================
# Interpreter: control flow
# ============================================================

class TestInterpreterControlFlow(AssayFluxTestCase):

    def test_if_true(self):
        interpreter = self.execute_assayflux(
            "result = 0\n"
            "if true:\n"
            "    result = 10\n"
            "end\n"
        )

        self.assertEqual(
            self.get_variable(interpreter, "result"),
            10,
        )

    def test_if_false(self):
        interpreter = self.execute_assayflux(
            "result = 0\n"
            "if false:\n"
            "    result = 10\n"
            "end\n"
        )

        self.assertEqual(
            self.get_variable(interpreter, "result"),
            0,
        )

    def test_otherwise_branch(self):
        interpreter = self.execute_assayflux(
            "result = 0\n"
            "if false:\n"
            "    result = 1\n"
            "otherwise true:\n"
            "    result = 2\n"
            "else:\n"
            "    result = 3\n"
            "end\n"
        )

        self.assertEqual(
            self.get_variable(interpreter, "result"),
            2,
        )

    def test_else_branch(self):
        interpreter = self.execute_assayflux(
            "result = 0\n"
            "if false:\n"
            "    result = 1\n"
            "else:\n"
            "    result = 3\n"
            "end\n"
        )

        self.assertEqual(
            self.get_variable(interpreter, "result"),
            3,
        )

    def test_repeat_count(self):
        interpreter = self.execute_assayflux(
            "count = 0\n"
            "repeat 5:\n"
            "    count = count + 1\n"
            "end\n"
        )

        self.assertEqual(
            self.get_variable(interpreter, "count"),
            5,
        )

    def test_function_call(self):
        interpreter = self.execute_assayflux(
            "f.add(a, b):\n"
            "    return a + b\n"
            "end\n"
            "result = add(10, 20)\n"
        )

        self.assertEqual(
            self.get_variable(interpreter, "result"),
            30,
        )


# ============================================================
# Interpreter: errors
# ============================================================

class TestInterpreterErrors(AssayFluxTestCase):

    def test_invalid_syntax_is_rejected(self):
        with self.assertRaises(Exception):
            Interpreter().run(
                "if true:\n"
                "    show 1\n"
            )

    def test_undefined_variable_is_rejected(self):
        with self.assertRaises(Exception):
            Interpreter().run(
                "show variable_that_does_not_exist"
            )

    def test_division_by_zero_is_rejected(self):
        with self.assertRaises(Exception):
            Interpreter().run(
                "result = 1 / 0"
            )

    def test_invalid_repeat_count_is_rejected(self):
        with self.assertRaises(Exception):
            Interpreter().run(
                "repeat -1:\n"
                "    show 1\n"
                "end\n"
            )


# ============================================================
# Language adapter coverage
# ============================================================

class TestLanguageAdapters(AssayFluxTestCase):

    EXPECTED_LANGUAGES = {
        "bash",
        "c",
        "cpp",
        "csharp",
        "cobol",
        "crystal",
        "d",
        "dart",
        "elixir",
        "erlang",
        "fortran",
        "fsharp",
        "go",
        "haskell",
        "java",
        "javascript",
        "julia",
        "kotlin",
        "lua",
        "nim",
        "ocaml",
        "perl",
        "php",
        "python",
        "r",
        "ruby",
        "rust",
        "scala",
        "sql",
        "swift",
        "typescript",
        "zig",
        "html",
        "css",
    }

    def test_all_expected_languages_are_declared(self):
        declared = set(
            MasterAdapter.registered_languages()
        )

        self.assertEqual(
            declared,
            self.EXPECTED_LANGUAGES,
            "The adapter language inventory has changed.",
        )

    def test_every_language_can_be_instantiated(self):
        for language in sorted(self.EXPECTED_LANGUAGES):
            with self.subTest(language=language):
                adapter = get_adapter(language)

                self.assertEqual(
                    adapter.language,
                    language,
                )

    def test_every_language_has_availability_check(self):
        for language in sorted(self.EXPECTED_LANGUAGES):
            with self.subTest(language=language):
                adapter = get_adapter(language)

                available = adapter.is_available()

                self.assertIsInstance(available, bool)

    def test_aliases(self):
        aliases = {
            "py": "python",
            "js": "javascript",
            "node": "javascript",
            "rb": "ruby",
            "c++": "cpp",
            "c#": "csharp",
            "rs": "rust",
            "sh": "bash",
            "shell": "bash",
            "sqlite": "sql",
            "ts": "typescript",
        }

        for alias, expected in aliases.items():
            with self.subTest(alias=alias):
                self.assertEqual(
                    normalize_language(alias),
                    expected,
                )

    def test_unknown_language_is_rejected(self):
        with self.assertRaises(KeyError):
            get_adapter("this_language_does_not_exist")

    def test_available_languages_are_supported(self):
        available = set(available_languages())

        self.assertTrue(
            available.issubset(self.EXPECTED_LANGUAGES)
        )

    def test_python_adapter_executes_code(self):
        result = dispatch(
            "python",
            'print("ASSAYFLUX_MASTER_TEST")',
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn(
            "ASSAYFLUX_MASTER_TEST",
            result.stdout,
        )

    def test_python_alias_executes_code(self):
        result = dispatch(
            "py",
            "print(2 + 3)",
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn("5", result.stdout)

    def test_execute_code_matches_dispatch(self):
        result = execute_code(
            "python",
            "print(7 * 6)",
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn("42", result.stdout)

    def test_execution_result_contract(self):
        result = dispatch(
            "python",
            "print('ok')",
        )

        self.assertEqual(result.language, "python")
        self.assertIsInstance(result.stdout, str)
        self.assertIsInstance(result.stderr, str)
        self.assertIsInstance(result.returncode, int)
        self.assertIsInstance(result.duration, (int, float))
        self.assertGreaterEqual(result.duration, 0)


# ============================================================
# SQL adapter
# ============================================================

class TestSQLAdapter(AssayFluxTestCase):

    def test_sql_adapter_is_registered(self):
        adapter = get_adapter("sql")
        self.assertEqual(adapter.language, "sql")

    def test_sql_availability_check(self):
        adapter = get_adapter("sql")
        self.assertIsInstance(adapter.is_available(), bool)

    def test_sql_execution(self):
        adapter = get_adapter("sql")

        if not adapter.is_available():
            self.skipTest("SQLite is unavailable.")

        result = adapter.execute(
            "SELECT 2 + 3;"
        )

        self.assertEqual(
            result.returncode,
            0,
            result.stderr,
        )

        self.assertIn("5", result.stdout)


# ============================================================
# HTML and CSS adapters
# ============================================================

class TestStaticAssetAdapters(AssayFluxTestCase):

    def test_html_adapter_is_is_registered(self):
        adapter = get_adapter("html")
        self.assertEqual(adapter.language, "html")

    def test_css_adapter_is_registered(self):
        adapter = get_adapter("css")
        self.assertEqual(adapter.language, "css")

    def test_html_adapter_is_available(self):
        self.assertTrue(
            get_adapter("html").is_available()
        )

    def test_css_adapter_is_available(self):
        self.assertTrue(
            get_adapter("css").is_available()
        )


# ============================================================
# Invalid API arguments
# ============================================================

class TestInteropValidation(AssayFluxTestCase):

    def test_non_string_language_is_rejected(self):
        with self.assertRaises(TypeError):
            dispatch(None, "print(1)")

    def test_non_string_source_is_rejected(self):
        with self.assertRaises(TypeError):
            dispatch("python", None)

    def test_zero_timeout_is_rejected(self):
        with self.assertRaises(ValueError):
            dispatch("python", "print(1)", timeout=0)

    def test_negative_timeout_is_rejected(self):
        with self.assertRaises(ValueError):
            dispatch("python", "print(1)", timeout=-1)

    def test_infinite_timeout_is_rejected(self):
        with self.assertRaises(ValueError):
            dispatch("python", "print(1)", timeout=float("inf"))

    def test_boolean_timeout_is_rejected(self):
        with self.assertRaises(TypeError):
            dispatch("python", "print(1)", timeout=True)


# ============================================================
# Test entry point
# ============================================================

if __name__ == "__main__":
    unittest.main(verbosity=2)