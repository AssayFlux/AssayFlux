from pathlib import Path

import pytest

from assayflux.diagnostics.model import (
    AstError,
    ParseError,
    SecurityError,
    SourceError,
    TypeCheckError,
)
from assayflux.language.ast_nodes import Program
from assayflux.language.ast_validator import validate_ast
from assayflux.language.parser import parse
from assayflux.language.semantic import check
from assayflux.runtime.interpreter import Interpreter
from assayflux.security.checkpoints import SecurityPolicy, validate_source


def test_parse_and_semantically_check_canonical_program():
    program = parse('project "Test"\nanswer = 6 * 7\nshow answer\n')
    assert isinstance(program, Program)
    check(program)


def test_interpreter_executes_arithmetic_and_show():
    result = Interpreter(SecurityPolicy()).run(
        parse('project "Test"\nanswer = 6 * 7\nshow answer\n'),
        validate=False,
    )
    assert result.output == ["42"]


def test_counted_repetition_runs_exactly_n_times():
    result = Interpreter(SecurityPolicy()).run(
        parse('3 times:\n    show "again"\nend\n'),
        validate=False,
    )
    assert result.output == ["again", "again", "again"]


def test_legacy_counted_loop_marker_is_rejected():
    with pytest.raises(ParseError):
        parse("3x.:\n")


def test_function_declaration_and_default_argument():
    program = parse(
        "f.multiply(value, factor = 2):\n"
        "    return value * factor\n"
        "end\n"
        "show multiply(6)\n"
    )
    check(program)
    result = Interpreter(SecurityPolicy()).run(program, validate=False)
    assert result.output == ["12"]


def test_null_and_boolean_literals():
    result = Interpreter(SecurityPolicy()).run(
        parse("missing = null\nactive = true\nshow missing\nshow active\n"),
        validate=False,
    )
    assert result.output == ["null", "true"]


def test_unknown_names_fail_semantic_check():
    with pytest.raises(TypeCheckError, match="Undefined name"):
        check(parse("show missing_name\n"))


def test_invalid_syntax_is_reported_as_parse_error():
    with pytest.raises(ParseError):
        parse("project [not a string]\n")


def test_ast_validator_rejects_non_program_root():
    with pytest.raises(AstError, match="AST root"):
        validate_ast(None)


def test_source_validation_enforces_byte_limit():
    policy = SecurityPolicy(max_source_bytes=4)
    with pytest.raises(SecurityError, match="size limit"):
        validate_source("12345", "<test>", policy)


def test_source_validation_rejects_nul_bytes():
    with pytest.raises(SourceError, match="NUL"):
        validate_source("show 1\x00", "<test>", SecurityPolicy())


def test_cli_check_and_run(tmp_path: Path, capsys):
    from assayflux.cli import main

    source = tmp_path / "hello.af"
    source.write_text('show "hello"\n', encoding="utf-8")

    assert main(["check", str(source)]) == 0
    assert "OK:" in capsys.readouterr().out

    assert main(["run", str(source)]) == 0
    assert capsys.readouterr().out.strip() == "hello"
