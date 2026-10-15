"""
Crystal language adapter for AssayFlux.

Compiles and executes Crystal source code.

Requirement:
- Crystal installed and available through the 'crystal' command.

Warning:
Executed programs are not sandboxed. Only run trusted code.
"""

import math
import shutil
import subprocess
import tempfile
from pathlib import Path

from assayflux.interop.base import ExecutionResult, LanguageAdapter


class CrystalAdapter(LanguageAdapter):
    """Compile and execute Crystal source code."""

    @property
    def language(self) -> str:
        return "crystal"

    def is_available(self) -> bool:
        """Check whether the Crystal compiler is available."""
        return shutil.which("crystal") is not None

    def execute(
        self,
        source: str,
        *,
        timeout: float = 10.0,
    ) -> ExecutionResult:
        """Compile and execute trusted Crystal source code."""
        if not isinstance(source, str):
            raise ValueError("Crystal source must be a string.")

        if not source.strip():
            raise ValueError("Crystal source must not be empty.")

        if (
            isinstance(timeout, bool)
            or not isinstance(timeout, (int, float))
            or not math.isfinite(timeout)
            or timeout <= 0
        ):
            raise ValueError(
                "Timeout must be a finite positive number."
            )

        crystal = shutil.which("crystal")

        if crystal is None:
            raise RuntimeError(
                "Crystal is unavailable. Install Crystal and "
                "ensure the 'crystal' command is on PATH."
            )

        try:
            with tempfile.TemporaryDirectory(
                prefix="assayflux_crystal_"
            ) as directory:
                workdir = Path(directory)
                source_path = workdir / "program.cr"

                source_path.write_text(
                    source,
                    encoding="utf-8",
                )

                try:
                    execution = subprocess.run(
                        [
                            crystal,
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
                        "Crystal execution or compilation "
                        "exceeded the "
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
                f"Could not compile or execute the Crystal "
                f"program: {exc}"
            ) from exc