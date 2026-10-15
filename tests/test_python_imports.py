"""Tests for importing Python libraries into AssayFlux."""

import importlib
import unittest

from assayflux.interpreter import Interpreter


class PythonImportTests(unittest.TestCase):
    """Test Python module imports and function calls in AssayFlux."""

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

    def test_call_qualified_python_function(self):
        """Call a function through an imported Python module."""
        interpreter = Interpreter()

        interpreter.run(
            "import math\n"
            "result = math.sqrt(25)\n"
        )

        self.assertEqual(
            interpreter.global_environment.get("result"),
            5.0,
        )

    def test_call_python_function_using_module_alias(self):
        """Call a Python function through an imported module alias."""
        interpreter = Interpreter()

        interpreter.run(
            "import math as mathematics\n"
            "result = mathematics.sqrt(36)\n"
        )

        self.assertEqual(
            interpreter.global_environment.get("result"),
            6.0,
        )

    def test_call_python_function_with_show(self):
        """Evaluate a qualified Python function inside show."""
        interpreter = Interpreter()

        interpreter.run(
            "import math\n"
            "show math.sqrt(49)\n"
        )

        self.assertEqual(
            interpreter.global_environment.get("math").sqrt(49),
            7.0,
        )


if __name__ == "__main__":
    unittest.main()