"""
COBOL language adapter for AssayFlux.

Compiles and executes COBOL source code using GnuCOBOL.

Requirement:
- GnuCOBOL installed and available through the 'cobc' command.

Warning:
Executed programs are not sandboxed. Only run trusted code.
"""

import math
import shutil
import subprocess
import tempfile
from pathlib import Path

from assayflux.interop.base import ExecutionResult, LanguageAdapter


class COBOLAdapter(LanguageAdapter):
    """Compile and execute COBOL source code."""

    @property
    def language(self) -> str:
        return "cobol"

    def is_available(self) -> bool:
        """Check whether the GnuCOBOL compiler is available."""
        return shutil.which("cobc") is not None

    def execute(
        self,
        source: str,
        *,
        timeout: float = 10.0,
    ) -> ExecutionResult:
        """Compile and execute trusted COBOL source code."""
        if not isinstance(source, str):
            raise ValueError("COBOL source must be a string.")

        if not source.strip():
            raise ValueError("COBOL source must not be empty.")

        if (
            isinstance(timeout, bool)
            or not isinstance(timeout, (int, float))
            or not math.isfinite(timeout)
            or timeout <= 0
        ):
            raise ValueError(
                "Timeout must be a finite positive number."
            )

        compiler = shutil.which("cobc")

        if compiler is None:
            raise RuntimeError(
                "COBOL is unavailable. Install GnuCOBOL "
                "and ensure the 'cobc' command is on PATH."
            )

        try:
            with tempfile.TemporaryDirectory(
                prefix="assayflux_cobol_"
            ) as directory:
                workdir = Path(directory)
                source_path = workdir / "main.cob"
                executable = workdir / "assayflux_program"

                source_path.write_text(
                    source,
                    encoding="utf-8",
                )

                try:
                    compilation = subprocess.run(
                        [
                            compiler,
                            "-x",
                            "-free",
                            "-o",
                            str(executable),
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
                        "COBOL compilation exceeded the "
                        f"{timeout}-second timeout."
                    )

                    stderr = f"{stderr.rstrip()}\n{message}\n"

                    return ExecutionResult(
                        language=self.language,
                        stdout=stdout,
                        stderr=stderr,
                        returncode=124,
                    )

                if compilation.returncode != 0:
                    return ExecutionResult(
                        language=self.language,
                        stdout=compilation.stdout,
                        stderr=compilation.stderr,
                        returncode=compilation.returncode,
                    )

                try:
                    execution = subprocess.run(
                        [str(executable)],
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
                        "COBOL execution exceeded the "
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
                f"Could not compile or execute the COBOL "
                f"program: {exc}"
            ) from exc