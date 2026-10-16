"""
Core interfaces for AssayFlux language interoperability.

This module defines the common execution-result format and the
abstract interface that every language adapter must implement.

All adapters should return the same ExecutionResult structure,
regardless of the language or execution mechanism.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
import math


@dataclass(frozen=True, slots=True)
class ExecutionResult:
    """
    Standardized result of a language execution.

    Attributes:
        language:
            Canonical language identifier.

        stdout:
            Standard output produced by the execution.

        stderr:
            Standard error produced by the execution.

        returncode:
            Process-style exit code. Zero means success.

        duration:
            Execution duration in seconds.

    This result object is immutable so that its recorded outcome
    cannot accidentally be modified after execution.
    """

    language: str
    stdout: str = ""
    stderr: str = ""
    returncode: int = 0
    duration: float = 0.0

    def __post_init__(self) -> None:
        """Validate the execution result's public fields."""

        if not isinstance(self.language, str):
            raise TypeError("language must be a string.")

        normalized_language = self.language.strip().lower()

        if not normalized_language:
            raise ValueError("language must not be empty.")

        if not isinstance(self.stdout, str):
            raise TypeError("stdout must be a string.")

        if not isinstance(self.stderr, str):
            raise TypeError("stderr must be a string.")

        if isinstance(self.returncode, bool) or not isinstance(
            self.returncode, int
        ):
            raise TypeError("returncode must be an integer.")

        if isinstance(self.duration, bool) or not isinstance(
            self.duration, (int, float)
        ):
            raise TypeError("duration must be a number.")

        if not math.isfinite(self.duration) or self.duration < 0:
            raise ValueError(
                "duration must be a finite, non-negative number."
            )

        object.__setattr__(self, "language", normalized_language)
        object.__setattr__(self, "duration", float(self.duration))

    @property
    def success(self) -> bool:
        """Whether execution completed with exit code zero."""

        return self.returncode == 0

    @property
    def exit_code(self) -> int:
        """
        Compatibility alias for returncode.

        Some existing adapter implementations use exit_code.
        Keeping this alias avoids unnecessary breakage.
        """

        return self.returncode


class LanguageAdapter(ABC):
    """
    Abstract base class for a language-specific adapter.

    Each adapter represents one canonical target language.

    Examples:
        PythonAdapter.language == "python"
        JavaScriptAdapter.language == "javascript"

    An adapter must report whether its required runtime is available
    and implement the standard execute() interface.
    """

    @property
    @abstractmethod
    def language(self) -> str:
        """Return the adapter's canonical language identifier."""

        raise NotImplementedError

    @abstractmethod
    def is_available(self) -> bool:
        """
        Return whether the required execution toolchain is available.

        This method must only inspect the environment. It must not
        execute arbitrary user-supplied source code.
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
        Execute source code in this adapter's target language.

        Args:
            source:
                Source code written in the target language.

            timeout:
                Maximum allowed execution time, in seconds.

        Returns:
            A standardized ExecutionResult.

        Raises:
            TypeError:
                If source or timeout has an invalid type.

            ValueError:
                If source or timeout has an invalid value.

            RuntimeError:
                If the execution environment cannot be started
                or managed.

        Implementations must not claim that arbitrary code is safe
        merely because it runs in a temporary directory.
        """

        raise NotImplementedError