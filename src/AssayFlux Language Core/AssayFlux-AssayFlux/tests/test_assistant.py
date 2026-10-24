from __future__ import annotations

from unittest.mock import patch

import pytest

from assayflux.assistant import OfflineAssistant
from assayflux.diagnostics.model import RuntimeErrorAF, SecurityError


def test_assistant_defaults_to_loopback():
    assistant = OfflineAssistant()
    assert assistant.base_url == "http://127.0.0.1:8080"
    assert assistant.model


def test_assistant_rejects_remote_endpoint_by_default():
    with pytest.raises(SecurityError):
        OfflineAssistant(base_url="http://192.0.2.10:11434")


def test_assistant_deterministic_fallback_when_local_model_is_unavailable():
    assistant = OfflineAssistant()
    with patch.object(assistant, "_request", side_effect=RuntimeErrorAF("offline")):
        result = assistant.diagnose("SyntaxError: unexpected token")
    assert result["provider"] == "deterministic-fallback"
    assert result["requires_review"] is True


def test_assistant_parses_structured_local_model_response():
    assistant = OfflineAssistant()
    response = {
        "message": {
            "content": '{"cause":"Missing import","suggestions":["Add the required import"],"confidence":"medium","uncertainty":"Check the module name."}'
        }
    }
    with patch.object(assistant, "_request", side_effect=[
        {"status": "ok"},
        {"configured": False, "connected": False},
        [{"name": "llama3.2"}],
        response,
    ]):
        result = assistant.diagnose("NameError: np is not defined")
    assert result["provider"] == "project-nomad-local"
    assert result["cause"] == "Missing import"
    assert result["suggestions"] == ["Add the required import"]
    assert result["confidence"] == "medium"
    assert result["requires_review"] is True


def test_nomad_installed_model_list_accepts_json_array():
    assistant = OfflineAssistant()

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self, limit):
            return b'[{"name":"llama3.2"}]'

    with patch("assayflux.assistant.urlopen", return_value=FakeResponse()):
        result = assistant._request("/api/ollama/installed-models")
    assert result == [{"name": "llama3.2"}]


def test_nomad_chat_payload_matches_supported_api_contract():
    assistant = OfflineAssistant()
    calls = []

    def fake_request(path, payload=None):
        calls.append((path, payload))
        if path == "/api/health":
            return {"status": "ok"}
        if path == "/api/ollama/remote-status":
            return {"configured": False, "connected": False}
        if path == "/api/ollama/installed-models":
            return [{"name": "llama3.2"}]
        return {"message": {"content": '{"cause":"Bad syntax","suggestions":["Check brackets"],"confidence":[],"uncertainty":17}'}}

    with patch.object(assistant, "_request", side_effect=fake_request):
        result = assistant.diagnose("SyntaxError: unexpected token")

    assert [path for path, _ in calls] == [
        "/api/health", "/api/ollama/remote-status",
        "/api/ollama/installed-models", "/api/ollama/chat"
    ]
    payload = calls[-1][1]
    assert payload["model"] == "llama3.2"
    assert payload["stream"] is False
    assert "format" not in payload and "options" not in payload
    assert result["cause"] == "Bad syntax"
    assert result["confidence"] == "low"
    assert result["uncertainty"] == "Model uncertainty was not supplied."


def test_assistant_handles_non_object_chat_response_without_crashing():
    assistant = OfflineAssistant()
    with patch.object(assistant, "_request", side_effect=[
        {"status": "ok"}, {"configured": False, "connected": False}, [{"name": "llama3.2"}], [{"unexpected": "list"}]
    ]):
        result = assistant.diagnose("Example error")
    assert result["provider"] == "deterministic-fallback"
    assert result["requires_review"] is True


def test_assistant_rejects_oversized_inputs():
    assistant = OfflineAssistant()
    with pytest.raises(SecurityError):
        assistant.diagnose("x" * 20_001)
    with pytest.raises(SecurityError):
        assistant.diagnose("error", "x" * 20_001)


def test_nomad_adapter_http_round_trip_against_loopback_stub():
    import json
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
    from threading import Thread

    seen = []

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_args):
            pass

        def do_GET(self):
            seen.append((self.path, None))
            if self.path == "/api/health":
                body = {"status": "ok"}
            elif self.path == "/api/ollama/remote-status":
                body = {"configured": False, "connected": False}
            elif self.path == "/api/ollama/installed-models":
                body = [{"name": "llama3.2"}]
            else:
                self.send_error(404)
                return
            data = json.dumps(body).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_POST(self):
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length))
            seen.append((self.path, payload))
            body = {"message": {"content": json.dumps({
                "cause": "Missing import",
                "suggestions": ["Verify the intended module before adding an import"],
                "confidence": "medium",
                "uncertainty": "The traceback alone cannot prove the intended module.",
            })}}
            data = json.dumps(body).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        assistant = OfflineAssistant(base_url=f"http://127.0.0.1:{server.server_port}")
        result = assistant.diagnose("NameError: np is not defined", "line 3")
        assert result["provider"] == "project-nomad-local"
        assert result["cause"] == "Missing import"
        assert result["requires_review"] is True
        assert [path for path, _ in seen] == [
            "/api/health", "/api/ollama/installed-models", "/api/ollama/chat"
        ]
        payload = seen[-1][1]
        assert payload["stream"] is False
        assert payload["model"] == "llama3.2"
        assert "format" not in payload and "options" not in payload
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
