from __future__ import annotations

from unittest.mock import patch

import pytest

from assayflux.assistant import OfflineAssistant
from assayflux.diagnostics.model import SecurityError


def test_assistant_defaults_to_loopback():
    assistant = OfflineAssistant()
    assert assistant.base_url == "http://127.0.0.1:11434"
    assert assistant.model


def test_assistant_rejects_remote_endpoint_by_default():
    with pytest.raises(SecurityError):
        OfflineAssistant(base_url="http://192.0.2.10:11434")


def test_assistant_deterministic_fallback_when_local_model_is_unavailable():
    assistant = OfflineAssistant()
    with patch.object(assistant, "_request", side_effect=Exception("offline")):
        result = assistant.diagnose("SyntaxError: unexpected token")
    assert result["provider"] == "deterministic-fallback"
    assert result["requires_review"] is True
