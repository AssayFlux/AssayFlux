"""
AssayFlux Scientific Systems
Core Tests

Tests the lexer, parser, and interpreter.

Version: 0.1.0
"""

import unittest

from assayflux.lexer import Lexer, LexerError
from assayflux.parser import ParserError, parse
from assayflux.interpreter import Interpreter


class TestAssayFluxLexer(unittest.TestCase):
    """Test AssayFlux tokenization."""

    def test_integer_token(self):
        tokens = Lexer("123").tokenize()
        self.assertEqual(tokens[0].type, "NUMBER")
        self.assertEqual(tokens[0].value, "123")

    def test_single_quoted_string(self):
        tokens = Lexer("'Hello'").tokenize()
        self.assertEqual(tokens[0].type, "STRING")
        self.assertEqual(tokens[0].value, "Hello")

    def test_double_quoted_string(self):
        tokens = Lexer('"Hello"').tokenize()
        self.assertEqual(tokens[0].type, "STRING")
        self.assertEqual(tokens[0].value, "Hello")

    def test_show_keyword(self):
        tokens = Lexer("show").tokenize()
        self.assertEqual(tokens[0].value, "show")
        self.assertEqual(tokens[0].type, "KEYWORD")

    def test_not_equal_operator(self):
        tokens = Lexer("a != b").tokenize()
        operators = [
            token.value
            for token in tokens
            if token.type == "OPERATOR"
        ]
        self.assertEqual(operators, ["!="])

    def test_old_not_equal_operator_is_not_supported(self):
        with self.assertRaises(ParserError):
            parse("show 1 nt= 2")

    def test_indentation_tokens(self):
        source = (
            "if true\n"
            "    show 'yes'\n"
            "end\n"
        )
        tokens = Lexer(source).tokenize()
        token_types = [token.type for token in tokens]

        self.assertIn("INDENT", token_types)
        self.assertIn("DEDENT", token_types)

    def test_two_space_indentation_is_rejected(self):
        source = (
            "if true\n"
            "  show 'yes'\n"
            "end\n"
        )
        with self.assertRaises(LexerError):
            Lexer(source).tokenize()

    def test_indentation_jump_is_rejected(self):
        source = (
            "if true\n"
            "        show 'yes'\n"
            "end\n"
        )
        with self.assertRaises(LexerError):
            Lexer(source).tokenize()

    def test_tab_indentation_is_rejected(self):
        source = (
            "if true\n"
            "\tshow 'yes'\n"
            "end\n"
        )
        with self.assertRaises(LexerError):
            Lexer(source).tokenize()


class TestAssayFluxParser(unittest.TestCase):
    """Test AssayFlux parsing."""

    def test_parse_show_statement(self):
        program = parse("show 123")
        self.assertEqual(len(program.statements), 1)

    def test_parse_assignment(self):
        program = parse("value = 10")
        self.assertEqual(len(program.statements), 1)

    def test_parse_if_statement(self):
        source = (
            "if true\n"
            "    show 'yes'\n"
            "end\n"
        )
        program = parse(source)
        self.assertEqual(len(program.statements), 1)

    def test_parse_if_else_statement(self):
        source = (
            "if true\n"
            "    show 'yes'\n"
            "else\n"
            "    show 'no'\n"
            "end\n"
        )
        program = parse(source)
        self.assertEqual(len(program.statements), 1)

    def test_parse_nested_if_statement(self):
        source = (
            "if true\n"
            "    if true\n"
            "        show 'nested'\n"
            "    end\n"
            "end\n"
        )
        program = parse(source)
        self.assertEqual(len(program.statements), 1)

    def test_missing_end_is_rejected(self):
        source = (
            "if true\n"
            "    show 'yes'\n"
        )
        with self.assertRaises(ParserError):
            parse(source)

    def test_unexpected_end_is_rejected(self):
        with self.assertRaises(ParserError):
            parse("end\n")

    def test_parse_not_equal_expression(self):
        program = parse("show 1 != 2")
        self.assertEqual(len(program.statements), 1)


class TestAssayFluxInterpreter(unittest.TestCase):
    """Test AssayFlux execution."""

    def run_program(self, source):
        interpreter = Interpreter()
        return interpreter.run(source)

    def test_show_single_quoted_string(self):
        result = self.run_program("show 'Hello AssayFlux'")
        self.assertEqual(result, "Hello AssayFlux")

    def test_show_double_quoted_string(self):
        result = self.run_program('show "Hello AssayFlux"')
        self.assertEqual(result, "Hello AssayFlux")

    def test_assignment_and_show(self):
        source = (
            "value = 10\n"
            "show value\n"
        )
        result = self.run_program(source)
        self.assertEqual(result, 10)

    def test_arithmetic(self):
        result = self.run_program("show 2 + 3")
        self.assertEqual(result, 5)

    def test_boolean_condition(self):
        source = (
            "if true\n"
            "    show 'passed'\n"
            "end\n"
        )
        result = self.run_program(source)
        self.assertEqual(result, "passed")


if __name__ == "__main__":
    unittest.main()