"""
Dart language adapter for AssayFlux.

Executes Dart source code through the Dart SDK.

Requirement:
- Dart SDK installed and available through the 'dart' command.

Warning:
Executed programs are not sandboxed. Only run trusted code.
"""

import math
import shutil
import subprocess
import tempfile
from pathlib import Path

from assayflux.interop.base import ExecutionResult, LanguageAdapter


class DartAdapter(LanguageAdapter):
    """Execute Dart source code."""

    @property
    def language(self) -> str:
        return "dart"

    def is_available(self) -> bool:
        """Check whether the Dart SDK is available."""
        return shutil.which("dart") is not None

    def execute(
        self,
        source: str,
        *,
        timeout: float = 10.0,
    ) -> ExecutionResult:
        """Execute trusted Dart source code."""
        if not isinstance(source, str):
            raise ValueError("Dart source must be a string.")

        if not source.strip():
            raise ValueError("Dart source must not be empty.")

        if (
            isinstance(timeout, bool)
            or not isinstance(timeout, (int, float))
            or not math.isfinite(timeout)
            or timeout <= 0
        ):
            raise ValueError(
                "Timeout must be a finite positive number."
            )

        dart = shutil.which("dart")

        if dart is None:
            raise RuntimeError(
                "Dart is unavailable. Install the Dart SDK "
                "and ensure 'dart' is on PATH."
            )

        try:
            with tempfile.TemporaryDirectory(
                prefix="assayflux_dart_"
            ) as directory:
                workdir = Path(directory)
                source_path = workdir / "program.dart"

                source_path.write_text(
                    source,
                    encoding="utf-8",
                )

                try:
                    execution = subprocess.run(
                        [
                            dart,
                            "run",
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
                        "Dart execution exceeded the "
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
                f"Could not execute the Dart program: {exc}"
            ) from exc