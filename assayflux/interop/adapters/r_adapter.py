"""
R language adapter for AssayFlux.

Executes R source code through the Rscript command.

Requirement:
- R installed and available through 'Rscript'.

Warning:
Executed programs are not sandboxed. Only run trusted code.
"""

import math
import shutil
import subprocess
import tempfile
from pathlib import Path

from assayflux.interop.base import ExecutionResult, LanguageAdapter


class RAdapter(LanguageAdapter):
    """Execute R source code."""

    @property
    def language(self) -> str:
        return "r"

    def is_available(self) -> bool:
        """Check whether Rscript is available."""
        return shutil.which("Rscript") is not None

    def execute(
        self,
        source: str,
        *,
        timeout: float = 10.0,
    ) -> ExecutionResult:
        """Execute trusted R source code."""
        if not isinstance(source, str):
            raise ValueError("R source must be a string.")

        if not source.strip():
            raise ValueError("R source must not be empty.")

        if (
            isinstance(timeout, bool)
            or not isinstance(timeout, (int, float))
            or not math.isfinite(timeout)
            or timeout <= 0
        ):
            raise ValueError(
                "Timeout must be a finite positive number."
            )

        rscript = shutil.which("Rscript")

        if rscript is None:
            raise RuntimeError(
                "R is unavailable. Install R and ensure "
                "'Rscript' is on PATH."
            )

        try:
            with tempfile.TemporaryDirectory(
                prefix="assayflux_r_"
            ) as directory:
                workdir = Path(directory)
                source_path = workdir / "program.R"

                source_path.write_text(
                    source,
                    encoding="utf-8",
                )

                try:
                    execution = subprocess.run(
                        [
                            rscript,
                            "--vanilla",
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
                        "R execution exceeded the "
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
                f"Could not execute the R program: {exc}"
            ) from exc