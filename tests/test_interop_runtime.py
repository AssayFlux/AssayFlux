"""Tests for the AssayFlux interoperability runtime API."""

import unittest

from assayflux.interop.base import ExecutionResult
from assayflux.interop.runtime import execute_code


class TestInteropRuntime(unittest.TestCase):
    """Verify the public language execution API."""

    def test_execute_python_code(self):
        result = execute_code(
            "python",
            "print(10 + 20)",
        )

        self.assertIsInstance(result, ExecutionResult)
        self.assertEqual(result.language, "python")
        self.assertEqual(result.stdout, "30\n")
        self.assertEqual(result.stderr, "")
        self.assertEqual(result.returncode, 0)
        self.assertTrue(result.success)

    def test_language_name_is_case_insensitive(self):
        result = execute_code(
            "PYTHON",
            "print('AssayFlux')",
        )

        self.assertEqual(result.stdout, "AssayFlux\n")
        self.assertTrue(result.success)

    def test_runtime_error_is_returned(self):
        result = execute_code(
            "python",
            "raise ValueError('runtime test error')",
        )

        self.assertFalse(result.success)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("ValueError", result.stderr)
        self.assertIn("runtime test error", result.stderr)

    def test_empty_language_is_rejected(self):
        with self.assertRaises(ValueError):
            execute_code("", "print(1)")

    def test_non_string_language_is_rejected(self):
        with self.assertRaises(ValueError):
            execute_code(None, "print(1)")

    def test_empty_source_is_rejected(self):
        with self.assertRaises(ValueError):
            execute_code("python", "   ")

    def test_non_string_source_is_rejected(self):
        with self.assertRaises(ValueError):
            execute_code("python", None)

    def test_unknown_language_is_rejected(self):
        with self.assertRaises(KeyError):
            execute_code("unsupported-language", "print(1)")

    def test_timeout_is_enforced(self):
        result = execute_code(
            "python",
            "import time\ntime.sleep(5)",
            timeout=0.2,
        )

        self.assertFalse(result.success)
        self.assertEqual(result.returncode, 124)
        self.assertIn("timeout", result.stderr.lower())


if __name__ == "__main__":
    unittest.main()