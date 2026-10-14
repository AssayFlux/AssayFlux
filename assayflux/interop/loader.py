"""
Default language adapter loader for AssayFlux.

This module constructs the default registry and registers
the language adapters available in this installation.
"""

from functools import lru_cache

from assayflux.interop.registry import AdapterRegistry


@lru_cache(maxsize=1)
def get_default_registry() -> AdapterRegistry:
    """
    Return the process-wide default adapter registry.

    The registry is initialized only once per Python process.
    """
    from assayflux.interop.adapters.python_adapter import PythonAdapter

    registry = AdapterRegistry()
    registry.register(PythonAdapter())

    return registry


def get_adapter(language: str):
    """
    Retrieve a registered adapter by language identifier.

    Args:
        language: Name of the requested programming language.

    Returns:
        The registered LanguageAdapter.

    Raises:
        ValueError: If the language identifier is invalid.
        KeyError: If no adapter is registered for that language.
    """
    return get_default_registry().get(language)


def available_languages() -> tuple[str, ...]:
    """Return registered languages whose runtimes are available."""
    return get_default_registry().available_languages()