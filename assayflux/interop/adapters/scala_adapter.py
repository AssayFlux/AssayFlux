"""
Scala language adapter for AssayFlux.

Compiles and executes Scala source code using Scala CLI.

Requirement:
- Scala CLI installed and available through the 'scala' command.

Warning:
Executed programs are not sandboxed. Only run trusted code.
"""

import math
import shutil
import subprocess
import tempfile
from pathlib import Path

from assayflux.interop.base import ExecutionResult, LanguageAdapter


class ScalaAdapter(LanguageAdapter):
    """Compile and execute Scala source code."""

    @property
    def language(self) -> str:
        return "scala"

    def is_available(self) -> bool:
        """Check whether Scala CLI is available."""
        return shutil.which("scala") is not None

    def execute(
        self,
        source: str,
        *,
        timeout: float = 10.0,
    ) -> ExecutionResult:
        """Compile and execute trusted Scala source code."""
        if not isinstance(source, str):
            raise ValueError("Scala source must be a string.")

        if not source.strip():
            raise ValueError("Scala source must not be empty.")

        if (
            isinstance(timeout, bool)
            or not isinstance(timeout, (int, float))
            or not math.isfinite(timeout)
            or timeout <= 0
        ):
            raise ValueError(
                "Timeout must be a finite positive number."
            )

        scala = shutil.which("scala")

        if scala is None:
            raise RuntimeError(
                "Scala is unavailable. Install Scala CLI and "
                "ensure the 'scala' command is on PATH."
            )

        try:
            with tempfile.TemporaryDirectory(
                prefix="assayflux_scala_"
            ) as directory:
                workdir = Path(directory)
                source_path = workdir / "Main.scala"

                source_path.write_text(
                    source,
                    encoding="utf-8",
                )

                try:
                    execution = subprocess.run(
                        [
                            scala,
                            "run",
                            str(source_path),
                            "--server=false",
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
                        "Scala compilation or execution exceeded "
                        f"the {timeout}-second timeout."
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
                f"Could not compile or execute the Scala "
                f"program: {exc}"
            ) from exc