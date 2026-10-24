"""Local-first diagnostic assistant adapter using the Ollama HTTP API.

The assistant explains errors and proposes bounded suggestions; it never executes
or applies generated code. If the local model is unavailable, a deterministic
fallback is returned instead of silently using a cloud service.
"""
from __future__ import annotations

import json
import os
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

from assayflux.diagnostics.model import RuntimeErrorAF, SecurityError

_MAX_TEXT = 20_000
_MAX_RESPONSE = 1_000_000


def _endpoint(value: str) -> str:
    value = value.strip().rstrip("/")
    parsed = urlsplit(value)
    if (
        parsed.scheme not in {"http", "https"} or not parsed.hostname
        or parsed.username is not None or parsed.password is not None
        or parsed.query or parsed.fragment
    ):
        raise SecurityError("Invalid local assistant URL")
    if parsed.hostname not in {"127.0.0.1", "localhost", "::1"} and os.environ.get(
        "ASSAYFLUX_ASSISTANT_ALLOW_REMOTE", ""
    ).lower() not in {"1", "true", "yes"}:
        raise SecurityError(
            "Assistant endpoint must be loopback by default",
            suggestion="Use a local Ollama service or explicitly review and enable remote access.",
        )
    return value


class OfflineAssistant:
    """Use a local Ollama model for diagnostics; no cloud fallback is performed."""

    def __init__(self, base_url: str | None = None, model: str | None = None):
        self.base_url = _endpoint(
            base_url or os.environ.get("ASSAYFLUX_ASSISTANT_URL", "http://127.0.0.1:11434")
        )
        self.model = (model or os.environ.get("ASSAYFLUX_ASSISTANT_MODEL", "llama3.2")).strip()
        if not self.model or len(self.model) > 120:
            raise SecurityError("Assistant model name must contain 1-120 characters")

    def _request(self, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        data = None if payload is None else json.dumps(payload).encode("utf-8")
        request = Request(
            f"{self.base_url}{path}", data=data,
            headers={"Accept": "application/json", **({"Content-Type": "application/json"} if data else {})},
            method="GET" if data is None else "POST",
        )
        try:
            with urlopen(request, timeout=10) as response:
                raw = response.read(_MAX_RESPONSE + 1)
            if len(raw) > _MAX_RESPONSE:
                raise RuntimeErrorAF("Local assistant response exceeded the 1 MB limit")
            result = json.loads(raw.decode("utf-8"))
            if not isinstance(result, dict):
                raise RuntimeErrorAF("Local assistant returned an invalid response")
            return result
        except HTTPError as exc:
            raise RuntimeErrorAF(
                f"Local assistant returned HTTP {exc.code}",
                suggestion="Check that Ollama is running and the requested model is available.",
            ) from exc
        except (URLError, TimeoutError, OSError) as exc:
            raise RuntimeErrorAF(
                "Local assistant is unavailable",
                details=type(exc).__name__,
                suggestion="Start the local model service or use the deterministic diagnostic fallback.",
            ) from exc
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise RuntimeErrorAF("Local assistant returned invalid JSON") from exc

    def health(self) -> dict[str, Any]:
        """Return health and locally installed model names."""
        result = self._request("/api/tags")
        models = result.get("models", [])
        if not isinstance(models, list):
            models = []
        return {
            "available": True,
            "provider": "ollama-local",
            "models": [
                item.get("name") for item in models
                if isinstance(item, dict) and isinstance(item.get("name"), str)
            ],
        }

    def diagnose(self, error: str, context: str = "") -> dict[str, Any]:
        """Explain a failure with a local model or return deterministic guidance."""
        if not isinstance(error, str) or not error.strip() or len(error) > _MAX_TEXT:
            raise SecurityError("Diagnostic error must be non-empty text up to 20,000 characters")
        if not isinstance(context, str) or len(context) > _MAX_TEXT:
            raise SecurityError("Diagnostic context must be text up to 20,000 characters")
        fallback = {
            "provider": "deterministic-fallback",
            "cause": error.strip()[:500],
            "suggestions": [
                "Inspect the first error message and the file/line it identifies.",
                "Make one small change at a time, then rerun AssayFlux validation and tests.",
            ],
            "confidence": "low",
            "requires_review": True,
        }
        try:
            result = self._request("/api/chat", {
                "model": self.model,
                "stream": False,
                "format": "json",
                "messages": [
                    {"role": "system", "content": (
                        "You are a local software diagnostic assistant. Do not claim certainty "
                        "without evidence. Never execute code or apply changes. Return JSON with "
                        "cause (string), suggestions (array of strings), confidence (low/medium/high), "
                        "and uncertainty (string)."
                    )},
                    {"role": "user", "content": f"Error:\n{error}\n\nContext:\n{context}"},
                ],
                "options": {"temperature": 0.1},
            })
            message = result.get("message", {})
            content = message.get("content") if isinstance(message, dict) else None
            parsed = json.loads(content) if isinstance(content, str) else None
            if not isinstance(parsed, dict) or not isinstance(parsed.get("cause"), str):
                return fallback
            suggestions = parsed.get("suggestions", [])
            if not isinstance(suggestions, list):
                suggestions = []
            return {
                "provider": "ollama-local",
                "model": self.model,
                "cause": parsed["cause"][:2000],
                "suggestions": [s[:1000] for s in suggestions if isinstance(s, str)][:8],
                "confidence": parsed.get("confidence") if parsed.get("confidence") in {"low", "medium", "high"} else "low",
                "uncertainty": parsed.get("uncertainty", "Model uncertainty was not supplied."),
                "requires_review": True,
            }
        except (RuntimeErrorAF, SecurityError, json.JSONDecodeError):
            return fallback
