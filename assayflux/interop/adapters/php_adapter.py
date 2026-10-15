"""
PHP language adapter for AssayFlux.

Executes PHP source code using the PHP CLI interpreter.

Requirement:
- PHP CLI installed and available through the 'php' command.

Warning:
Executed programs are not sandboxed. Only run trusted code.
"""

import math
import shutil
import subprocess
import tempfile
from pathlib import Path

from assayflux.interop.base import ExecutionResult, LanguageAdapter


class PHPAdapter(LanguageAdapter):
    """Execute PHP source code."""

    @property
    def language(self) -> str:
        return "php"

    def is_available(self) -> bool:
        """Check whether the PHP CLI is available."""
        return shutil.which("php") is not None

    def execute(
        self,
        source: str,
        *,
        timeout: float = 10.0,
    ) -> ExecutionResult:
        """Execute trusted PHP source code."""
        if not isinstance(source, str):
            raise ValueError("PHP source must be a string.")

        if not source.strip():
            raise ValueError("PHP source must not be empty.")

        if (
            isinstance(timeout, bool)
            or not isinstance(timeout, (int, float))
            or not math.isfinite(timeout)
            or timeout <= 0
        ):
            raise ValueError(
                "Timeout must be a finite positive number."
            )

        php = shutil.which("php")

        if php is None:
            raise RuntimeError(
                "PHP is unavailable. Install PHP CLI and ensure "
                "the 'php' command is on PATH."
            )

        try:
            with tempfile.TemporaryDirectory(
                prefix="assayflux_php_"
            ) as directory:
                workdir = Path(directory)
                source_path = workdir / "program.php"

                source_path.write_text(
                    source,
                    encoding="utf-8",
                )

                try:
                    execution = subprocess.run(
                        [
                            php,
                            "-f",
                            str(source_path),
                        ],
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
                        "PHP execution exceeded the "
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
                f"Could not execute the PHP program: {exc}"
            ) from exc