"""
Fortran language adapter for AssayFlux.

Executes Fortran source code by compiling it with a Fortran
compiler and running the resulting executable.

Supported compiler commands:
- gfortran
- flang
- ifx

Warning:
Executed programs are not sandboxed. Only run trusted code.
"""

import math
import shutil
import subprocess
import tempfile
from pathlib import Path

from assayflux.interop.base import ExecutionResult, LanguageAdapter


class FortranAdapter(LanguageAdapter):
    """Compile and execute Fortran source code."""

    @property
    def language(self) -> str:
        return "fortran"

    def _find_compiler(self) -> str | None:
        """Find an available Fortran compiler."""
        for command in ("gfortran", "flang", "ifx"):
            compiler = shutil.which(command)
            if compiler is not None:
                return compiler
        return None

    def is_available(self) -> bool:
        """Check whether a supported compiler is available."""
        return self._find_compiler() is not None

    def execute(
        self,
        source: str,
        *,
        timeout: float = 10.0,
    ) -> ExecutionResult:
        """Compile and execute trusted Fortran source code."""
        if not isinstance(source, str):
            raise ValueError("Fortran source must be a string.")

        if not source.strip():
            raise ValueError("Fortran source must not be empty.")

        if (
            isinstance(timeout, bool)
            or not isinstance(timeout, (int, float))
            or not math.isfinite(timeout)
            or timeout <= 0
        ):
            raise ValueError(
                "Timeout must be a finite positive number."
            )

        compiler = self._find_compiler()

        if compiler is None:
            raise RuntimeError(
                "Fortran is unavailable. Install gfortran, "
                "flang, or ifx and ensure it is on PATH."
            )

        try:
            with tempfile.TemporaryDirectory(
                prefix="assayflux_fortran_"
            ) as directory:
                workdir = Path(directory)
                source_path = workdir / "program.f90"
                executable = workdir / "program"

                source_path.write_text(
                    source,
                    encoding="utf-8",
                )

                try:
                    compilation = subprocess.run(
                        [
                            compiler,
                            str(source_path),
                            "-o",
                            str(executable),
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
                        "Fortran compilation exceeded the "
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
                        "Fortran execution exceeded the "
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
                f"Could not compile or execute the Fortran "
                f"program: {exc}"
            ) from exc