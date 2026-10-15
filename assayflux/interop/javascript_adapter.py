"""
JavaScript language adapter for AssayFlux.

Executes JavaScript source code through Node.js in a separate
process and normalizes its output into an AssayFlux ExecutionResult.

Node.js must be installed and available on PATH.
A subprocess is not a security sandbox. Only execute trusted code.
"""

import math
import shutil
import subprocess

from assayflux.interop.base import ExecutionResult, LanguageAdapter


class JavaScriptAdapter(LanguageAdapter):
    """Execute JavaScript source code using Node.js."""

    @property
    def language(self) -> str:
        """Return the canonical language identifier."""
        return "javascript"

    def is_available(self) -> bool:
        """Check whether Node.js is available."""
        return shutil.which("node") is not None

    def execute(
        self,
        source: str,
        *,
        timeout: float = 10.0,
    ) -> ExecutionResult:
        """
        Execute JavaScript source code in a separate Node.js process.

        Args:
            source: JavaScript source code.
            timeout: Maximum execution time in seconds.

        Returns:
            An ExecutionResult containing stdout, stderr, and exit code.

        Raises:
            ValueError: If source or timeout is invalid.
            RuntimeError: If Node.js is unavailable or cannot be started.

        Note:
            This adapter does not sandbox untrusted JavaScript.
        """
        if not isinstance(source, str):
            raise ValueError("JavaScript source must be a string.")

        if not source.strip():
            raise ValueError("JavaScript source must not be empty.")

        if isinstance(timeout, bool) or not isinstance(timeout, (int, float)):
            raise ValueError("Timeout must be a positive number of seconds.")

        if not math.isfinite(timeout) or timeout <= 0:
            raise ValueError("Timeout must be a finite positive number.")

        node_executable = shutil.which("node")

        if node_executable is None:
            raise RuntimeError(
                "Node.js is unavailable. Install Node.js and ensure "
                "the 'node' command is on PATH."
            )

        try:
            completed = subprocess.run(
                [
                    node_executable,
                    "-e",
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
                f"JavaScript execution exceeded the {timeout}-second timeout."
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
                f"Could not start the Node.js process: {exc}"
            ) from exc