from __future__ import annotations

import json
from unittest.mock import patch

from assayflux.execution import ExecutionRequest
from assayflux.execution.providers import CodeInterpreterProvider, PistonProvider


def test_piston_adapter_normalizes_response():
    response = {
        "language": "python",
        "version": "3.12.0",
        "run": {"stdout": "42\\n", "stderr": "", "code": 0, "signal": None, "output": "42\\n"},
    }
    with patch(
        "assayflux.execution.providers._request_json",
        return_value=(json.dumps(response).encode(), "application/json"),
    ) as call:
        result = PistonProvider("http://localhost:2000").execute(
            ExecutionRequest(code="print(6 * 7)", language="python", version="3.12.0")
        )

    assert call.call_args.kwargs["payload"]["run_timeout"] == 10000
    assert result.stdout == "42\\n"
    assert result.exit_code == 0


def test_code_interpreter_adapter_reads_newline_delimited_events():
    stream = (
        '{"type":"stdout","text":"hello\\n"}\\n'
        '{"type":"end_of_execution"}\\n'
    ).encode()
    with patch(
        "assayflux.execution.providers._request_json",
        return_value=(stream, "application/json"),
    ):
        result = CodeInterpreterProvider("http://localhost:8000").execute(
            ExecutionRequest(code="print('hello')")
        )

    assert result.stdout == "hello\\n"
    assert result.exit_code == 0
