"""
Language adapter loader for AssayFlux.

Registers one MasterAdapter for each supported language.

Responsibilities:
- Normalize language names and aliases.
- Return the correct adapter for each language.
- Preserve the UniversalAdapter compatibility interface.
- Report available language runtimes.
- Reject unknown language names clearly.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Tuple

from assayflux.interop.base import LanguageAdapter
from assayflux.interop.registry import AdapterRegistry
from assayflux.interop.adapters.master_adapter import MasterAdapter


@lru_cache(maxsize=1)
def get_default_registry() -> AdapterRegistry:
    """
    Create and cache the default adapter registry.

    Each supported language receives its own configured
    MasterAdapter instance. The UniversalAdapter is also
    registered for backward compatibility.
    """
    from assayflux.interop.adapters.universal_adapter import (
        UniversalAdapter,
    )

    registry = AdapterRegistry()

    for language in MasterAdapter.registered_languages():
        registry.register(
            MasterAdapter(language),
            replace=True,
        )

    registry.register(
        UniversalAdapter(),
        replace=True,
    )

    return registry


def normalize_language(language: str) -> str:
    """
    Return the canonical name for a language or alias.

    Examples:
        js       -> javascript
        py       -> python
        c++      -> cpp
        rs       -> rust
        sqlite   -> sql
    """
    if not isinstance(language, str):
        raise KeyError(
            f"Unknown language: {language!r}"
        )

    normalized = language.strip().lower()

    if not normalized:
        raise KeyError("Language name must not be empty.")

    if normalized == "universal":
        return "universal"

    try:
        canonical = MasterAdapter.normalize_language(normalized)
    except (TypeError, ValueError) as exc:
        raise KeyError(
            f"Unknown language: {language!r}"
        ) from exc

    if canonical not in MasterAdapter.registered_languages():
        raise KeyError(
            f"Unknown language: {language!r}"
        )

    return canonical


def get_adapter(language: str) -> LanguageAdapter:
    """
    Retrieve the adapter for a requested language.

    Canonical language names and supported aliases are accepted.

    Raises:
        KeyError: If the requested language is not supported.
    """
    canonical = normalize_language(language)
    registry = get_default_registry()

    try:
        return registry.get(canonical)
    except KeyError as exc:
        raise KeyError(
            f"No adapter registered for language "
            f"{canonical!r}."
        ) from exc


def available_languages() -> Tuple[str, ...]:
    """
    Return canonical language names whose runtimes are available.

    HTML and CSS are static-asset targets. They do not require
    a separate language runtime.
    """
    registry = get_default_registry()

    available = []

    for language in MasterAdapter.registered_languages():
        try:
            adapter = registry.get(language)

            if adapter.is_available():
                available.append(language)

        except (KeyError, OSError):
            continue

    return tuple(sorted(available))


__all__ = [
    "get_default_registry",
    "get_adapter",
    "normalize_language",
    "available_languages",
]