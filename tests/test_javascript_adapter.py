"""Tests for the AssayFlux JavaScript adapter."""

import unittest

from assayflux.interop.loader import get_adapter


class TestJavaScriptAdapter(unittest.TestCase):
    """Verify JavaScript adapter execution."""

    def setUp(self):
        self.adapter = get_adapter("javascript")

    def test_javascript_adapter_is_registered(self):
        self.assertEqual(self.adapter.language, "javascript")

    def test_javascript_adapter_implements_execution_interface(self):
        self.assertTrue(callable(self.adapter.is_available))
        self.assertTrue(callable(self.adapter.execute))

    def test_javascript_runtime_availability(self):
        self.assertIsInstance(self.adapter.is_available(), bool)

    def test_execute_javascript(self):
        if not self.adapter.is_available():
            self.skipTest("JavaScript runtime is not installed.")

        source = 'console.log("Hello from AssayFlux JavaScript");'

        result = self.adapter.execute(source)

        self.assertTrue(
            result.success,
            msg=f"JavaScript execution failed: {result.stderr}",
        )
        self.assertIn(
            "Hello from AssayFlux JavaScript",
            result.stdout,
        )

    def test_javascript_syntax_error_returns_failure(self):
        if not self.adapter.is_available():
            self.skipTest("JavaScript runtime is not installed.")

        result = self.adapter.execute("const = ;")

        self.assertFalse(result.success)
        self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()