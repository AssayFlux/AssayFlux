import pytest
from assayflux.lexer import LexError
from assayflux.parser import ParserError
from assayflux.interpreter import RuntimeError

@pytest.fixture
def run_af():
    """Helper to parse and interpret AssayFlux source code."""
    from assayflux.lexer import Lexer
    from assayflux.parser import Parser
    from assayflux.interpreter import Interpreter

    def _run(source: str):
        tokens = Lexer(source).tokenize()
        ast = Parser(tokens).parse()
        interpreter = Interpreter()
        return interpreter.interpret(ast)

    return _run