"""Unified execution interface for AssayFlux language adapters."""

from assayflux.interop.base import ExecutionResult
from assayflux.interop.loader import get_adapter


def execute_code(
    language: str,
    source: str,
    *,
    timeout: float = 10.0,
) -> ExecutionResult:
    """Execute source code using a registered language adapter."""
    if not isinstance(language, str) or not language.strip():
        raise ValueError("Language must be a non-empty string.")

    if not isinstance(source, str):
        raise ValueError("Source code must be a string.")

    if not source.strip():
        raise ValueError("Source code must not be empty.")

    adapter = get_adapter(language)
    return adapter.execute(source, timeout=timeout)


def dispatch(
    language: str,
    source: str,
    *,
    timeout: float = 10.0,
) -> ExecutionResult:
    """Dispatch source code to the selected language adapter."""
    return execute_code(language, source, timeout=timeout)


__all__ = ["execute_code", "dispatch", "ExecutionResult"]