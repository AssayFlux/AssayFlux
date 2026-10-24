"""Adapters for the optional Piston and Code Interpreter services.

These clients call separately deployed services. They do not start containers,
install runtimes, or claim that a remote endpoint is a security boundary.
"""
from __future__ import annotations

import json
import os
import re
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request as URLRequest
from urllib.request import urlopen

from assayflux.diagnostics.model import RuntimeErrorAF, SecurityError
from assayflux.execution.models import ExecutionProvider, ExecutionRequest, ExecutionResult

_MAX_CODE_BYTES = 1_000_000
_MAX_RESPONSE_BYTES = 8_000_000
_MAX_TIMEOUT_SECONDS = 120
_DEFAULT_HTTP_TIMEOUT_SECONDS = 15
_LANGUAGE = re.compile(r"[A-Za-z0-9_+.#-]{1,80}\Z")
_VERSION = re.compile(r"[A-Za-z0-9.+_-]{1,80}\Z")
_CONTEXT_ID = re.compile(r"[A-Za-z0-9_-]{1,200}\Z")


def _base_url(value: str, *, env_name: str) -> str:
    value = value.strip().rstrip("/")
    parts = urlsplit(value)
    if (
        parts.scheme not in {"http", "https"}
        or not parts.netloc
        or parts.username is not None
        or parts.password is not None
        or parts.query
        or parts.fragment
    ):
        raise SecurityError(
            f"Invalid service URL in {env_name}",
            suggestion="Use an http(s) URL without embedded credentials, query, or fragment.",
        )
    return value


def _validate_request(request: ExecutionRequest) -> None:
    if not isinstance(request.code, str):
        raise SecurityError("Execution code must be text")
    if len(request.code.encode("utf-8")) > _MAX_CODE_BYTES:
        raise SecurityError("Execution code exceeds the 1 MB request limit")
    if not 1 <= request.timeout_seconds <= _MAX_TIMEOUT_SECONDS:
        raise SecurityError(f"Execution timeout must be between 1 and {_MAX_TIMEOUT_SECONDS} seconds")
    if request.language is not None and not _LANGUAGE.fullmatch(request.language):
        raise SecurityError("Invalid execution language identifier")
    if request.version is not None and not _VERSION.fullmatch(request.version):
        raise SecurityError("Invalid runtime version selector")
    if request.context_id is not None and not _CONTEXT_ID.fullmatch(request.context_id):
        raise SecurityError("Invalid code-interpreter context identifier")
    if not isinstance(request.stdin, str) or len(request.stdin.encode("utf-8")) > _MAX_CODE_BYTES:
        raise SecurityError("stdin must be text no larger than 1 MB")
    if len(request.args) > 100 or any(not isinstance(arg, str) or len(arg) > 10_000 for arg in request.args):
        raise SecurityError("Program arguments must be strings with at most 100 arguments of 10,000 characters each")
    filename = request.filename
    if (
        not filename
        or len(filename) > 200
        or filename in {".", ".."}
        or "/" in filename
        or "\\" in filename
        or "\x00" in filename
    ):
        raise SecurityError("Execution filename must be a plain filename, not a path")


def _request_json(
    url: str,
    *,
    method: str,
    payload: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
    timeout: int = _DEFAULT_HTTP_TIMEOUT_SECONDS,
    max_response_bytes: int = _MAX_RESPONSE_BYTES,
) -> tuple[bytes, str]:
    request_headers = {"Accept": "application/json", **(headers or {})}
    data = None
    if payload is not None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        request_headers["Content-Type"] = "application/json"
    req = URLRequest(url, data=data, headers=request_headers, method=method)
    try:
        with urlopen(req, timeout=timeout) as response:
            content_type = response.headers.get("Content-Type", "")
            body = response.read(max_response_bytes + 1)
            if len(body) > max_response_bytes:
                raise RuntimeErrorAF("Execution provider response exceeded the configured size limit")
            return body, content_type
    except HTTPError as exc:
        # Do not echo request bodies or authorization headers into diagnostics.
        try:
            message = exc.read(4096).decode("utf-8", errors="replace")
        except OSError:
            message = ""
        raise RuntimeErrorAF(
            f"Execution provider returned HTTP {exc.code}",
            details=message[:1000] or exc.reason,
            suggestion="Check the provider URL, runtime availability, and service logs.",
        ) from exc
    except (URLError, TimeoutError, OSError) as exc:
        raise RuntimeErrorAF(
            "Could not reach the configured execution provider",
            details=type(exc).__name__,
            suggestion="Check that the service is running and its URL is correct.",
        ) from exc


