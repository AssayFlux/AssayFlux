"""
AssayFlux Scientific Systems
Initial Lexer Implementation

The lexer converts AssayFlux source code into tokens.

Version: 0.1.0
"""

from dataclasses import dataclass
from typing import List


KEYWORDS = {
    "show",
    "if",
    "otherwise",
    "else",
    "end",
    "repeat",
    "stop",
    "skip",
    "return",
    "and",
    "or",
    "not",
    "true",
    "false",
    "import",
    "as",
    "const",
}


OPERATORS = [
    "nt=",
    "==",
    ">=",
    "<=",
    "+",
    "-",
    "*",
    "/",
    "%",
    "=",
    ">",
    "<",
]


PUNCTUATION = {
    "(": "LEFT_PAREN",
    ")": "RIGHT_PAREN",
    ",": "COMMA",
    ".": "DOT",
}


@dataclass(frozen=True)
class Token:
    """Represents one token in AssayFlux source code."""

    type: str
    value: str
    line: int
    column: int

    def __repr__(self) -> str:
        return (
            f"Token(type={self.type!r}, "
            f"value={self.value!r}, "
            f"line={self.line}, "
            f"column={self.column})"
        )


class LexerError(Exception):
    """Raised when invalid source text is encountered."""

    def __init__(
        self,
        message: str,
        line: int,
        column: int,
    ):
        self.message = message
        self.line = line
        self.column = column

        super().__init__(
            f"AssayFlux Lexer Error at "
            f"line {line}, column {column}: {message}"
        )


class Lexer:
    """Tokenizes AssayFlux source code."""

    def __init__(self, source: str):
        self.source = source
        self.position = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []

    def current_char(self):
        """Return the current character or None at EOF."""

        if self.position >= len(self.source):
            return None

        return self.source[self.position]

    def peek(self, offset: int = 1):
        """Look ahead without consuming a character."""

        index = self.position + offset

        if index >= len(self.source):
            return None

        return self.source[index]

    def advance(self):
        """Consume one character and update its location."""

        char = self.current_char()

        if char is None:
            return None

        self.position += 1

        if char == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1

        return char

    def add_token(
        self,
        token_type: str,
        value: str,
        line: int,
        column: int,
    ):
        """Append a token to the token list."""

        self.tokens.append(
            Token(
                type=token_type,
                value=value,
                line=line,
                column=column,
            )
        )

    def tokenize(self) -> List[Token]:
        """Convert the complete source into tokens."""

        while self.current_char() is not None:
            char = self.current_char()

            if char in " \t\r":
                self.advance()
                continue

            if char == "\n":
                line = self.line
                column = self.column

                self.advance()

                self.add_token(
                    "NEWLINE",
                    "\\n",
                    line,
                    column,
                )
                continue

            if char == "#":
                self.skip_comment()
                continue

            if char == "`":
                self.read_string()
                continue

            if char.isdigit():
                self.read_number()
                continue

            if char.isalpha() or char == "_":
                self.read_identifier()
                continue

            if char in PUNCTUATION:
                line = self.line
                column = self.column
                value = self.advance()

                self.add_token(
                    PUNCTUATION[value],
                    value,
                    line,
                    column,
                )
                continue

            if self.read_operator():
                continue

            raise LexerError(
                f"Unexpected character {char!r}.",
                self.line,
                self.column,
            )

        self.add_token(
            "EOF",
            "",
            self.line,
            self.column,
        )

        return self.tokens

    def skip_comment(self):
        """Skip a comment beginning with #."""

        while (
            self.current_char() is not None
            and self.current_char() != "\n"
        ):
            self.advance()

    def read_string(self):
        """Read a backtick-delimited string literal."""

        start_line = self.line
        start_column = self.column

        self.advance()  # Opening backtick

        value = []

        while self.current_char() is not None:
            char = self.current_char()

            if char == "`":
                self.advance()

                self.add_token(
                    "STRING",
                    "".join(value),
                    start_line,
                    start_column,
                )
                return

            if char == "\n":
                raise LexerError(
                    "String literals cannot contain an "
                    "unescaped newline.",
                    self.line,
                    self.column,
                )

            if char == "\\":
                self.advance()

                escaped = self.current_char()

                if escaped is None:
                    raise LexerError(
                        "Unterminated escape sequence "
                        "in string literal.",
                        self.line,
                        self.column,
                    )

                escape_map = {
                    "n": "\n",
                    "t": "\t",
                    "r": "\r",
                    "`": "`",
                    "\\": "\\",
                }

                if escaped not in escape_map:
                    raise LexerError(
                        f"Unknown escape sequence "
                        f"'\\{escaped}'.",
                        self.line,
                        self.column,
                    )

                value.append(escape_map[escaped])
                self.advance()
                continue

            value.append(char)
            self.advance()

        raise LexerError(
            "Unterminated string literal. "
            "Expected a closing backtick.",
            start_line,
            start_column,
        )

    def read_number(self):
        """Read an integer or decimal number."""

        start_line = self.line
        start_column = self.column
        start_position = self.position

        while (
            self.current_char() is not None
            and self.current_char().isdigit()
        ):
            self.advance()

        if (
            self.current_char() == "."
            and self.peek() is not None
            and self.peek().isdigit()
        ):
            self.advance()

            while (
                self.current_char() is not None
                and self.current_char().isdigit()
            ):
                self.advance()

        value = self.source[
            start_position:self.position
        ]

        self.add_token(
            "NUMBER",
            value,
            start_line,
            start_column,
        )

    def read_identifier(self):
        """Read an identifier or keyword."""

        start_line = self.line
        start_column = self.column
        start_position = self.position

        while self.current_char() is not None:
            char = self.current_char()

            if char.isalnum() or char == "_":
                self.advance()
            else:
                break

        value = self.source[
            start_position:self.position
        ]

        if value in KEYWORDS:
            token_type = "KEYWORD"
        else:
            token_type = "IDENTIFIER"

        self.add_token(
            token_type,
            value,
            start_line,
            start_column,
        )

    def read_operator(self) -> bool:
        """Read an operator using longest-match-first."""

        line = self.line
        column = self.column

        for operator in OPERATORS:
            if self.source.startswith(
                operator,
                self.position,
            ):
                for _ in operator:
                    self.advance()

                self.add_token(
                    "OPERATOR",
                    operator,
                    line,
                    column,
                )

                return True

        return False


def tokenize(source: str) -> List[Token]:
    """Convenience function for tokenizing source code."""

    return Lexer(source).tokenize()


if __name__ == "__main__":
    example = (
        "temperature = 30\n"
        "if temperature > 20\n"
        "    show `Warm day`\n"
        "else\n"
        "    show `Cold day`\n"
        "end\n"
    )

    try:
        for token in tokenize(example):
            print(token)

    except LexerError as error:
        print(error)