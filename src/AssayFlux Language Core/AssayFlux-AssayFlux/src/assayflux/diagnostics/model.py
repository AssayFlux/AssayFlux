"""Stable diagnostic model shared by compiler stages and runtime."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any


class Severity(StrEnum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    HINT = "hint"

@dataclass(frozen=True, slots=True)
class SourceLocation:
    file: str = "<memory>"
    line: int = 1
    column: int = 1
    end_line: int | None = None
    end_column: int | None = None

@dataclass(frozen=True, slots=True)
class Diagnostic:
    code: str
    category: str
    severity: Severity
    message: str
    location: SourceLocation = field(default_factory=SourceLocation)
    details: str | None = None
    suggestion: str | None = None
    cause_type: str | None = None
    stack: tuple[str, ...] = ()
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

class AssayFluxError(Exception):
    code = "AF-INTERNAL-001"
    category = "internal"
    def __init__(self, message: str, *, location: SourceLocation | None = None,
                 details: str | None = None, suggestion: str | None = None):
        super().__init__(message)
        self.message = message
        self.location = location or SourceLocation()
        self.details = details
        self.suggestion = suggestion
    def diagnostic(self) -> Diagnostic:
        return Diagnostic(self.code, self.category, Severity.ERROR, self.message,
                          self.location, self.details, self.suggestion, type(self).__name__)

class SourceError(AssayFluxError): code = "AF-SOURCE-001"; category = "source"
class LexError(AssayFluxError): code = "AF-LEX-001"; category = "lexical"
class ParseError(AssayFluxError): code = "AF-PARSE-001"; category = "syntax"
class AstError(AssayFluxError): code = "AF-AST-001"; category = "ast"
class TypeCheckError(AssayFluxError): code = "AF-TYPE-001"; category = "type"
class SecurityError(AssayFluxError): code = "AF-SEC-001"; category = "security"
class RuntimeErrorAF(AssayFluxError): code = "AF-RUNTIME-001"; category = "runtime"
class ImportErrorAF(AssayFluxError): code = "AF-IMPORT-001"; category = "import"
class PythonBridgeError(AssayFluxError): code = "AF-PYTHON-001"; category = "python-interop"
class DatabaseErrorAF(AssayFluxError): code = "AF-SQL-001"; category = "database"
class BuildError(AssayFluxError): code = "AF-BUILD-001"; category = "build"
