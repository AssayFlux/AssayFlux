import pytest
from assayflux.lexer import LexError
from assayflux.parser import ParserError
from assayflux.interpreter import RuntimeError


class TestLexErrors:
    def test_tab_indentation_rejected(self, run_af):
        source = "f.foo()\n\tshow 1\nend"
        with pytest.raises(LexError, match="tabs are not allowed"):
            run_af(source)

    def test_unterminated_string(self, run_af):
        source = 'show "hello'
        with pytest.raises(LexError, match="unterminated string"):
            run_af(source)

    def test_invalid_character(self, run_af):
        source = "show @"
        with pytest.raises(LexError, match="unexpected character"):
            run_af(source)


class TestParserErrors:
    def test_missing_end_keyword(self, run_af):
        source = "f.foo()\n    show 1"
        with pytest.raises(ParserError, match="expected 'end'"):
            run_af(source)

    def test_stop_outside_loop(self, run_af):
        source = "stop"
        with pytest.raises(ParserError, match="'stop' outside"):
            run_af(source)

    def test_unexpected_token(self, run_af):
        source = "f.foo()\n    if\n    end\nend"
        with pytest.raises(ParserError, match="expected expression"):
            run_af(source)


class TestRuntimeErrors:
    def test_division_by_zero(self, run_af):
        source = "show 10 / 0"
        with pytest.raises(RuntimeError, match="division by zero"):
            run_af(source)

    def test_undefined_variable(self, run_af):
        source = "show undefined_var"
        with pytest.raises(RuntimeError, match="undefined variable"):
            run_af(source)

    def test_wrong_argument_count(self, run_af):
        source = "f.add(a, b)\n    show a + b\nend\nadd(1)"
        with pytest.raises(RuntimeError, match="expects 2 arguments"):
            run_af(source)