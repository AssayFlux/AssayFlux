"""
AssayFlux Scientific Systems
Lexer and Tokenizer

This module converts AssayFlux source code into a sequence of
tokens for the parser.

Language:
    AssayFlux Scientific Systems

File extension:
    .af

Core custom syntax:
    show
    otherwise
    constant
    stop
    skip
    true
    false
    end
    f.function_name(...):

The lexer preserves source positions and emits NEWLINE, INDENT,
and DEDENT tokens to support indentation-sensitive parsing.

The lexer does not build an AST or execute programs. Those
responsibilities belong to the parser and interpreter.
"""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from typing import Optional


# ============================================================
# Version and Public API
# ============================================================

LEXER_VERSION = "1.0.0"


__all__ = [
    "Token",
    "Lexer",
    "LexError",
    "LexerError",
    "tokenize",
    "LEXER_VERSION",
]


# ============================================================
# Exceptions
# ============================================================

class LexError(Exception):
    """
    Raised when source code contains invalid lexical structure.

    Every error records:
        message
        line
        column
        filename

    Columns are one-based.
    Lines are one-based.
    """

    def __init__(
        self,
        message: str,
        line: int,
        column: int,
        filename: str = "<string>",
    ):
        self.message = message
        self.line = line
        self.column = column
        self.filename = filename

        super().__init__(
            f"[{filename}:{line}:{column}] "
            f"Lexical Error: {message}"
        )


# Compatibility alias.

# The existing parser imports LexerError, while the original
# lexer used the name LexError. Both names are now available.

LexerError = LexError


# ============================================================
# Token Representation
# ============================================================

@dataclass(frozen=True, slots=True)
class Token:
    """
    Represents one lexical token.

    Attributes:
        type:
            Token category, such as IDENTIFIER, NUMBER,
            STRING, KEYWORD, OPERATOR, NEWLINE, INDENT,
            DEDENT, or EOF.

        value:
            Semantic token value.

            Examples:
                IDENTIFIER -> "sample"
                NUMBER     -> "100"
                STRING     -> "AssayFlux"
                OPERATOR   -> "+"

        line:
            One-based starting line.

        column:
            One-based starting column.

        start:
            Zero-based starting source offset.

        end:
            Zero-based ending source offset, exclusive.

        filename:
            Source filename.

        lexeme:
            Original source spelling, when different from
            the normalized token value.

    The .type and .value attributes are intentionally provided
    for compatibility with the parser's current token API.
    """

    type: str
    value: str
    line: int
    column: int
    start: int = 0
    end: int = 0
    filename: str = "<string>"
    lexeme: Optional[str] = None

    def __post_init__(self):
        if self.lexeme is None:
            object.__setattr__(
                self,
                "lexeme",
                self.value,
            )

    @property
    def kind(self) -> str:
        """Alternative name for the token category."""
        return self.type

    @property
    def name(self) -> str:
        """Compatibility-friendly name for the token category."""
        return self.type

    @property
    def text(self) -> str:
        """Return the original token spelling."""
        return self.lexeme or self.value

    @property
    def width(self) -> int:
        """Return the source width of this token."""
        return self.end - self.start

    def __repr__(self) -> str:
        return (
            f"Token("
            f"type={self.type!r}, "
            f"value={self.value!r}, "
            f"line={self.line}, "
            f"column={self.column}"
            f")"
        )


# ============================================================
# Keyword Definitions
# ============================================================

# These keywords introduce AssayFlux-specific behavior.
#
# They are recognized by the lexer but their meaning must
# also be implemented by the parser and interpreter.

CUSTOM_KEYWORDS = {
    "show",
    "otherwise",
    "constant",
    "stop",
    "skip",
    "true",
    "false",
    "end",
    "repeat",
}


# These keywords retain Python-like meanings.
#
# Some are intended for future parser/runtime support.
# Recognizing a keyword does not mean that the current
# parser or interpreter already supports its behavior.

PYTHON_STYLE_KEYWORDS = {
    "and",
    "as",
    "assert",
    "async",
    "await",
    "break",
    "class",
    "continue",
    "def",
    "del",
    "elif",
    "else",
    "except",
    "finally",
    "for",
    "from",
    "global",
    "if",
    "import",
    "in",
    "is",
    "lambda",
    "nonlocal",
    "not",
    "or",
    "pass",
    "raise",
    "return",
    "try",
    "while",
    "with",
    "yield",
    "match",
    "case",
}


