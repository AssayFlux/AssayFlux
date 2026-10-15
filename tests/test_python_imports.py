"""Tests for importing Python libraries into AssayFlux."""

import importlib
import unittest

from assayflux.interpreter import Interpreter


class PythonImportTests(unittest.TestCase):
    """Test Python module imports in AssayFlux programs."""

    def test_import_python_module(self):
        """Import a Python module using its original name."""
        interpreter = Interpreter()

        interpreter.run("import math")

        imported_module = interpreter.global_environment.get("math")

        self.assertIs(imported_module, importlib.import_module("math"))

    def test_import_python_module_with_alias(self):
        """Import a Python module using an alias."""
        interpreter = Interpreter()

        interpreter.run("import math as mathematics")

        imported_module = interpreter.global_environment.get(
            "mathematics"
        )

        self.assertIs(imported_module, importlib.import_module("math"))

    def test_import_missing_module_raises_error(self):
        """A missing Python module should produce a clear error."""
        interpreter = Interpreter()

        with self.assertRaises(Exception):
            interpreter.run("import assayflux_module_that_does_not_exist")


if __name__ == "__main__":
    unittest.main()