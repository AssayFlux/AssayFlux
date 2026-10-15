"""Tests for unified language dispatch in AssayFlux."""

import unittest
from unittest.mock import patch

from assayflux.interop import dispatch
from assayflux.interop.base import ExecutionResult
from assayflux.interop.runtime import execute_code


class TestUnifiedDispatch(unittest.TestCase):
    """Verify the unified execution interface."""

    def test_python_dispatch_returns_execution_result(self):
        result = dispatch("python", "print(10 + 20)")

        self.assertIsInstance(result, ExecutionResult)
        self.assertEqual(result.language, "python")
        self.assertEqual(result.stdout, "30\n")
        self.assertEqual(result.stderr, "")
        self.assertEqual(result.returncode, 0)
        self.assertTrue(result.success)

    def test_dispatch_accepts_case_insensitive_language_names(self):
        result = dispatch("PYTHON", "print('AssayFlux')")

        self.assertEqual(result.stdout, "AssayFlux\n")
        self.assertTrue(result.success)

    def test_dispatch_rejects_unknown_language(self):
        with self.assertRaises(KeyError):
            dispatch("unknown_assayflux_language", "print(1)")

    def test_dispatch_preserves_execution_errors(self):
        result = dispatch(
            "python",
            "raise ValueError('dispatch test error')",
        )

        self.assertFalse(result.success)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("ValueError", result.stderr)
        self.assertIn("dispatch test error", result.stderr)

    def test_dispatch_uses_registered_adapter(self):
        fake_result = ExecutionResult(
            language="python",
            stdout="42\n",
            stderr="",
            returncode=0,
        )

        with patch(
            "assayflux.interop.runtime.get_adapter"
        ) as mocked_get_adapter:
            mocked_adapter = mocked_get_adapter.return_value
            mocked_adapter.execute.return_value = fake_result

            result = dispatch("python", "print(42)")

        mocked_get_adapter.assert_called_once_with("python")
        mocked_adapter.execute.assert_called_once_with(
            "print(42)",
            timeout=10.0,
        )
        self.assertEqual(result.stdout, "42\n")
        self.assertTrue(result.success)

    def test_execute_code_remains_compatible(self):
        result = execute_code("python", "print('compatible')")

        self.assertEqual(result.stdout, "compatible\n")
        self.assertTrue(result.success)


if __name__ == "__main__":
    unittest.main()