KEYWORDS = CUSTOM_KEYWORDS | PYTHON_STYLE_KEYWORDS


# Important:
#
# "f" is deliberately NOT a keyword.
#
# A function declaration such as:
#
#     f.add(a, b):
#
# must tokenize as:
#
#     IDENTIFIER("f")
#     OPERATOR(".")
#     IDENTIFIER("add")
#
# This allows the parser to recognize the special f.name
# declaration form without changing ordinary identifiers.


# ============================================================
# Operators
# ============================================================

# Longer operators must be matched before shorter operators.
#
# For example:
#
#     **= before **
#     **  before *
#     //= before //
#     //  before /
#     !=  before !
#     >=  before >
#
# Otherwise, the lexer could split one valid operator into
# multiple incorrect tokens.

OPERATORS = (
    "**=",
    "//=",
    ">>=",
    "<<=",
    "==",
    "!=",
    "<=",
    ">=",
    "+=",
    "-=",
    "*=",
    "/=",
    "%=",
    "@=",
    "&=",
    "|=",
    "^=",
    ":=",
    "->",
    "**",
    "//",
    "<<",
    ">>",
    "+",
    "-",
    "*",
    "/",
    "%",
    "@",
    "&",
    "|",
    "^",
    "~",
    "<",
    ">",
    "=",
)


DELIMITERS = {
    "(",
    ")",
    "[",
    "]",
    "{",
    "}",
    ",",
    ":",
    ".",
    ";",
}


OPENING_DELIMITERS = {
    "(",
    "[",
    "{",
}


CLOSING_DELIMITERS = {
    ")",
    "]",
    "}",
}


MATCHING_DELIMITERS = {
    ")": "(",
    "]": "[",
    "}": "{",
}


# ============================================================
# Numeric Literal Patterns
# ============================================================

# Supported lexical forms:
#
# Decimal integers:
#     0
#     10
#     1_000
#     25
#
# Binary integers:
#     0b1010
#
# Octal integers:
#     0o17
#
# Hexadecimal integers:
#     0xFF
#
# Floating-point numbers:
#     1.5
#     .5
#     10.
#     1e5
#     1.5e-3
#
# Complex numeric suffixes:
#     2j
#     3.5j
#
# Whether every form is accepted by the parser and runtime
# depends on their implementations.

NUMBER_PATTERN = re.compile(
    r"""
    (?:
        # Hexadecimal integer.
        0[xX](?:[0-9a-fA-F](?:_?[0-9a-fA-F])*)?

        |

        # Binary integer.
        0[bB](?:[01](?:_?[01])*)?

        |

        # Octal integer.
        0[oO](?:[0-7](?:_?[0-7])*)?

        |

        # Decimal integer, decimal float, or exponent form.
        (?:
            (?:
                [0-9](?:_?[0-9])*
                (?:\.(?:[0-9](?:_?[0-9])*)?)?
                |
                \.(?:[0-9](?:_?[0-9])*)
            )
            (?:[eE][+-]?[0-9](?:_?[0-9])*)?
        )

        # Optional complex suffix.
        [jJ]?
    )
    """,
    re.VERBOSE,
)


# ============================================================
# String Prefixes
# ============================================================

# The lexer recognizes common Python-style string prefixes.
#
# Prefix recognition does not automatically guarantee that
# the parser/interpreter supports each string behavior.

STRING_PREFIXES = {
    "",
    "r",
    "u",
    "b",
    "f",
    "br",
    "rb",
    "fr",
    "rf",
}


# ============================================================
# Lexer Implementation
# ============================================================

