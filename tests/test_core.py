import unittest

from assayflux.lexer import Lexer
from assayflux.parser import parse
from assayflux.interpreter import Interpreter


class TestAssayFluxLexer(unittest.TestCase):
    def test_integer_token(self):
        tokens = Lexer("123").tokenize()
        self.assertEqual(tokens[0].value, "123")

    def test_string_token(self):
        tokens = Lexer("`Hello`").tokenize()
        self.assertEqual(tokens[0].value, "Hello")

    def test_show_keyword(self):
        tokens = Lexer("show").tokenize()
        self.assertEqual(tokens[0].value, "show")


class TestAssayFluxParser(unittest.TestCase):
    def test_parse_show_statement(self):
        program = parse("show 123")
        self.assertEqual(len(program.statements), 1)

    def test_parse_assignment(self):
        program = parse("value = 10")
        self.assertEqual(len(program.statements), 1)

    def test_parse_if_statement(self):
        source = "if true\nshow `yes`\nend"
        program = parse(source)
        self.assertEqual(len(program.statements), 1)


class TestAssayFluxInterpreter(unittest.TestCase):
    def run_program(self, source):
        interpreter = Interpreter()
        return interpreter.run(source)

    def test_show_string(self):
        result = self.run_program("show `Hello AssayFlux`")
        self.assertEqual(result, "Hello AssayFlux")

    def test_assignment_and_show(self):
        source = "value = 10\nshow value"
        result = self.run_program(source)
        self.assertEqual(result, 10)

    def test_arithmetic(self):
        result = self.run_program("show 2 + 3")
        self.assertEqual(result, 5)

    def test_boolean_condition(self):
        source = "if true\nshow `passed`\nend"
        result = self.run_program(source)
        self.assertEqual(result, "passed")


if __name__ == "__main__":
    unittest.main()
