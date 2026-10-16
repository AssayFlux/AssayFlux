"""
AssayFlux Scientific Systems
Core Regression Tests

Run with:
    python -m unittest discover -s tests -v

Or:
    python -m pytest -v
"""

import contextlib
import io
import unittest

from assayflux.interpreter import (
    AssayFluxRuntimeError,
    Interpreter,
)
from assayflux.lexer import LexerError
from assayflux.parser import ParserError, parse


class AssayFluxTestCase(unittest.TestCase):
    """Shared helpers for AssayFlux tests."""

    def setUp(self):
        self.interpreter = Interpreter()
        self.stdout = io.StringIO()

    def run_program(self, source):
        """Execute a program while capturing printed output."""
        with contextlib.redirect_stdout(self.stdout):
            return self.interpreter.run(source)

    def get_output(self):
        """Return captured terminal output as separate lines."""
        return self.stdout.getvalue().splitlines()


class TestAssayFluxParser(AssayFluxTestCase):
    """Parser and syntax regression tests."""

    def test_parse_simple_program(self):
        program = parse(
            'app "Parser Test"\n'
            'show "Hello"\n'
        )

        self.assertIsNotNone(program)
        self.assertTrue(hasattr(program, "statements"))

    def test_parse_condition_repeat(self):
        program = parse(
            "counter = 0\n"
            "repeat counter < 3\n"
            "    counter = counter + 1\n"
            "end\n"
        )

        self.assertIsNotNone(program)

    def test_parse_counted_repeat(self):
        program = parse(
            "repeat count 3\n"
            '    show "iteration"\n'
            "end\n"
        )

        self.assertIsNotNone(program)

    def test_parse_forever_repeat(self):
        program = parse(
            "repeat forever\n"
            "    stop\n"
            "end\n"
        )

        self.assertIsNotNone(program)

    def test_parse_function(self):
        program = parse(
            "f.add(a, b)\n"
            "    return a + b\n"
            "end\n"
            "show add(2, 3)\n"
        )

        self.assertIsNotNone(program)

    def test_invalid_syntax_raises_parser_error(self):
        with self.assertRaises((ParserError, LexerError)):
            parse(
                "repeat count\n"
                "    show 1\n"
                "end\n"
            )