class Lexer:
    """
    Tokenize AssayFlux source code.

    The lexer handles:

        * identifiers
        * keywords
        * numeric literals
        * strings
        * operators
        * delimiters
        * comments
        * line boundaries
        * indentation
        * dedentation
        * bracket nesting
        * lexical errors
        * source locations

    Token output is intended for a separate parser.
    """

    def __init__(
        self,
        source_code: str,
        filename: str = "<string>",
    ):
        if not isinstance(source_code, str):
            raise TypeError(
                "AssayFlux source code must be a string."
            )

        self.source_code = (
    source_code
    .replace("\r\n", "\n")
    .replace("\r", "\n")
)
self.filename = filename

        self.position = 0
        self.length = len(source_code)

        self.line = 1
        self.column = 1

        self.tokens: list[Token] = []

        # Indentation levels are measured in visual columns.
        #
        # The first element represents the top-level scope.
        self.indentation_stack = [0]

        # Bracket nesting suppresses NEWLINE and indentation
        # processing inside multiline expressions.
        self.delimiter_stack: list[tuple[str, int, int]] = []

        self.at_line_start = True

        # Whether the current logical line has meaningful
        # source tokens.
        self.logical_line_has_tokens = False

        # Whether the previous character was a line-continuation
        # backslash.
        self.explicit_line_continuation = False

    # --------------------------------------------------------
    # Position Tracking
    # --------------------------------------------------------

    def _current_char(self) -> str:
        """Return the current character or an empty string."""
        if self.position >= self.length:
            return ""

        return self.source_code[self.position]

    def _peek_char(self, offset: int = 1) -> str:
        """Look ahead without consuming characters."""
        index = self.position + offset

        if index >= self.length:
            return ""

        return self.source_code[index]

    def _advance(self, count: int = 1) -> str:
        """
        Consume source characters and update line/column.

        Returns the consumed text.
        """
        start = self.position
        end = min(
            self.position + count,
            self.length,
        )

        consumed = self.source_code[start:end]

        for character in consumed:
            if character == "\n":
                self.line += 1
                self.column = 1
            else:
                self.column += 1

        self.position = end

        return consumed

    def _location(self) -> tuple[int, int]:
        """Return the current one-based line and column."""
        return self.line, self.column

    def error(self, message: str):
        """Raise a lexical error at the current position."""
        raise LexError(
            message=message,
            line=self.line,
            column=self.column,
            filename=self.filename,
        )

    def _error_at(
        self,
        message: str,
        line: int,
        column: int,
    ):
        """Raise a lexical error at a specified location."""
        raise LexError(
            message=message,
            line=line,
            column=column,
            filename=self.filename,
        )

    # --------------------------------------------------------
    # Token Creation
    # --------------------------------------------------------

    def _emit(
        self,
        token_type: str,
        value: str,
        start: int,
        line: int,
        column: int,
        lexeme: Optional[str] = None,
    ) -> Token:
        """Create and append a token."""
        token = Token(
            type=token_type,
            value=value,
            line=line,
            column=column,
            start=start,
            end=self.position,
            filename=self.filename,
            lexeme=lexeme,
        )

        self.tokens.append(token)

        return token

    def _emit_at_current(
        self,
        token_type: str,
        value: str,
        start: int,
        line: int,
        column: int,
        lexeme: Optional[str] = None,
    ) -> Token:
        """
        Emit a token ending at the current source position.

        This helper makes token creation explicit at scanning
        boundaries.
        """
        return self._emit(
            token_type=token_type,
            value=value,
            start=start,
            line=line,
            column=column,
            lexeme=lexeme,
        )

    # --------------------------------------------------------
    # Indentation
    # --------------------------------------------------------

    def _visual_indentation(
        self,
        whitespace: str,
        line: int,
        column: int,
    ) -> int:
        """
        Calculate indentation using visual columns.

        Spaces advance one column.
        Tabs advance to the next multiple of eight.

        Mixing tabs and spaces in a single indentation prefix
        is rejected to prevent ambiguous block structure.
        """
        if " " in whitespace and "\t" in whitespace:
            self._error_at(
                "Do not mix tabs and spaces in indentation.",
                line,
                column,
            )

        visual_column = 0

        for character in whitespace:
            if character == " ":
                visual_column += 1

            elif character == "\t":
                visual_column = (
                    (visual_column // 8) + 1
                ) * 8

        return visual_column

    def _handle_indentation(self):
        """
        Process indentation at the beginning of a physical line.

        Blank lines and comment-only lines do not change the
        indentation stack.

        Inside parentheses, brackets, and braces, indentation
        does not create INDENT or DEDENT tokens.
        """
        if not self.at_line_start:
            return

        if self.delimiter_stack:
            # Continuation lines inside delimiters do not
            # introduce new indentation scopes.
            while self._current_char() in (" ", "\t", "\f"):
                self._advance()

            self.at_line_start = False
            return

        indentation_start = self.position
        indentation_line = self.line
        indentation_column = self.column

        while self._current_char() in (" ", "\t", "\f"):
            self._advance()

        whitespace = self.source_code[
            indentation_start:self.position
        ]

        current_char = self._current_char()

        # Blank line.
        if current_char == "\n":
            newline_start = self.position
            newline_line = self.line
            newline_column = self.column

            self._advance()

            self._emit(
                "NEWLINE",
                "\n",
                newline_start,
                newline_line,
                newline_column,
                "\n",
            )

            self.at_line_start = True
            self.logical_line_has_tokens = False
            return

        # End of file after whitespace.
        if current_char == "":
            self.at_line_start = False
            return

        # Comment-only line.
        if current_char == "#":
            self._consume_comment()

            if self._current_char() == "\n":
                newline_start = self.position
                newline_line = self.line
                newline_column = self.column

                self._advance()

                self._emit(
                    "NEWLINE",
                    "\n",
                    newline_start,
                    newline_line,
                    newline_column,
                    "\n",
                )

            self.at_line_start = True
            self.logical_line_has_tokens = False
            return

        indentation = self._visual_indentation(
            whitespace,
            indentation_line,
            indentation_column,
        )

        previous_indentation = self.indentation_stack[-1]

        if indentation > previous_indentation:
            self.indentation_stack.append(indentation)

            self._emit(
                "INDENT",
                str(indentation),
                self.position,
                self.line,
                self.column,
                "",
            )

        elif indentation < previous_indentation:
            while (
                len(self.indentation_stack) > 1
                and indentation < self.indentation_stack[-1]
            ):
                self.indentation_stack.pop()

                self._emit(
                    "DEDENT",
                    str(self.indentation_stack[-1]),
                    self.position,
                    self.line,
                    self.column,
                    "",
                )

            if self.indentation_stack[-1] != indentation:
                self._error_at(
                    "Inconsistent indentation. "
                    "The indentation does not match "
                    "any previously opened block.",
                    self.line,
                    self.column,
                )

        self.at_line_start = False

    # --------------------------------------------------------
    # Comments
    # --------------------------------------------------------

    def _consume_comment(self):
        """Consume a hash comment through the end of the line."""
        while self._current_char() not in ("", "\n"):
            self._advance()

    # --------------------------------------------------------
    # Newlines
    # --------------------------------------------------------

    def _consume_newline(self):
        """
        Consume a physical newline.

        A logical NEWLINE token is emitted only when the lexer
        is not inside a bracketed expression and the line has
        meaningful tokens.
        """
        start = self.position
        line = self.line
        column = self.column

        self._advance()

        if self.delimiter_stack:
            # Physical newline inside a bracketed expression.
            # The expression continues on the next line.
            self.at_line_start = True
            return

        if self.logical_line_has_tokens:
            self._emit(
                "NEWLINE",
                "\n",
                start,
                line,
                column,
                "\n",
            )

        self.logical_line_has_tokens = False
        self.at_line_start = True
        self.explicit_line_continuation = False

    # --------------------------------------------------------
    # Identifiers and Keywords
    # --------------------------------------------------------

    @staticmethod
    def _is_identifier_start(character: str) -> bool:
        """
        Determine whether a character can begin an identifier.

        Python's Unicode identifier rules are approximated
        using str.isidentifier().
        """
        if character == "_":
            return True

        return bool(character) and character.isidentifier()

    @staticmethod
    def _is_identifier_continue(character: str) -> bool:
        """Determine whether a character can continue an identifier."""
        if not character:
            return False

        return ("a" + character).isidentifier()

    def _scan_identifier(self) -> Token:
        """Scan an identifier or keyword."""
        start = self.position
        line = self.line
        column = self.column

        self._advance()

        while self._is_identifier_continue(
            self._current_char()
        ):
            self._advance()

        lexeme = self.source_code[start:self.position]

        if lexeme in KEYWORDS:
            token_type = "KEYWORD"
        else:
            token_type = "IDENTIFIER"

        self.logical_line_has_tokens = True

        return self._emit(
            token_type,
            lexeme,
            start,
            line,
            column,
            lexeme,
        )


    # --------------------------------------------------------
    # Numeric Literals
    # --------------------------------------------------------

    
def _scan_number(self) -> Token:
    """
    Scan and validate a complete numeric literal.

    Lexical recognition and numeric validation are separate.
    The lexer must not silently accept malformed numbers.
    """
    start = self.position
    line = self.line
    column = self.column

    remaining = self.source_code[self.position:]
    match = NUMBER_PATTERN.match(remaining)

    if match is None:
        self._error_at(
            "Invalid numeric literal.",
            line,
            column,
        )

    lexeme = match.group(0)

    if not lexeme:
        self._error_at(
            "Invalid numeric literal.",
            line,
            column,
        )

    # Reject malformed suffixes instead of splitting them
    # into a number followed by an identifier.
    next_index = self.position + len(lexeme)

    if next_index < self.length:
        next_character = self.source_code[next_index]

        if (
            next_character.isalpha()
            or next_character == "_"
        ):
            self._error_at(
                f"Invalid numeric literal "
                f"{lexeme + next_character!r}.",
                line,
                column,
            )

    # Validate the complete numeric spelling without executing
    # arbitrary source code.
    try:
        parsed_value = ast.literal_eval(lexeme)

    except (ValueError, SyntaxError, TypeError, MemoryError):
        self._error_at(
            f"Malformed numeric literal {lexeme!r}.",
            line,
            column,
        )

    if type(parsed_value) not in (int, float, complex):
        self._error_at(
            f"Invalid numeric literal {lexeme!r}.",
            line,
            column,
        )

    self._advance(len(lexeme))

    self.logical_line_has_tokens = True

    return self._emit(
        "NUMBER",
        lexeme,
        start,
        line,
        column,
        lexeme,
    )
 --------------------------------------------------------
    # Strings
    # --------------------------------------------------------

    def _find_string_prefix(self) -> Optional[str]:
        """
        Detect a recognized string prefix immediately before
        a quote.

        Returns:
            The prefix, including an empty prefix for an
            unprefixed string.

        The method does not consume source characters.
        """
        if self._current_char() in ("'", '"'):
            return ""

        if not self._is_identifier_start(
            self._current_char()
        ):
            return None

        index = self.position

        while (
            index < self.length
            and self.source_code[index].isalpha()
        ):
            index += 1

        prefix = self.source_code[
            self.position:index
        ].lower()

        if prefix not in STRING_PREFIXES:
            return None

        if index >= self.length:
            return None

        if self.source_code[index] not in ("'", '"'):
            return None

        return prefix

    def _scan_string(self) -> Token:
        """
        Scan a quoted string literal.

        Supported lexical forms include:

            "text"
            'text'
            """multiline text"""
            '''multiline text'''
            r"raw text"
            b"bytes"
            f"formatted text"

        Formatted strings receive the FSTRING token type.
        Their interpolation semantics must be implemented by
        the parser/runtime.

        Ordinary strings are decoded with ast.literal_eval
        when possible.
        """
        start = self.position
        line = self.line
        column = self.column

        prefix = self._find_string_prefix()

        if prefix is None:
            self.error("Invalid string prefix.")

        # Consume the prefix.
        if prefix:
            self._advance(len(prefix))

        quote = self._current_char()

        if quote not in ("'", '"'):
            self.error("Expected a string quotation mark.")

        # Triple-quoted string detection.
        triple = (
            self._peek_char(0) == quote
            and self._peek_char(1) == quote
            and self._peek_char(2) == quote
        )

        if triple:
            opening = quote * 3
            self._advance(3)
        else:
            opening = quote
            self._advance(1)

        content_start = self.position

        while True:
            current = self._current_char()

            if current == "":
                self._error_at(
                    "Unterminated string literal.",
                    line,
                    column,
                )

            if current == "\\":
                # Consume the escape marker and the next
                # character without treating an escaped
                # quote as the string terminator.
                self._advance()

                if self._current_char() == "":
                    self._error_at(
                        "Unterminated escape sequence.",
                        self.line,
                        self.column,
                    )

                self._advance()
                continue

            if triple:
                if (
                    current == quote
                    and self._peek_char(1) == quote
                    and self._peek_char(2) == quote
                ):
                    content_end = self.position
                    self._advance(3)
                    break

            else:
                if current == quote:
                    content_end = self.position
                    self._advance()
                    break

                if current == "\n":
                    self._error_at(
                        "A single-line string cannot contain "
                        "an unescaped newline.",
                        self.line,
                        self.column,
                    )

            self._advance()

        lexeme = self.source_code[
            start:self.position
        ]

        raw_content = self.source_code[
            content_start:content_end
        ]

        self.logical_line_has_tokens = True

        # A string token may contain physical newlines.
        # After the closing quotation mark, the current
        # source line already contains part of the token.
        self.at_line_start = False

        if "f" in prefix:
            # The parser/runtime must implement interpolation.
            token_type = "FSTRING"
            value = raw_content

        elif "b" in prefix:
            # Keep the lexical content as text here.
            # The parser may later introduce a dedicated
            # bytes-literal AST node.
            token_type = "BYTES"
            value = raw_content

        else:
            token_type = "STRING"

            try:
                # ast.literal_eval safely decodes ordinary
                # Python-compatible string escapes.
                value = ast.literal_eval(lexeme)

                if not isinstance(value, str):
                    value = raw_content

            except (ValueError, SyntaxError):
                value = raw_content

        return self._emit(
            token_type,
            str(value),
            start,
            line,
            column,
            lexeme,
        )


    # --------------------------------------------------------
    # Operators and Delimiters
    # --------------------------------------------------------

    def _scan_operator_or_delimiter(self) -> Token:
        """Scan the longest valid operator or delimiter."""
        start = self.position
        line = self.line
        column = self.column

        for operator in OPERATORS:
            if self.source_code.startswith(
                operator,
                self.position,
            ):
                self._advance(len(operator))

                self.logical_line_has_tokens = True

                return self._emit(
                    "OPERATOR",
                    operator,
                    start,
                    line,
                    column,
                    operator,
                )

        current = self._current_char()

        if current in DELIMITERS:
            self._advance()

            if current in OPENING_DELIMITERS:
                self.delimiter_stack.append(
                    (current, line, column)
                )

            elif current in CLOSING_DELIMITERS:
                if not self.delimiter_stack:
                    self._error_at(
                        f"Unexpected closing delimiter {current!r}.",
                        line,
                        column,
                    )

                opening, opening_line, opening_column = (
                    self.delimiter_stack[-1]
                )

                expected_opening = MATCHING_DELIMITERS[
                    current
                ]

                if opening != expected_opening:
                    self._error_at(
                        f"Mismatched delimiter {current!r}; "
                        f"the most recent opening delimiter "
                        f"was {opening!r} at "
                        f"{opening_line}:{opening_column}.",
                        line,
                        column,
                    )

                self.delimiter_stack.pop()

            self.logical_line_has_tokens = True

            return self._emit(
                "DELIMITER",
                current,
                start,
                line,
                column,
                current,
            )

        self.error(
            f"Unexpected character {current!r}."
        )

    # --------------------------------------------------------
    # Explicit Line Continuation
    # --------------------------------------------------------

    def _consume_line_continuation(self):
        """
        Consume a backslash followed by a newline.

        This continues the current logical line.
        """
        line = self.line
        column = self.column

        if self._current_char() != "\\":
            return False

        next_character = self._peek_char()

        if next_character != "\n":
            return False

        self._advance(2)

        self.at_line_start = True
        self.explicit_line_continuation = True

        return True

    # --------------------------------------------------------
    # End-of-File Handling
    # --------------------------------------------------------

    def _finish(self):
        """
        Finish tokenization.

        Emit a final NEWLINE when necessary, close all remaining
        indentation levels, validate delimiter nesting, and
        append EOF.
        """
        if self.delimiter_stack:
            opening, line, column = self.delimiter_stack[-1]

            self._error_at(
                f"Unclosed delimiter {opening!r}.",
                line,
                column,
            )

        # A final line need not physically end with '\n'.
        if self.logical_line_has_tokens:
            self._emit(
                "NEWLINE",
                "\n",
                self.position,
                self.line,
                self.column,
                "",
            )

            self.logical_line_has_tokens = False

        # Close all indentation scopes.
        while len(self.indentation_stack) > 1:
            self.indentation_stack.pop()

            self._emit(
                "DEDENT",
                str(self.indentation_stack[-1]),
                self.position,
                self.line,
                self.column,
                "",
            )

        self._emit(
            "EOF",
            "EOF",
            self.position,
            self.line,
            self.column,
            "",
        )

    # --------------------------------------------------------
    # Main Tokenization Loop
    # --------------------------------------------------------

    def tokenize(self) -> list[Token]:
        """
        Tokenize the entire source file.

        Returns:
            A list of Token objects ending with EOF.

        Calling tokenize repeatedly on the same Lexer instance
        returns the cached token list after the first run.
        """
        if self.tokens:
            if self.tokens[-1].type == "EOF":
                return list(self.tokens)

        while self.position < self.length:
            if self.at_line_start:
                self._handle_indentation()

                # Indentation processing may consume an entire
                # blank or comment-only line.
                if self.position >= self.length:
                    break

                if self.at_line_start:
                    continue

            current = self._current_char()

            # Ordinary horizontal whitespace.
            if current in (" ", "\t", "\f"):
                self._advance()
                continue

            # Newline.
            if current == "\n":
                self._consume_newline()
                continue

            # Comments.
            if current == "#":
                self._consume_comment()
                continue

            # Explicit line continuation.
            if current == "\\":
                if self._consume_line_continuation():
                    continue

                self.error(
                    "A backslash must be followed by a newline "
                    "when used for explicit line continuation."
                )

            # String literals must be checked before ordinary
            # identifiers because prefixes such as f and r
            # may immediately precede quotation marks.
            prefix = self._find_string_prefix()

            if prefix is not None:
                self._scan_string()
                continue

            # Identifiers and keywords.
            if self._is_identifier_start(current):
                self._scan_identifier()
                continue

            # Numeric literals.
            if current.isdigit() or (
                current == "."
                and self._peek_char().isdigit()
            ):
                self._scan_number()
                continue

            # Operators and delimiters.
            self._scan_operator_or_delimiter()

        self._finish()

        return list(self.tokens)


# ============================================================
# Public Convenience API
# ============================================================

def tokenize(
    source_code: str,
    filename: str = "<string>",
) -> list[Token]:
    """
    Tokenize AssayFlux source code without manually creating
    a Lexer instance.

    Example:

        from assayflux.lexer import tokenize

        tokens = tokenize(
            'show "Hello"',
            filename="hello.af",
        )
    """
    return Lexer(
        source_code,
        filename=filename,
    ).tokenize()


# ============================================================
# Command-Line Debugging
# ============================================================

if __name__ == "__main__":
    import argparse
    from pathlib import Path
    import sys

    argument_parser = argparse.ArgumentParser(
        description=(
            "Tokenize an AssayFlux source file "
            "and display its tokens."
        )
    )

    argument_parser.add_argument(
        "file",
        nargs="?",
        help="Path to an AssayFlux source file.",
    )

    argument_parser.add_argument(
        "--source",
        help="Tokenize a source string directly.",
    )

    arguments = argument_parser.parse_args()

    if arguments.source is not None:
        source = arguments.source
        filename = "<command-line>"

    elif arguments.file:
        source_path = Path(arguments.file)

        if not source_path.is_file():
            print(
                f"File not found: {source_path}",
                file=sys.stderr,
            )
            sys.exit(1)

        try:
            source = source_path.read_text(
                encoding="utf-8"
            )
        except (OSError, UnicodeError) as error:
            print(
                f"Could not read source file: {error}",
                file=sys.stderr,
            )
            sys.exit(1)

        filename = str(source_path)

    else:
        argument_parser.error(
            "Provide a source file or use --source."
        )

    try:
        for token in tokenize(
            source,
            filename=filename,
        ):
            print(token)

    except LexError as error:
        print(error, file=sys.stderr)
        sys.exit(1)