"""Named guard rails. A checkpoint returns only after its contract is satisfied."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from assayflux.diagnostics.model import SecurityError, SourceError, SourceLocation


@dataclass(frozen=True, slots=True)
class SecurityPolicy:
    max_source_bytes: int = 1_000_000
    max_value_bytes: int = 8_000_000
    max_line_chars: int = 100_000
    max_steps: int = 100_000
    max_loop_iterations: int = 10_000
    max_output_chars: int = 1_000_000
    max_numeric_bits: int = 4096
    allowed_python_modules: tuple[str, ...] = ("math", "statistics", "json")
    allowed_python_calls: tuple[str, ...] = ()
    capabilities: tuple[str, ...] = ()
    allow_file_imports: bool = False
    allow_network: bool = False

def validate_source(source: str, filename: str, policy: SecurityPolicy) -> str:
    if not isinstance(source, str): raise SourceError("Source must be UTF-8 text", location=SourceLocation(filename))
    try:
        size = len(source.encode("utf-8", errors="strict"))
    except UnicodeEncodeError as exc:
        raise SourceError("Source contains invalid Unicode surrogate data", location=SourceLocation(filename)) from exc
    if size > policy.max_source_bytes:
        raise SecurityError("Source exceeds configured size limit", location=SourceLocation(filename),
                            details=f"Limit: {policy.max_source_bytes} bytes; received: {size} bytes")
    if "\x00" in source:
        raise SourceError("Source contains a NUL character", location=SourceLocation(filename))
    for line_no,line in enumerate(source.splitlines(),1):
        if len(line)>policy.max_line_chars:
            raise SecurityError("Source line exceeds configured length limit",location=SourceLocation(filename,line_no,policy.max_line_chars+1),details=f"Limit: {policy.max_line_chars} characters")
    return source

def read_source(path: Path, policy: SecurityPolicy) -> str:
    try:
        resolved = path.resolve(strict=True)
        if not resolved.is_file(): raise SourceError("Source path is not a regular file", location=SourceLocation(str(path)))
        if resolved.stat().st_size > policy.max_source_bytes:
            raise SecurityError("Source exceeds configured size limit", location=SourceLocation(str(path)))
        with resolved.open("rb") as stream:
            data = stream.read(policy.max_source_bytes + 1)
        if len(data) > policy.max_source_bytes:
            raise SecurityError("Source exceeds configured size limit", location=SourceLocation(str(resolved)),
                                details=f"Limit: {policy.max_source_bytes} bytes")
        source = data.decode("utf-8", errors="strict")
    except (OSError, UnicodeDecodeError) as exc:
        raise SourceError("Unable to read source file", location=SourceLocation(str(path)), details=type(exc).__name__) from exc
    return validate_source(source, str(resolved), policy)
