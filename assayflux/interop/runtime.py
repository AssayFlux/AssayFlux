"""Unified execution interface for AssayFlux language adapters."""

from assayflux.interop.base import ExecutionResult
from assayflux.interop.loader import get_adapter


def execute_code(
    language: str,
    source: str,
    *,
    timeout: float = 10.0,
) -> ExecutionResult:
    """Execute source code using the Universal Adapter."""
    if not isinstance(language, str) or not language.strip():
        raise ValueError("Language must be a non-empty string.")

    if not isinstance(source, str):
        raise ValueError("Source code must be a string.")

    if not source.strip():
        raise ValueError("Source code must not be empty.")

    adapter = get_adapter(language)

    # UniversalAdapter needs the language name
    return adapter.execute(source, language=language, timeout=timeout)


def dispatch(
    language: str,
    source: str,
    *,
    timeout: float = 10.0,
) -> ExecutionResult:
    """Dispatch source code to the selected language via Universal Adapter."""
    return execute_code(language, source, timeout=timeout)


__all__ = ["execute_code", "dispatch", "ExecutionResult"]