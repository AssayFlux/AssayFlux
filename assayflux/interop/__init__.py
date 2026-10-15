"""
AssayFlux Language Interoperability.

This package provides a common execution API for integrating
external programming languages into AssayFlux Scientific Systems.

Language adapters handle execution through their respective
installed runtimes. The package does not provide a security
sandbox, so only trusted source code should be executed.
"""

from assayflux.interop.base import ExecutionResult, LanguageAdapter
from assayflux.interop.loader import (
    available_languages,
    get_adapter,
    get_default_registry,
)
from assayflux.interop.runtime import execute_code

__version__ = "0.1.0"

__all__ = [
    "__version__",
    "ExecutionResult",
    "LanguageAdapter",
    "available_languages",
    "get_adapter",
    "get_default_registry",
    "execute_code",
]