"""
Python language adapter for AssayFlux.

Executes Python source code in a separate Python process and
normalizes its output into an AssayFlux ExecutionResult.
"""

import math
import shutil
import subprocess
import sys

from assayflux.interop.base import ExecutionResult, LanguageAdapter


class PythonAdapter(LanguageAdapter):
    """Execute Python source code through the current Python runtime."""

    @property
    def language(self) -> str:
        """Return the canonical language identifier."""
        return "python"

    def is_available(self) -> bool:
        """Check whether the current Python executable is available."""
        return shutil.which(sys.executable) is not None

    def execute(
        self,
        source: str,
        *,
        timeout: float = 10.0,
    ) -> ExecutionResult:
        """
        Execute Python source code in a separate process.

        Args:
            source: Python source code to execute.
            timeout: Maximum execution time in seconds.

        Returns:
            An ExecutionResult containing stdout, stderr, and exit code.

        Raises:
            ValueError: If source or timeout is invalid.
            RuntimeError: If the process cannot be started or managed.

        Note:
            A subprocess is not a security sandbox. Only execute
            trusted source code.
        """
        if not isinstance(source, str):
            raise ValueError("Python source must be a string.")

        if not source.strip():
            raise ValueError("Python source must not be empty.")

        if isinstance(timeout, bool) or not isinstance(timeout, (int, float)):
            raise ValueError("Timeout must be a positive number of seconds.")

        if not math.isfinite(timeout) or timeout <= 0:
            raise ValueError("Timeout must be a finite positive number.")

        if not self.is_available():
            raise RuntimeError("The current Python runtime is unavailable.")

        try:
            completed = subprocess.run(
                [
                    sys.executable,
                    "-I",
                    "-c",
                    source,
                ],
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
            )

            return ExecutionResult(
                language=self.language,
                stdout=completed.stdout,
                stderr=completed.stderr,
                returncode=completed.returncode,
            )

        except subprocess.TimeoutExpired as exc:
            stdout = exc.stdout or ""
            stderr = exc.stderr or ""

            if isinstance(stdout, bytes):
                stdout = stdout.decode("utf-8", errors="replace")

            if isinstance(stderr, bytes):
                stderr = stderr.decode("utf-8", errors="replace")

            timeout_message = (
                f"Python execution exceeded the {timeout}-second timeout."
            )

            if stderr:
                stderr = f"{stderr.rstrip()}\n{timeout_message}\n"
            else:
                stderr = f"{timeout_message}\n"

            return ExecutionResult(
                language=self.language,
                stdout=stdout,
                stderr=stderr,
                returncode=124,
            )

        except OSError as exc:
            raise RuntimeError(
                f"Could not start the Python process: {exc}"
            ) from exc