class PistonProvider:
    """Client for a separately deployed Piston API v2 instance."""

    name = "piston"

    def __init__(self, base_url: str | None = None, token: str | None = None):
        self.base_url = _base_url(
            base_url or os.environ.get("ASSAYFLUX_PISTON_URL", "http://127.0.0.1:2000"),
            env_name="ASSAYFLUX_PISTON_URL",
        )
        self.token = token if token is not None else os.environ.get("ASSAYFLUX_PISTON_TOKEN")

    def _headers(self) -> dict[str, str]:
        if self.token:
            return {"Authorization": f"Bearer {self.token}"}
        return {}

    def list_runtimes(self) -> list[dict[str, Any]]:
        body, _ = _request_json(
            f"{self.base_url}/api/v2/runtimes",
            method="GET",
            headers=self._headers(),
        )
        try:
            value = json.loads(body)
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise RuntimeErrorAF("Piston returned invalid JSON for its runtime list") from exc
        if not isinstance(value, list) or any(not isinstance(item, dict) for item in value):
            raise RuntimeErrorAF("Piston returned an unexpected runtime-list format")
        return value

    def execute(self, request: ExecutionRequest) -> ExecutionResult:
        _validate_request(request)
        if not request.language or not request.version:
            raise SecurityError("Piston execution requires both --language and --version")
        source = request.code
        payload = {
            "language": request.language,
            "version": request.version,
            "files": [{"name": request.filename, "content": source, "encoding": "utf8"}],
            "stdin": request.stdin,
            "args": list(request.args),
            "run_timeout": request.timeout_seconds * 1000,
            "compile_timeout": request.timeout_seconds * 1000,
        }
        body, _ = _request_json(
            f"{self.base_url}/api/v2/execute",
            method="POST",
            payload=payload,
            headers=self._headers(),
            timeout=request.timeout_seconds + _DEFAULT_HTTP_TIMEOUT_SECONDS,
        )
        try:
            value = json.loads(body)
            run = value["run"]
            if not isinstance(run, dict):
                raise TypeError("run must be an object")
        except (json.JSONDecodeError, UnicodeDecodeError, KeyError, TypeError) as exc:
            raise RuntimeErrorAF("Piston returned an unexpected execution response") from exc
        compile_result = value.get("compile") or {}
        compile_stderr = compile_result.get("stderr", "") if isinstance(compile_result, dict) else ""
        compile_stdout = compile_result.get("stdout", "") if isinstance(compile_result, dict) else ""
        exit_code = run.get("code")
        signal = run.get("signal")
        if exit_code is not None and (isinstance(exit_code, bool) or not isinstance(exit_code, int)):
            raise RuntimeErrorAF("Piston returned an invalid exit code")
        if signal is not None and not isinstance(signal, str):
            raise RuntimeErrorAF("Piston returned an invalid signal")
        return ExecutionResult(
            provider=self.name,
            language=str(value.get("language", request.language)),
            version=str(value.get("version", request.version)),
            stdout=str(run.get("stdout", "")),
            stderr=str(compile_stderr) + str(run.get("stderr", "")),
            exit_code=exit_code,
            signal=signal,
            metadata={
                "compile_stdout": str(compile_stdout),
                "compile_stderr": str(compile_stderr),
                "output": str(run.get("output", "")),
            },
        )


