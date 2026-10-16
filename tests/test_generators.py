import unittest
from assayflux.generator.python_generator import PythonGenerator
from assayflux.generator.js_generator import JSGenerator
from assayflux.generator.sql_generator import SQLGenerator
from assayflux.generator.html_generator import HTMLGenerator
from assayflux.generator.css_generator import CSSGenerator


class TestAssayFluxGenerators(unittest.TestCase):

    def test_python_generator_stub(self):
        gen = PythonGenerator(ast=None)
        self.assertIsInstance(gen.generate(), str)

    def test_js_generator_stub(self):
        gen = JSGenerator(ast=None)
        self.assertIsInstance(gen.generate(), str)

    def test_sql_generator_safety(self):
        gen = SQLGenerator(ast=None)
        self.assertEqual(gen.escape_identifier("valid_table"), '"valid_table"')
        self.assertEqual(gen.sanitize_value(42), "42")

    def test_html_generator_stub(self):
        gen = HTMLGenerator(ast=None)
        self.assertIsInstance(gen.generate(), str)

    def test_css_generator_stub(self):
        gen = CSSGenerator(ast=None)
        self.assertIsInstance(gen.generate(), str)


if __name__ == "__main__":
    unittest.main()
