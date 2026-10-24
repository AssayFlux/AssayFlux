"""Backend-neutral execution request and result models."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Protocol, runtime_checkable


@dataclass(frozen=True, slots=True)
class ExecutionRequest:
    code: str
    language: str | None = None
    version: str | None = None
    filename: str = "main.py"
    stdin: str = ""
    args: tuple[str, ...] = ()
    timeout_seconds: int = 10
    context_id: str | None = None


@dataclass(slots=True)
class ExecutionResult:
    provider: str
    language: str
    version: str | None = None
    stdout: str = ""
    stderr: str = ""
    exit_code: int | None = None
    signal: str | None = None
    context_id: str | None = None
    outputs: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@runtime_checkable
class ExecutionProvider(Protocol):
    """Stable interface implemented by external execution backends."""

    name: str

    def execute(self, request: ExecutionRequest) -> ExecutionResult:
        """Execute a request and return normalized output."""
        ...
