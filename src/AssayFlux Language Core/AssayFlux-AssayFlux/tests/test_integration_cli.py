from __future__ import annotations

import json

from assayflux.cli import main


def test_quantum_cli_runs_validated_circuit_with_mocked_provider(monkeypatch, capsys):
    monkeypatch.setattr(
        "assayflux.quantum.run_circuit",
        lambda circuit: {"provider": "pennylane", "probabilities": [1.0, 0.0]},
    )
    assert main(["quantum", "run", "--circuit", json.dumps({"wires": 1, "gates": []})]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["provider"] == "pennylane"


def test_assistant_cli_uses_diagnostic_result(monkeypatch, capsys):
    from assayflux.assistant import OfflineAssistant

    monkeypatch.setattr(
        OfflineAssistant,
        "diagnose",
        lambda self, error, context="": {
            "provider": "deterministic-fallback",
            "cause": error,
            "requires_review": True,
        },
    )
    assert main(["assistant", "diagnose", "--error", "example failure"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["cause"] == "example failure"
    assert result["requires_review"] is True


def test_native_failure_can_request_local_assistant_diagnosis(monkeypatch, capsys):
    from assayflux.assistant import OfflineAssistant

    called = {}
    monkeypatch.setattr(
        OfflineAssistant,
        "diagnose",
        lambda self, error, context="": called.update(error=error, context=context) or {
            "provider": "deterministic-fallback",
            "cause": error,
            "requires_review": True,
        },
    )
    assert main(["check", "not-an-assayflux-file.txt", "--assist"]) == 1
    stderr = capsys.readouterr().err
    assert "deterministic-fallback" in stderr
    assert "not-an-assayflux-file.txt" not in called["error"]
    assert called["context"] == "AssayFlux command: check"
