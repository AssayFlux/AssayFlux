"""
AssayFlux Scientific Systems
Lexer Implementation

Converts AssayFlux source code into tokens.

Language rules:
- Strings use single or double quotes.
- The not-equal operator is !=.
- Indentation uses four spaces per level.
- Tabs are prohibited for indentation.
- Comments begin with #.

Version: 0.2.0
"""

from dataclasses import dataclass
from typing import List


INDENT_SIZE = 4


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
    "constant",
}


OPERATORS = [
    "==",
    "!=",
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

        # Stack of indentation widths, measured in spaces.
        self.indentation_stack = [0]

        # True when the next nonblank source line begins.
        self.at_line_start = True

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

    def process_indentation(self):
        """Recognize indentation at the beginning of a line."""

        if not self.at_line_start:
            return

        start_line = self.line
        spaces = 0

        while self.current_char() == " ":
            self.advance()
            spaces += 1

        if self.current_char() == "\t":
            raise LexerError(
                "Tabs are not allowed for indentation. "
                "Use four spaces per indentation level.",
                self.line,
                self.column,
            )

        # Blank lines and comment-only lines do not change
        # the indentation level.
        if (
            self.current_char() is None
            or self.current_char() == "\n"
            or self.current_char() == "#"
        ):
            self.at_line_start = False
            return

        if spaces % INDENT_SIZE != 0:
            raise LexerError(
                "Indentation must use multiples of "
                "four spaces.",
                start_line,
                1,
            )

        current_indent = self.indentation_stack[-1]

        if spaces > current_indent:
            if spaces != current_indent + INDENT_SIZE:
                raise LexerError(
                    "Indentation may increase by exactly "
                    "four spaces per level.",
                    start_line,
                    1,
                )

            self.indentation_stack.append(spaces)

            self.add_token(
                "INDENT",
                " " * spaces,
                start_line,
                1,
            )

        elif spaces < current_indent:
            while (
                len(self.indentation_stack) > 1
                and spaces < self.indentation_stack[-1]
            ):
                self.indentation_stack.pop()

                self.add_token(
                    "DEDENT",
                    "",
                    start_line,
                    1,
                )

            if self.indentation_stack[-1] != spaces:
                raise LexerError(
                    "Indentation does not match an "
                    "existing indentation level.",
                    start_line,
                    1,
                )

        self.at_line_start = False

    def tokenize(self) -> List[Token]:
        """Convert the complete source into tokens."""

        while self.current_char() is not None:
            if self.at_line_start:
                self.process_indentation()

                if (
                    self.current_char() is None
                    or self.current_char() == "\n"
                    or self.current_char() == "#"
                ):
                    continue

            char = self.current_char()

            if char in " \t\r":
                if char == "\t":
                    raise LexerError(
                        "Tabs are not allowed. "
                        "Use spaces for indentation.",
                        self.line,
                        self.column,
                    )

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

                self.at_line_start = True
                continue

            if char == "#":
                self.skip_comment()
                continue

            if char in ("'", '"'):
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

        # Close any remaining indentation levels.
        while len(self.indentation_stack) > 1:
            self.indentation_stack.pop()

            self.add_token(
                "DEDENT",
                "",
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
        """Read a single- or double-quoted string."""

        quote = self.current_char()
        start_line = self.line
        start_column = self.column

        self.advance()

        value = []

        escape_map = {
            "n": "\n",
            "t": "\t",
            "r": "\r",
            "\\": "\\",
            "'": "'",
            '"': '"',
        }

        while self.current_char() is not None:
            char = self.current_char()

            if char == quote:
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
            f"Expected a closing {quote}.",
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
        'temperature = 30\n'
        'if temperature > 20\n'
        '    show "Warm day"\n'
        'else\n'
        '    show \'Cold day\'\n'
        'end\n'
    )

    try:
        for token in tokenize(example):
            print(token)

    except LexerError as error:
        print(error) 