from __future__ import annotations

import json
from unittest.mock import patch

from assayflux.execution import ExecutionRequest
from assayflux.execution.providers import CodeInterpreterProvider, PistonProvider


def test_piston_adapter_normalizes_response():
    response = {
        "language": "python",
        "version": "3.12.0",
        "run": {"stdout": "42\n", "stderr": "", "code": 0, "signal": None, "output": "42\n"},
    }
    with patch(
        "assayflux.execution.providers._request_json",
        return_value=(json.dumps(response).encode(), "application/json"),
    ) as call:
        result = PistonProvider("http://localhost:2000").execute(
            ExecutionRequest(code="print(6 * 7)", language="python", version="3.12.0")
        )

    assert call.call_args.kwargs["payload"]["run_timeout"] == 10000
    assert result.stdout == "42\n"
    assert result.exit_code == 0


def test_code_interpreter_adapter_reads_newline_delimited_events():
    stream = (
        '{"type":"stdout","text":"hello\\n"}\n'
        '{"type":"end_of_execution"}\n'
    ).encode()
    with patch(
        "assayflux.execution.providers._request_json",
        return_value=(stream, "application/json"),
    ):
        result = CodeInterpreterProvider("http://localhost:8000").execute(
            ExecutionRequest(code="print('hello')")
        )

    assert result.stdout == "hello\n"
    assert result.exit_code == 0


def test_cli_requires_explicit_external_execution_opt_in(capsys):
    from assayflux.cli import main

    status = main(["execute", "--provider", "piston", "--code", "print(1)"])

    assert status == 1
    assert "--allow-external-execution" in capsys.readouterr().err


def test_cli_runtime_discovery_uses_provider_factory(monkeypatch, capsys):
    from assayflux.cli import main

    class FakePiston:
        def list_runtimes(self):
            return [{"language": "python", "version": "3.12.0", "aliases": ["py"]}]

    monkeypatch.setattr("assayflux.cli.get_provider", lambda name: FakePiston())
    status = main(["runtimes", "--json"])

    assert status == 0
    assert '"language": "python"' in capsys.readouterr().out
