"""
C language adapter for AssayFlux.

Compiles and executes C source code using GCC or Clang.
The selected compiler must be installed and available on PATH.

Warning:
Compiled programs are not sandboxed. Only execute trusted source code.
"""

import math
import shutil
import subprocess
import tempfile
from pathlib import Path

from assayflux.interop.base import ExecutionResult, LanguageAdapter


class CAdapter(LanguageAdapter):
    """Compile and execute C source code."""

    @property
    def language(self) -> str:
        return "c"

    def _find_compiler(self) -> str | None:
        """Find an available C compiler."""
        return shutil.which("cc") or shutil.which("gcc") or shutil.which("clang")

    def is_available(self) -> bool:
        """Return whether a C compiler is available."""
        return self._find_compiler() is not None

    def execute(
        self,
        source: str,
        *,
        timeout: float = 10.0,
    ) -> ExecutionResult:
        """Compile and execute trusted C source code."""
        if not isinstance(source, str):
            raise ValueError("C source must be a string.")

        if not source.strip():
            raise ValueError("C source must not be empty.")

        if (
            isinstance(timeout, bool)
            or not isinstance(timeout, (int, float))
            or not math.isfinite(timeout)
            or timeout <= 0
        ):
            raise ValueError("Timeout must be a finite positive number.")

        compiler = self._find_compiler()
        if compiler is None:
            raise RuntimeError(
                "No C compiler found. Install GCC or Clang and ensure "
                "the compiler is on PATH."
            )

        try:
            with tempfile.TemporaryDirectory(prefix="assayflux_c_") as directory:
                workdir = Path(directory)
                source_path = workdir / "program.c"
                executable_path = workdir / "program"

                source_path.write_text(source, encoding="utf-8")

                try:
                    compilation = subprocess.run(
                        [
                            compiler,
                            str(source_path),
                            "-o",
                            str(executable_path),
                        ],
                        capture_output=True,
                        text=True,
                        timeout=timeout,
                        check=False,
                    )
                except subprocess.TimeoutExpired as exc:
                    return ExecutionResult(
                        language=self.language,
                        stdout="",
                        stderr=f"C compilation exceeded the {timeout}-second timeout.\n",
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
                        [str(executable_path)],
                        capture_output=True,
                        text=True,
                        timeout=timeout,
                        check=False,
                    )
                except subprocess.TimeoutExpired as exc:
                    stdout = exc.stdout or ""
                    stderr = exc.stderr or ""

                    if isinstance(stdout, bytes):
                        stdout = stdout.decode("utf-8", errors="replace")
                    if isinstance(stderr, bytes):
                        stderr = stderr.decode("utf-8", errors="replace")

                    message = (
                        f"C execution exceeded the {timeout}-second timeout."
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
                f"Could not compile or execute the C program: {exc}"
            ) from exc