class TestAssayFluxInterpreter(AssayFluxTestCase):
    """Interpreter execution tests."""

    def test_show_string(self):
        self.run_program('show "Hello, AssayFlux!"')

        self.assertEqual(
            self.get_output(),
            ["Hello, AssayFlux!"],
        )

    def test_arithmetic(self):
        self.run_program(
            "a = 10\n"
            "b = 5\n"
            "show a + b\n"
            "show a * b\n"
            "show a / b\n"
        )

        self.assertEqual(
            self.get_output(),
            ["15", "50", "2.0"],
        )

    def test_boolean_literals(self):
        self.run_program(
            "show true\n"
            "show false\n"
        )

        self.assertEqual(
            self.get_output(),
            ["true", "false"],
        )

    def test_condition_repeat(self):
        self.run_program(
            "counter = 0\n"
            "repeat counter < 3\n"
            "    counter = counter + 1\n"
            "end\n"
            "show counter\n"
        )

        self.assertEqual(self.get_output(), ["3"])

    def test_counted_repeat(self):
        self.run_program(
            "counter = 0\n"
            "repeat count 4\n"
            "    counter = counter + 1\n"
            "end\n"
            "show counter\n"
        )

        self.assertEqual(self.get_output(), ["4"])

    def test_counted_repeat_zero_times(self):
        self.run_program(
            "counter = 10\n"
            "repeat count 0\n"
            "    counter = 99\n"
            "end\n"
            "show counter\n"
        )

        self.assertEqual(self.get_output(), ["10"])

    def test_counted_repeat_rejects_negative_count(self):
        with self.assertRaises(AssayFluxRuntimeError):
            self.run_program(
                "repeat count -1\n"
                "    show 1\n"
                "end\n"
            )

    def test_counted_repeat_rejects_fractional_count(self):
        with self.assertRaises(AssayFluxRuntimeError):
            self.run_program(
                "repeat count 2.5\n"
                "    show 1\n"
                "end\n"
            )

    def test_forever_repeat_stops(self):
        self.run_program(
            "counter = 0\n"
            "repeat forever\n"
            "    counter = counter + 1\n"
            "    if counter >= 3\n"
            "        stop\n"
            "    end\n"
            "end\n"
            "show counter\n"
        )

        self.assertEqual(self.get_output(), ["3"])

    def test_skip_advances_to_next_iteration(self):
        self.run_program(
            "counter = 0\n"
            "total = 0\n"
            "repeat counter < 5\n"
            "    counter = counter + 1\n"
            "    if counter == 3\n"
            "        skip\n"
            "    end\n"
            "    total = total + counter\n"
            "end\n"
            "show total\n"
        )

        self.assertEqual(self.get_output(), ["12"])

    def test_constant_can_be_read(self):
        self.run_program(
            "constant PI = 3.14159\n"
            "show PI\n"
        )

        self.assertEqual(self.get_output(), ["3.14159"])

    def test_constant_cannot_be_reassigned(self):
        with self.assertRaises(AssayFluxRuntimeError):
            self.run_program(
                "constant PI = 3.14\n"
                "PI = 3.14159\n"
            )

    def test_constant_cannot_be_declared_twice(self):
        with self.assertRaises(AssayFluxRuntimeError):
            self.run_program(
                "constant LIMIT = 10\n"
                "constant LIMIT = 20\n"
            )

    def test_undefined_variable_raises_error(self):
        with self.assertRaises(AssayFluxRuntimeError):
            self.run_program("show missing_variable")

    def test_function_returns_value(self):
        self.run_program(
            "f.add(a, b)\n"
            "    return a + b\n"
            "end\n"
            "show add(10, 20)\n"
        )

        self.assertEqual(self.get_output(), ["30"])

    def test_function_without_return(self):
        self.run_program(
            "f.announce()\n"
            '    show "called"\n'
            "end\n"
            "announce()\n"
        )

        self.assertEqual(self.get_output(), ["called"])

    def test_function_argument_count_is_checked(self):
        with self.assertRaises(AssayFluxRuntimeError):
            self.run_program(
                "f.add(a, b)\n"
                "    return a + b\n"
                "end\n"
                "show add(1)\n"
            )

    def test_python_module_import(self):
        self.run_program(
            "import math\n"
            "show math.sqrt(25)\n"
        )

        self.assertEqual(self.get_output(), ["5.0"])

    def test_destroy_stops_program(self):
        self.run_program(
            'show "before"\n'
            "destroy()\n"
            'show "after"\n'
        )

        self.assertTrue(self.interpreter.destroyed)
        self.assertEqual(self.get_output(), ["before"])

    def test_destroy_clears_interpreter_output(self):
        # The output list is the interpreter's internal output buffer.
        # destroy() clears it, including earlier output in that buffer.
        with contextlib.redirect_stdout(self.stdout):
            self.interpreter.run(
                'show "before"\n'
                "destroy()\n"
            )

        self.assertTrue(self.interpreter.destroyed)
        self.assertEqual(self.interpreter.output, [])

    def test_destroy_clears_global_variables(self):
        self.run_program(
            "counter = 42\n"
            "destroy()\n"
        )

        self.assertTrue(self.interpreter.destroyed)
        self.assertEqual(self.interpreter.global_environment.values, {})

    def test_destroyed_interpreter_cannot_run_again(self):
        self.run_program("destroy()")

        with self.assertRaises(AssayFluxRuntimeError):
            self.interpreter.run('show "again"')

    def test_new_interpreter_can_run_after_another_is_destroyed(self):
        self.run_program("destroy()")

        another_interpreter = Interpreter()
        output = io.StringIO()

        with contextlib.redirect_stdout(output):
            another_interpreter.run('show "new instance"')

        self.assertFalse(another_interpreter.destroyed)
        self.assertEqual(
            output.getvalue().splitlines(),
            ["new instance"],
        )

    def test_division_by_zero_raises_runtime_error(self):
        with self.assertRaises(AssayFluxRuntimeError):
            self.run_program("show 1 / 0")


if __name__ == "__main__":
    unittest.main()