import unittest

from assayflux.lexer import Lexer, LexError


class TestAssayFluxLexerPhase1(unittest.TestCase):

    def token_pairs(self, source):
        """Return token type/value pairs, excluding EOF."""
        tokens = Lexer(source).tokenize()

        return [
            (token.type, token.value)
            for token in tokens
            if token.type != "EOF"
        ]

    def test_arithmetic_and_matrix_operators(self):
        source = "show a + b * c @ d"

        tokens = self.token_pairs(source)
        operators = [
            value
            for token_type, value in tokens
            if token_type == "OPERATOR"
        ]

        self.assertEqual(
            operators,
            ["+", "*", "@"],
        )

    def test_bitwise_operators(self):
        source = "show a & b | c ^ d << 2 >> 1"

        tokens = self.token_pairs(source)
        operators = [
            value
            for token_type, value in tokens
            if token_type == "OPERATOR"
        ]

        self.assertEqual(
            operators,
            ["&", "|", "^", "<<", ">>"],
        )

    def test_unary_bitwise_inversion(self):
        tokens = self.token_pairs("show ~value")

        self.assertIn(
            ("OPERATOR", "~"),
            tokens,
        )

    def test_augmented_assignments(self):
        source = """
a += 1
b -= 1
c *= 2
d /= 2
e //= 2
f %= 3
g **= 2
h @= matrix
i &= mask
j |= mask
k ^= mask
m <<= 1
n >>= 1
"""

        tokens = self.token_pairs(source)

        expected = [
            "+=",
            "-=",
            "*=",
            "/=",
            "//=",
            "%=",
            "**=",
            "@=",
            "&=",
            "|=",
            "^=",
            "<<=",
            ">>=",
        ]

        actual = [
            value
            for token_type, value in tokens
            if token_type == "OPERATOR"
        ]

        self.assertEqual(actual, expected)

    def test_membership_and_identity_keywords(self):
        source = """
show a in values
show a is b
show a not in values
show a is not b
"""

        tokens = self.token_pairs(source)

        keyword_values = [
            value
            for token_type, value in tokens
            if token_type == "KEYWORD"
        ]

        self.assertIn("in", keyword_values)
        self.assertIn("is", keyword_values)
        self.assertIn("not", keyword_values)

    def test_walrus_operator(self):
        tokens = self.token_pairs("show (value := 10)")

        self.assertIn(
            ("OPERATOR", ":="),
            tokens,
        )

    def test_arrow_operator(self):
        tokens = self.token_pairs("result -> value")

        self.assertIn(
            ("OPERATOR", "->"),
            tokens,
        )

    def test_semicolon_is_recognized(self):
        tokens = self.token_pairs("a = 1; show a")

        self.assertIn(
            ("DELIMITER", ";"),
            tokens,
        )

    def test_longest_operator_match(self):
        source = "a **= 2; b //= 3; c <<= 1"

        tokens = self.token_pairs(source)

        operators = [
            value
            for token_type, value in tokens
            if token_type == "OPERATOR"
        ]

        self.assertEqual(
            operators,
            ["**=", "//=", "<<="],
        )

    def test_explicit_continuation_does_not_indent(self):
        source = "show 10 + \\\n    20\n"

        tokens = self.token_pairs(source)

        token_types = [
            token_type
            for token_type, value in tokens
        ]

        self.assertNotIn("INDENT", token_types)
        self.assertNotIn("DEDENT", token_types)

        number_values = [
            value
            for token_type, value in tokens
            if token_type == "NUMBER"
        ]

        self.assertEqual(number_values, ["10", "20"])

    def test_indentation_still_works_for_blocks(self):
        source = (
            "if true:\n"
            "    show 10\n"
            "end\n"
        )

        tokens = self.token_pairs(source)

        token_types = [
            token_type
            for token_type, value in tokens
        ]

        self.assertIn("INDENT", token_types)
        self.assertIn("DEDENT", token_types)

    def test_unexpected_character_raises_lex_error(self):
        with self.assertRaises(LexError):
            Lexer("show $").tokenize()


if __name__ == "__main__":
    unittest.main()