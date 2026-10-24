"""Runtime registry for the universal external-execution interface.

Only runtimes reported by a live provider are marked available. This module does
not infer support from language names or claim that a service is isolated.
"""
from __future__ import annotations

from typing import Any

from assayflux.diagnostics.model import RuntimeErrorAF, SecurityError
from assayflux.execution.providers import CodeInterpreterProvider, PistonProvider


def list_languages(provider: str = "auto") -> list[dict[str, Any]]:
    """Return a normalized runtime inventory from configured providers."""
    if provider not in {"auto", "piston", "code-interpreter"}:
        raise SecurityError("Unknown language inventory provider")
    records: list[dict[str, Any]] = []
    if provider in {"auto", "piston"}:
        try:
            runtimes = PistonProvider().list_runtimes()
        except RuntimeErrorAF:
            if provider == "piston":
                raise
            runtimes = []
        for runtime in runtimes:
            language = runtime.get("language")
            version = runtime.get("version")
            if not isinstance(language, str) or not isinstance(version, str):
                continue
            aliases = runtime.get("aliases", [])
            if not isinstance(aliases, list):
                aliases = []
            records.append({
                "language": language,
                "provider": "piston",
                "status": "available",
                "versions": [version],
                "aliases": [alias for alias in aliases if isinstance(alias, str)],
            })
    if provider in {"auto", "code-interpreter"}:
        try:
            healthy = CodeInterpreterProvider().health()
        except RuntimeErrorAF:
            if provider == "code-interpreter":
                raise
            healthy = False
        if healthy:
            # No runtime-list endpoint exists; advertise only the default Python
            # path, and only after a live health check succeeds.
            records.append({
                "language": "python",
                "provider": "code-interpreter",
                "status": "available",
                "versions": [],
                "aliases": ["py"],
            })
    # Keep every provider/version combination; the same language can exist in
    # multiple versions or on multiple providers.
    return sorted(records, key=lambda item: (
        item["language"].casefold(), item["provider"], item["versions"]
    ))
