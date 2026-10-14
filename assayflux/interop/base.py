"""
Shared interfaces for AssayFlux language integrations.

Every language adapter should follow the same public contract,
even when its underlying execution mechanism differs.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class ExecutionResult:
    """The result of executing code through a language adapter."""

    language: str
    stdout: str
    stderr: str
    returncode: int

    @property
    def success(self) -> bool:
        """Return True when execution completed successfully."""
        return self.returncode == 0


class LanguageAdapter(ABC):
    """
    Abstract base class for external language integrations.

    Subclasses must identify their language, report whether the
    required runtime is available, and implement code execution.
    """

    @property
    @abstractmethod
    def language(self) -> str:
        """Return the canonical language identifier."""
        raise NotImplementedError

    @abstractmethod
    def is_available(self) -> bool:
        """
        Return whether this adapter's required runtime is available.

        This method should check availability without executing
        user-supplied source code.
        """
        raise NotImplementedError

    @abstractmethod
    def execute(
        self,
        source: str,
        *,
        timeout: float = 10.0,
    ) -> ExecutionResult:
        """
        Execute source code and return a normalized result.

        Args:
            source: Source code written in the target language.
            timeout: Maximum permitted execution time in seconds.

        Returns:
            An ExecutionResult containing output, errors, and status.

        Raises:
            ValueError: If the source or timeout is invalid.
            RuntimeError: If execution cannot be started or managed.

        Implementations must document their execution environment
        and must not assume that arbitrary code is safe to execute.
        """
        raise NotImplementedError