"""
Default language adapter loader for AssayFlux.

Uses only the Universal Adapter.
All language requests (python, javascript, rust, go, etc.)
are routed through UniversalAdapter.
"""

from functools import lru_cache
from typing import Tuple

from assayflux.interop.registry import AdapterRegistry
from assayflux.interop.base import LanguageAdapter


@lru_cache(maxsize=1)
def get_default_registry() -> AdapterRegistry:
    """Create and cache the default adapter registry with Universal Adapter only."""
    from assayflux.interop.adapters.universal_adapter import UniversalAdapter

    registry = AdapterRegistry()
    registry.register(UniversalAdapter(), replace=True)
    return registry


def get_adapter(language: str) -> LanguageAdapter:
    """
    Retrieve an adapter for the requested language.

    Always returns the Universal Adapter.
    The actual language is handled inside UniversalAdapter.execute().
    """
    # We ignore the specific language name here and always return universal.
    # The language name is passed later to execute().
    return get_default_registry().get("universal")


def available_languages() -> Tuple[str, ...]:
    """
    Return the languages currently available on this system
    according to the Universal Adapter.
    """
    adapter = get_default_registry().get("universal")

    # UniversalAdapter has its own available_languages() method
    if hasattr(adapter, "available_languages"):
        return tuple(sorted(adapter.available_languages()))

    return ("universal",)