"""Stable public integration surface for AssayFlux language services.

Operating-system layers and third-party integrations should depend on this module,
not import parser, semantic, runtime, or security implementation modules directly.
The public API is a compatibility boundary; internal modules may evolve behind it.
"""
from __future__ import annotations

from assayflux.language.parser import parse
from assayflux.language.semantic import check
from assayflux.runtime.interpreter import ExecutionResult, Interpreter
from assayflux.security.checkpoints import SecurityPolicy, read_source, validate_source

__all__ = [
    "ExecutionResult",
    "Interpreter",
    "SecurityPolicy",
    "check",
    "parse",
    "read_source",
    "validate_source",
]
