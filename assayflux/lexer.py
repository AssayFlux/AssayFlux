class LexError(Exception):
    """Custom exception for lexical analysis errors with line and column tracking."""
    def __init__(self, message: str, line: int, column: int, filename: str = "<string>"):
        self.message = message
        self.line = line
        self.column = column
        self.filename = filename
        super().__init__(f"[{filename}:{line}:{column}] Lexical Error: {message}")


class Lexer:
    """Tokenizes AssayFlux (.assayflux) source code with strict position tracking."""
    def __init__(self, source_code: str, filename: str = "<string>"):
        self.source_code = source_code
        self.filename = filename
        self.position = 0
        self.length = len(source_code)
        self.line = 1
        self.column = 1

    def _track_position(self, index: int):
        line = self.source_code.count('\n', 0, index) + 1
        last_newline = self.source_code.rfind('\n', 0, index)
        column = index - last_newline if last_newline != -1 else index + 1
        return line, column

    def error(self, message: str):
        raise LexError(message, self.line, self.column, self.filename)

    def tokenize(self) -> list:
        tokens = []
        while self.position < self.length:
            current_char = self.source_code[self.position]

            # Track current line/col
            self.line, self.column = self._track_position(self.position)

            # Skip whitespace
            if current_char.isspace():
                self.position += 1
                continue

            # Identifiers & Keywords
            if current_char.isalpha() or current_char == '_':
                start_pos = self.position
                while self.position < self.length and (self.source_code[self.position].isalnum() or self.source_code[self.position] == '_'):
                    self.position += 1
                lexeme = self.source_code[start_pos:self.position]
                tokens.append(("IDENTIFIER" if lexeme not in ["fn", "if", "else", "return", "var"] else "KEYWORD", lexeme))
                continue

            # Numeric Literals
            if current_char.isdigit():
                start_pos = self.position
                while self.position < self.length and self.source_code[self.position].isdigit():
                    self.position += 1
                tokens.append(("NUMBER", self.source_code[start_pos:self.position]))
                continue

            # Basic operators and symbols
            if current_char in "+-*/=(){}[]:,;":
                tokens.append(("OPERATOR_OR_DELIMITER", current_char))
                self.position += 1
                continue

            # Catch-all lexical error
            self.error(f"Unexpected character '{current_char}'")

        tokens.append(("EOF", "EOF"))
        return tokens
