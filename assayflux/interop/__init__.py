"""AssayFlux language interoperability."""

from assayflux.interop.base import ExecutionResult, LanguageAdapter
from assayflux.interop.loader import (
    available_languages,
    get_adapter,
    get_default_registry,
)
from assayflux.interop.runtime import dispatch, execute_code

__version__ = "0.1.0"

__all__ = [
    "ExecutionResult",
    "LanguageAdapter",
    "available_languages",
    "dispatch",
    "execute_code",
    "get_adapter",
    "get_default_registry",
]