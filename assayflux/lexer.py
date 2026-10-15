"""Lexer for the AssayFlux programming language."""

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class Token:
    """A single token produced by the lexer."""

    type: str
    value: str
    line: int
    column: int


class LexerError(Exception):
    """Raised when source code contains an invalid token."""


KEYWORDS = {
    "let": "LET",
    "var": "VAR",
    "const": "CONST",
    "print": "PRINT",
    "input": "INPUT",
    "if": "IF",
    "else": "ELSE",
    "while": "WHILE",
    "for": "FOR",
    "in": "IN",
    "function": "FUNCTION",
    "fn": "FUNCTION",
    "return": "RETURN",
    "true": "TRUE",
    "false": "FALSE",
    "and": "AND",
    "or": "OR",
    "not": "NOT",
}


class Lexer:
    """Convert AssayFlux source code into tokens."""

    TWO_CHAR_OPERATORS = {
        "==": "EQ",
        "!=": "NE",
        "<=": "LE",
        ">=": "GE",
        "&&": "AND",
        "||": "OR",
        "->": "ARROW",
        "+=": "PLUS_ASSIGN",
        "-=": "MINUS_ASSIGN",
        "*=": "STAR_ASSIGN",
        "/=": "SLASH_ASSIGN",
    }

    ONE_CHAR_TOKENS = {
        "+": "PLUS",
        "-": "MINUS",
        "*": "STAR",
        "/": "SLASH",
        "%": "PERCENT",
        "=": "ASSIGN",
        "<": "LT",
        ">": "GT",
        "(": "LPAREN",
        ")": "RPAREN",
        "{": "LBRACE",
        "}": "RBRACE",
        "[": "LBRACKET",
        "]": "RBRACKET",
        ",": "COMMA",
        ":": "COLON",
        ";": "SEMICOLON",
        ".": "DOT",
    }

    def __init__(self, source: str):
        self.source = source
        self.position = 0
        self.line = 1
        self.column = 1

    def _peek(self, offset: int = 0) -> str:
        index = self.position + offset
        if index >= len(self.source):
            return ""
        return self.source[index]

    def _advance(self) -> str:
        char = self._peek()

        if char:
            self.position += 1

            if char == "\n":
                self.line += 1
                self.column = 1
            else:
                self.column += 1

        return char

    def _token(
        self,
        token_type: str,
        value: str,
        line: int,
        column: int,
    ) -> Token:
        return Token(token_type, value, line, column)

    def _read_number(self) -> Token:
        line = self.line
        column = self.column
        chars = []

        while self._peek().isdigit():
            chars.append(self._advance())

        if self._peek() == "." and self._peek(1).isdigit():
            chars.append(self._advance())

            while self._peek().isdigit():
                chars.append(self._advance())

        if self._peek() in ("e", "E"):
            exponent_start = self.position
            exponent_line = self.line
            exponent_column = self.column

            chars.append(self._advance())

            if self._peek() in ("+", "-"):
                chars.append(self._advance())

            if not self._peek().isdigit():
                raise LexerError(
                    f"Invalid exponent at "
                    f"{exponent_line}:{exponent_column}"
                )

            while self._peek().isdigit():
                chars.append(self._advance())

        return self._token(
            "NUMBER",
            "".join(chars),
            line,
            column,
        )

    def _read_identifier(self) -> Token:
        line = self.line
        column = self.column
        chars = []

        while (
            self._peek().isalnum()
            or self._peek() == "_"
        ):
            chars.append(self._advance())

        value = "".join(chars)
        token_type = KEYWORDS.get(value, "IDENTIFIER")

        return self._token(token_type, value, line, column)

    def _read_string(self) -> Token:
        quote = self._advance()
        line = self.line
        column = self.column - 1
        chars = []

        while self._peek() and self._peek() != quote:
            char = self._advance()

            if char == "\n":
                raise LexerError(
                    f"Unterminated string at {line}:{column}"
                )

            if char == "\\":
                escaped = self._advance()

                escape_map = {
                    "n": "\n",
                    "t": "\t",
                    "r": "\r",
                    "\\": "\\",
                    "'": "'",
                    '"': '"',
                }

                if not escaped:
                    raise LexerError(
                        f"Unterminated escape at "
                        f"{self.line}:{self.column}"
                    )

                chars.append(escape_map.get(escaped, escaped))
            else:
                chars.append(char)

        if self._peek() != quote:
            raise LexerError(
                f"Unterminated string at {line}:{column}"
            )

        self._advance()

        return self._token(
            "STRING",
            "".join(chars),
            line,
            column,
        )

    def tokenize(self) -> List[Token]:
        tokens = []

        while self._peek():
            char = self._peek()

            if char.isspace():
                self._advance()
                continue

            if char == "#":
                while self._peek() and self._peek() != "\n":
                    self._advance()
                continue

            if (
                char == "/"
                and self._peek(1) == "/"
            ):
                while self._peek() and self._peek() != "\n":
                    self._advance()
                continue

            line = self.line
            column = self.column

            if char.isdigit():
                tokens.append(self._read_number())
                continue

            if char.isalpha() or char == "_":
                tokens.append(self._read_identifier())
                continue

            if char in ("'", '"'):
                tokens.append(self._read_string())
                continue

            pair = char + self._peek(1)

            if pair in self.TWO_CHAR_OPERATORS:
                self._advance()
                self._advance()

                tokens.append(
                    self._token(
                        self.TWO_CHAR_OPERATORS[pair],
                        pair,
                        line,
                        column,
                    )
                )
                continue

            if char in self.ONE_CHAR_TOKENS:
                self._advance()

                tokens.append(
                    self._token(
                        self.ONE_CHAR_TOKENS[char],
                        char,
                        line,
                        column,
                    )
                )
                continue

            raise LexerError(
                f"Unexpected character {char!r} "
                f"at {line}:{column}"
            )

        tokens.append(
            self._token(
                "EOF",
                "",
                self.line,
                self.column,
            )
        )

        return tokens


def tokenize(source: str) -> List[Token]:
    """Tokenize AssayFlux source code."""
    return Lexer(source).tokenize()


def lex(source: str) -> List[Token]:
    """Alias for tokenize()."""
    return tokenize(source)