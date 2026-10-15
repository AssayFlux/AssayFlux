"""Tests for unified language dispatch."""

import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from assayflux.interop import dispatch
from assayflux.interop.base import ExecutionResult
from assayflux.interop.runtime import execute_code
from assayflux.interpreter import Interpreter


class UnifiedDispatchTests(unittest.TestCase):
    """Test unified dispatch and AssayFlux integration."""

    def test_dispatch_executes_python(self):
        result = dispatch("python", "print(2 + 3)")

        self.assertTrue(result.success)
        self.assertEqual(result.stdout, "5\n")

    def test_dispatch_accepts_case_insensitive_language(self):
        result = dispatch("PYTHON", "print('AssayFlux')")

        self.assertTrue(result.success)
        self.assertEqual(result.stdout, "AssayFlux\n")

    def test_dispatch_unknown_language_raises_error(self):
        with self.assertRaises(KeyError):
            dispatch("unknown_language", "print('test')")

    def test_dispatch_preserves_execution_errors(self):
        result = dispatch("python", "raise ValueError('test error')")

        self.assertFalse(result.success)
        self.assertIn("ValueError", result.stderr)
        self.assertIn("test error", result.stderr)

    def test_dispatch_uses_registered_adapter(self):
        expected = ExecutionResult(
            language="mock",
            stdout="mock output",
            stderr="",
            return_code=0,
        )

        with patch(
            "assayflux.interop.runtime.get_adapter"
        ) as mock_get_adapter:
            mock_adapter = mock_get_adapter.return_value
            mock_adapter.execute.return_value = expected

            result = dispatch("mock", "example code")

        mock_get_adapter.assert_called_once_with("mock")
        mock_adapter.execute.assert_called_once_with(
            "example code",
            timeout=10.0,
        )
        self.assertEqual(result, expected)

    def test_execute_code_remains_compatible(self):
        result = execute_code("python", "print('compatible')")

        self.assertTrue(result.success)
        self.assertEqual(result.stdout, "compatible\n")

    def test_assayflux_program_can_call_dispatch(self):
        interpreter = Interpreter()

        program = '''
result = dispatch("python", "print(2 + 3)")
show result.stdout
'''

        captured = io.StringIO()

        with redirect_stdout(captured):
            interpreter.run(program)

        self.assertEqual(interpreter.output, ["5\n"])
        self.assertEqual(captured.getvalue(), "5\n\n")


if __name__ == "__main__":
    unittest.main()