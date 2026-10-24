"""Runtime inventory for the universal external-execution interface.

Entries are advertised only when a provider reports runtimes or passes its
health check. This is discovery, not a security/isolation certification.
"""
from __future__ import annotations

from typing import Any

from assayflux.diagnostics.model import RuntimeErrorAF, SecurityError
from assayflux.execution.providers import CodeInterpreterProvider, PistonProvider


def list_languages(provider: str = "auto") -> list[dict[str, Any]]:
    """Return normalized runtime inventory from healthy/configured providers."""
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
            # The service adapter has no runtime-list endpoint. Only its documented
            # default Python path is advertised, and only after a live health check.
            records.append({
                "language": "python",
                "provider": "code-interpreter",
                "status": "available",
                "versions": [],
                "aliases": ["py"],
            })
    return sorted(records, key=lambda item: (
        item["language"].casefold(), item["provider"], item["versions"]
    ))
