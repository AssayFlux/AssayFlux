"""
Perl language adapter for AssayFlux.

Executes Perl source code through the Perl interpreter.

Requirement:
- Perl installed and available through the 'perl' command.

Warning:
Executed programs are not sandboxed. Only run trusted code.
"""

import math
import shutil
import subprocess
import tempfile
from pathlib import Path

from assayflux.interop.base import ExecutionResult, LanguageAdapter


class PerlAdapter(LanguageAdapter):
    """Execute Perl source code."""

    @property
    def language(self) -> str:
        return "perl"

    def is_available(self) -> bool:
        """Check whether the Perl interpreter is available."""
        return shutil.which("perl") is not None

    def execute(
        self,
        source: str,
        *,
        timeout: float = 10.0,
    ) -> ExecutionResult:
        """Execute trusted Perl source code."""
        if not isinstance(source, str):
            raise ValueError("Perl source must be a string.")

        if not source.strip():
            raise ValueError("Perl source must not be empty.")

        if (
            isinstance(timeout, bool)
            or not isinstance(timeout, (int, float))
            or not math.isfinite(timeout)
            or timeout <= 0
        ):
            raise ValueError(
                "Timeout must be a finite positive number."
            )

        perl = shutil.which("perl")

        if perl is None:
            raise RuntimeError(
                "Perl is unavailable. Install Perl and ensure "
                "the 'perl' command is on PATH."
            )

        try:
            with tempfile.TemporaryDirectory(
                prefix="assayflux_perl_"
            ) as directory:
                workdir = Path(directory)
                source_path = workdir / "program.pl"

                source_path.write_text(
                    source,
                    encoding="utf-8",
                )

                try:
                    execution = subprocess.run(
                        [perl, str(source_path)],
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
                        "Perl execution exceeded the "
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
                f"Could not execute the Perl program: {exc}"
            ) from exc 