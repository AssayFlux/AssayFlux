import pytest
from assayflux.lexer import LexError
from assayflux.parser import ParserError


class TestErrorLocations:
    def test_lex_error_line_column(self, run_af):
        source = "show 1\nshow @"
        with pytest.raises(LexError) as exc_info:
            run_af(source)
        assert exc_info.value.line == 2
        assert exc_info.value.column == 6

    def test_parser_error_line_column(self, run_af):
        source = "f.foo()\n    show 1\n    if\n    end\nend"
        with pytest.raises(ParserError) as exc_info:
            run_af(source)
        assert exc_info.value.line == 3

    def test_runtime_error_line_column(self, run_af):
        source = "show 1\nshow 2\nshow x / 0"
        with pytest.raises(RuntimeError) as exc_info:
            run_af(source)
        assert exc_info.value.line == 3