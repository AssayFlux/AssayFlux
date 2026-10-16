"""
AssayFlux interoperability runtime.

Provides the central execution interface for language adapters.

Public functions:
    dispatch(language, source, timeout=10.0)
    execute_code(language, source, timeout=10.0)

The runtime delegates language-specific execution to the adapter
loader and returns a shared ExecutionResult object.
"""

from __future__ import annotations

import math
from typing import Any, Callable

from assayflux.interop.base import ExecutionResult
from assayflux.interop.loader import get_adapter


class InteropRuntimeRegistry:
    """
    Registry for custom interoperability handlers.

    This class is retained for compatibility with existing
    integrations that register their own execution handlers.
    """

    def __init__(self) -> None:
        self._registry: dict[str, Callable[[dict], Any]] = {}

    def register(
        self,
        language: str,
        handler: Callable[[dict], Any],
    ) -> None:
        """Register a callable handler for a language identifier."""
        if not isinstance(language, str):
            raise TypeError("Language name must be a string.")

        normalized = language.strip().lower()

        if not normalized:
            raise ValueError("Language name must not be empty.")

        if not callable(handler):
            raise TypeError(
                f"Handler for '{normalized}' must be callable."
            )

        self._registry[normalized] = handler

    def execute(
        self,
        language: str,
        payload: dict,
    ) -> Any:
        """Execute a registered handler with a dictionary payload."""
        if not isinstance(language, str):
            raise TypeError("Language name must be a string.")

        normalized = language.strip().lower()

        if normalized not in self._registry:
            raise KeyError(
                "Unsupported interoperability language target: "
                f"{language!r}"
            )

        if not isinstance(payload, dict):
            raise TypeError(
                "Interop execution payload must be a dictionary."
            )

        handler = self._registry[normalized]

        try:
            return handler(payload)
        except Exception as exc:
            raise RuntimeError(
                f"Error executing interop for '{normalized}': {exc}"
            ) from exc


def dispatch(
    language: str,
    source: str,
    timeout: float = 10.0,
) -> ExecutionResult:
    """
    Execute source code using the requested language adapter.

    Args:
        language: Language name or supported alias.
        source: Source code to execute.
        timeout: Maximum execution time in seconds.

    Returns:
        ExecutionResult containing stdout, stderr, returncode,
        language, and duration.

    Raises:
        TypeError: If an argument has an invalid type.
        ValueError: If timeout is not finite and positive.
        KeyError: If the language is not supported.
    """
    if not isinstance(language, str):
        raise TypeError("Language name must be a string.")

    if not isinstance(source, str):
        raise TypeError("Source code must be a string.")

    if isinstance(timeout, bool) or not isinstance(
        timeout, (int, float)
    ):
        raise TypeError("Timeout must be a number.")

    if not math.isfinite(timeout) or timeout <= 0:
        raise ValueError(
            "Timeout must be a finite positive number."
        )

    adapter = get_adapter(language)

    return adapter.execute(
        source,
        timeout=float(timeout),
    )


def execute_code(
    language: str,
    source: str,
    timeout: float = 10.0,
) -> ExecutionResult:
    """
    Compatibility wrapper for executing code.

    This function intentionally delegates to dispatch(), ensuring
    both public entry points use the same execution behavior.
    """
    return dispatch(
        language=language,
        source=source,
        timeout=timeout,
    )


__all__ = [
    "InteropRuntimeRegistry",
    "dispatch",
    "execute_code",
]