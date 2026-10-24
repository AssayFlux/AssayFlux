from __future__ import annotations

import json
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