class CodeInterpreterProvider:
    """Client for the imported Code Interpreter HTTP service.

    Its /execute endpoint emits newline-delimited JSON events (not a single
    JSON document). Use a persistent context only when the caller explicitly
    supplies a context ID; otherwise the service's default Python context is used.
    """

    name = "code-interpreter"

    def __init__(self, base_url: str | None = None, access_token: str | None = None):
        self.base_url = _base_url(
            base_url or os.environ.get("ASSAYFLUX_CODE_INTERPRETER_URL", "http://127.0.0.1:8000"),
            env_name="ASSAYFLUX_CODE_INTERPRETER_URL",
        )
        self.access_token = (
            access_token
            if access_token is not None
            else os.environ.get("ASSAYFLUX_CODE_INTERPRETER_TOKEN")
        )

    def health(self) -> bool:
        body, _ = _request_json(
            f"{self.base_url}/health",
            method="GET",
            timeout=_DEFAULT_HTTP_TIMEOUT_SECONDS,
        )
        return body.strip().strip(b'"') == b"OK"

    def execute(self, request: ExecutionRequest) -> ExecutionResult:
        _validate_request(request)
        if request.context_id and request.language:
            raise SecurityError("Specify either a code-interpreter context ID or a language, not both")
        if request.version is not None or request.stdin or request.args:
            raise SecurityError("The Code Interpreter service does not support runtime versions, stdin, or program arguments")
        payload: dict[str, Any] = {"code": request.code}
        if request.context_id:
            payload["context_id"] = request.context_id
        elif request.language:
            payload["language"] = request.language
        headers = {}
        if self.access_token:
            headers["X-Access-Token"] = self.access_token
        body, _ = _request_json(
            f"{self.base_url}/execute",
            method="POST",
            payload=payload,
            headers=headers,
            timeout=request.timeout_seconds + _DEFAULT_HTTP_TIMEOUT_SECONDS,
        )
        events: list[dict[str, Any]] = []
        stdout: list[str] = []
        stderr: list[str] = []
        exit_code: int | None = 0
        context_id = request.context_id
        try:
            for raw_line in body.decode("utf-8").splitlines():
                if not raw_line.strip():
                    continue
                event = json.loads(raw_line)
                if not isinstance(event, dict):
                    continue
                events.append(event)
                kind = str(event.get("type", ""))
                if kind == "stdout":
                    stdout.append(str(event.get("text", event.get("data", ""))))
                elif kind == "stderr":
                    stderr.append(str(event.get("text", event.get("data", ""))))
                elif kind == "error":
                    stderr.append(str(event.get("traceback", event.get("error", event.get("text", "Execution failed")))))
                    exit_code = 1
                elif kind == "end_of_execution":
                    continue
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise RuntimeErrorAF("Code Interpreter returned malformed streaming JSON") from exc
        if not events or events[-1].get("type") not in {"end_of_execution", "unexpected_end_of_execution"}:
            raise RuntimeErrorAF(
                "Code Interpreter stream ended before the completion marker",
                suggestion="Check the sandbox service and its execution logs.",
            )
        if events[-1].get("type") == "unexpected_end_of_execution":
            exit_code = 1
        return ExecutionResult(
            provider=self.name,
            language=request.language or "python",
            stdout="".join(stdout),
            stderr="\n".join(part for part in stderr if part),
            exit_code=exit_code,
            context_id=context_id,
            outputs=events,
        )


PROVIDER_API_VERSION = "1.0"
_PROVIDER_FACTORIES = {
    "piston": PistonProvider,
    "code-interpreter": CodeInterpreterProvider,
}


def get_provider(name: str) -> ExecutionProvider:
    """Construct a configured provider by its stable CLI identifier."""
    factory = _PROVIDER_FACTORIES.get(name)
    if factory is None:
        supported = ", ".join(sorted(_PROVIDER_FACTORIES))
        raise SecurityError(
            f"Unknown execution provider '{name}'",
            suggestion=f"Choose one of: {supported}.",
        )
    return factory()
