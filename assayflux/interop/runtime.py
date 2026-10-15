"""
Public execution API for AssayFlux language interoperability.

This module provides a common interface for executing source code
through registered language adapters.
"""

from assayflux.interop.base import ExecutionResult
from assayflux.interop.loader import get_adapter


def execute_code(
    language: str,
    source: str,
    *,
    timeout: float = 10.0,
) -> ExecutionResult:
    """
    Execute source code using a registered language adapter.

    Args:
        language: Language identifier, such as "python".
        source: Source code written in the requested language.
        timeout: Maximum permitted execution time in seconds.

    Returns:
        An ExecutionResult containing output, errors, and exit status.

    Raises:
        ValueError: If the language, source, or timeout is invalid.
        KeyError: If the requested language is not registered.
        RuntimeError: If execution cannot be started or managed.

    Security:
        This function does not provide a security sandbox.
        Only execute trusted source code.
    """
    if not isinstance(language, str) or not language.strip():
        raise ValueError("Language must be a non-empty string.")

    if not isinstance(source, str):
        raise ValueError("Source code must be a string.")

    if not source.strip():
        raise ValueError("Source code must not be empty.")

    return get_adapter(language).execute(
        source,
        timeout=timeout,
    )


__all__ = [
    "execute_code",
    "ExecutionResult",
]