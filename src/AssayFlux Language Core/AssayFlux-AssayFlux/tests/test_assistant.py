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
