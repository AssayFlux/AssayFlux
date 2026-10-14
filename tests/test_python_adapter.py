"""Automated tests for the AssayFlux Python adapter."""

import sys
import unittest

from assayflux.interop.base import ExecutionResult
from assayflux.interop.adapters.python_adapter import PythonAdapter


class TestPythonAdapter(unittest.TestCase):
    """Verify Python adapter behavior."""

    def setUp(self):
        self.adapter = PythonAdapter()

    def test_language_identifier(self):
        self.assertEqual(self.adapter.language, "python")

    def test_runtime_is_available(self):
        self.assertTrue(self.adapter.is_available())

    def test_successful_execution(self):
        result = self.adapter.execute("print(10 + 20)")

        self.assertIsInstance(result, ExecutionResult)
        self.assertEqual(result.language, "python")
        self.assertEqual(result.stdout, "30\n")
        self.assertEqual(result.stderr, "")
        self.assertEqual(result.returncode, 0)
        self.assertTrue(result.success)

    def test_multiple_output_lines(self):
        result = self.adapter.execute(
            "print('AssayFlux')\nprint('Python integration')"
        )

        self.assertEqual(
            result.stdout,
            "AssayFlux\nPython integration\n",
        )
        self.assertTrue(result.success)

    def test_runtime_error(self):
        result = self.adapter.execute(
            "raise ValueError('intentional test error')"
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(result.success)
        self.assertIn("ValueError", result.stderr)
        self.assertIn("intentional test error", result.stderr)

    def test_invalid_source_type(self):
        with self.assertRaises(ValueError):
            self.adapter.execute(None)

    def test_empty_source(self):
        with self.assertRaises(ValueError):
            self.adapter.execute("   ")

    def test_invalid_timeout_type(self):
        for timeout in ("10", None, True):
            with self.subTest(timeout=timeout):
                with self.assertRaises(ValueError):
                    self.adapter.execute("print('test')", timeout=timeout)

    def test_invalid_timeout_value(self):
        for timeout in (0, -1, float("inf"), float("-inf"), float("nan")):
            with self.subTest(timeout=timeout):
                with self.assertRaises(ValueError):
                    self.adapter.execute("print('test')", timeout=timeout)

    def test_execution_timeout(self):
        result = self.adapter.execute(
            "import time\ntime.sleep(5)",
            timeout=0.2,
        )

        self.assertEqual(result.language, "python")
        self.assertEqual(result.returncode, 124)
        self.assertFalse(result.success)
        self.assertIn("timeout", result.stderr.lower())

    def test_current_python_executable_is_used(self):
        result = self.adapter.execute(
            "import sys\nprint(sys.executable)"
        )

        self.assertTrue(result.success)
        self.assertEqual(result.stdout.strip(), sys.executable)


if __name__ == "__main__":
    unittest.main()