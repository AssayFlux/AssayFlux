from __future__ import annotations

from unittest.mock import patch

from assayflux.execution.registry import list_languages


def test_registry_uses_live_piston_inventory_and_marks_default_interpreter():
    runtimes = [
        {"language": "python", "version": "3.12.0", "aliases": ["py"]},
        {"language": "typescript", "version": "5.0.0", "aliases": ["ts"]},
    ]
    with patch("assayflux.execution.registry.PistonProvider.list_runtimes", return_value=runtimes):
        languages = list_languages("auto")

    assert any(
        item["language"] == "typescript" and item["provider"] == "piston"
        and item["status"] == "available" and item["versions"] == ["5.0.0"]
        for item in languages
    )
    assert any(
        item["language"] == "python" and item["provider"] == "code-interpreter"
        and item["status"] == "configured-default"
        for item in languages
    )


def test_registry_auto_tolerates_piston_unavailable_but_provider_specific_does_not():
    from assayflux.diagnostics.model import RuntimeErrorAF

    with patch("assayflux.execution.registry.PistonProvider.list_runtimes", side_effect=RuntimeErrorAF("offline")):
        assert list_languages("auto")[0]["provider"] == "code-interpreter"
        try:
            list_languages("piston")
        except RuntimeErrorAF:
            pass
        else:
            raise AssertionError("provider-specific listing must surface provider failure")


def test_languages_cli_emits_machine_readable_inventory(capsys, monkeypatch):
    from assayflux.cli import main

    monkeypatch.setattr(
        "assayflux.execution.registry.list_languages",
        lambda provider: [
            {"language": "python", "provider": "code-interpreter",
             "status": "configured-default", "versions": [], "aliases": ["py"]}
        ],
    )
    assert main(["languages", "--json"]) == 0
    import json
    payload = json.loads(capsys.readouterr().out)
    assert payload[0]["language"] == "python"


def test_auto_execution_routes_versioned_requests_to_piston(monkeypatch, capsys):
    from assayflux.cli import main

    class FakeProvider:
        def execute(self, request):
            from assayflux.execution.models import ExecutionResult
            return ExecutionResult(provider="piston", language=request.language or "python",
                                   version=request.version, stdout="42\\n", exit_code=0)

    monkeypatch.setattr("assayflux.cli.get_provider", lambda name: (
        FakeProvider() if name == "piston" else (_ for _ in ()).throw(AssertionError(name))
    ))
    status = main(["execute", "--allow-external-execution", "--language", "python",
                   "--version", "3.12.0", "--code", "print(6*7)"])
    assert status == 0
    assert capsys.readouterr().out == "42\\n"
