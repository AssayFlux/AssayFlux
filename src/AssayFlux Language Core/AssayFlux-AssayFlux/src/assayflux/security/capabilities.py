"""Explicit deny-by-default capability grants for privileged runtime operations."""
from __future__ import annotations

from enum import StrEnum

from assayflux.diagnostics.model import SecurityError, SourceLocation


class Capability(StrEnum):
    PYTHON_CALL = "python.call"
    DATABASE_READ = "database.read"
    DATABASE_WRITE = "database.write"
    NATIVE_BUILD = "native.build"
    FILESYSTEM_READ = "filesystem.read"
    FILESYSTEM_WRITE = "filesystem.write"
    NETWORK_CONNECT = "network.connect"
    SUBPROCESS_RUN = "subprocess.run"

class CapabilityManager:
    def __init__(self, grants=()): self._grants = frozenset(str(x) for x in grants)
    @property
    def grants(self): return self._grants
    def has(self, capability: str | Capability) -> bool: return str(capability) in self._grants
    def require(self, capability: str | Capability, *, operation: str | None = None,
                location: SourceLocation | None = None) -> None:
        name = str(capability)
        if name not in self._grants:
            raise SecurityError(f"Capability denied: {name}", location=location or SourceLocation(),
                                details=f"Operation requires explicit grant '{name}'.",
                                suggestion=f"Grant '{name}' from trusted project configuration only if this operation is necessary.")
