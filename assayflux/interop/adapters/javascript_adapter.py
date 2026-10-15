"""
JavaScript language adapter for AssayFlux.

Executes JavaScript source code using Node.js.

Requirement:
- Node.js installed and available through the 'node' command.

Warning:
Executed programs are not sandboxed. Only run trusted code.
"""

import math
import shutil
import subprocess
import tempfile
from pathlib import Path

from assayflux.interop.base import ExecutionResult, LanguageAdapter


class JavaScriptAdapter(LanguageAdapter):
    """Execute JavaScript source code using Node.js."""

    @property
    def language(self) -> str:
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
        """Execute trusted JavaScript source code."""
        if not isinstance(source, str):
            raise ValueError("JavaScript source must be a string.")

        if not source.strip():
            raise ValueError("JavaScript source must not be empty.")

        if (
            isinstance(timeout, bool)
            or not isinstance(timeout, (int, float))
            or not math.isfinite(timeout)
            or timeout <= 0
        ):
            raise ValueError(
                "Timeout must be a finite positive number."
            )

        node = shutil.which("node")

        if node is None:
            raise RuntimeError(
                "JavaScript is unavailable. Install Node.js "
                "and ensure the 'node' command is on PATH."
            )

        try:
            with tempfile.TemporaryDirectory(
                prefix="assayflux_javascript_"
            ) as directory:
                workdir = Path(directory)
                source_path = workdir / "main.js"

                source_path.write_text(
                    source,
                    encoding="utf-8",
                )

                try:
                    execution = subprocess.run(
                        [node, str(source_path)],
                        cwd=workdir,
                        capture_output=True,
                        text=True,
                        timeout=timeout,
                        check=False,
                    )

                except subprocess.TimeoutExpired as exc:
                    stdout = exc.stdout or ""
                    stderr = exc.stderr or ""

                    if isinstance(stdout, bytes):
                        stdout = stdout.decode(
                            "utf-8",
                            errors="replace",
                        )

                    if isinstance(stderr, bytes):
                        stderr = stderr.decode(
                            "utf-8",
                            errors="replace",
                        )

                    message = (
                        "JavaScript execution exceeded the "
                        f"{timeout}-second timeout."
                    )

                    stderr = f"{stderr.rstrip()}\n{message}\n"

                    return ExecutionResult(
                        language=self.language,
                        stdout=stdout,
                        stderr=stderr,
                        returncode=124,
                    )

                return ExecutionResult(
                    language=self.language,
                    stdout=execution.stdout,
                    stderr=execution.stderr,
                    returncode=execution.returncode,
                )

        except OSError as exc:
            raise RuntimeError(
                f"Could not execute the JavaScript program: {exc}"
            ) from exc