"""
D language adapter for AssayFlux.

Compiles and executes D source code using a D compiler.

Supported compilers:
- DMD (dmd)
- LDC (ldc2)
- GDC (gdc)

Warning:
Executed programs are not sandboxed. Only run trusted code.
"""

import math
import shutil
import subprocess
import tempfile
from pathlib import Path

from assayflux.interop.base import ExecutionResult, LanguageAdapter


class DAdapter(LanguageAdapter):
    """Compile and execute D source code."""

    @property
    def language(self) -> str:
        return "d"

    def _find_compiler(self):
        """Find an available D compiler."""
        for compiler_name in ("dmd", "ldc2", "gdc"):
            compiler_path = shutil.which(compiler_name)

            if compiler_path is not None:
                return compiler_name, compiler_path

        return None, None

    def is_available(self) -> bool:
        """Check whether a supported D compiler is available."""
        _, compiler_path = self._find_compiler()
        return compiler_path is not None

    def execute(
        self,
        source: str,
        *,
        timeout: float = 10.0,
    ) -> ExecutionResult:
        """Compile and execute trusted D source code."""
        if not isinstance(source, str):
            raise ValueError("D source must be a string.")

        if not source.strip():
            raise ValueError("D source must not be empty.")

        if (
            isinstance(timeout, bool)
            or not isinstance(timeout, (int, float))
            or not math.isfinite(timeout)
            or timeout <= 0
        ):
            raise ValueError(
                "Timeout must be a finite positive number."
            )

        compiler_name, compiler_path = self._find_compiler()

        if compiler_path is None:
            raise RuntimeError(
                "D is unavailable. Install DMD, LDC, or GDC "
                "and ensure its compiler command is on PATH."
            )

        try:
            with tempfile.TemporaryDirectory(
                prefix="assayflux_d_"
            ) as directory:
                workdir = Path(directory)
                source_path = workdir / "main.d"
                executable = workdir / "assayflux_program"

                source_path.write_text(
                    source,
                    encoding="utf-8",
                )

                if compiler_name == "dmd":
                    compile_command = [
                        compiler_path,
                        "-of=" + str(executable),
                        str(source_path),
                    ]
                elif compiler_name == "ldc2":
                    compile_command = [
                        compiler_path,
                        "-of=" + str(executable),
                        str(source_path),
                    ]
                else:
                    compile_command = [
                        compiler_path,
                        "-o",
                        str(executable),
                        str(source_path),
                    ]

                try:
                    compilation = subprocess.run(
                        compile_command,
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
                        "D compilation exceeded the "
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
                        "D execution exceeded the "
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
                f"Could not compile or execute the D "
                f"program: {exc}"
            ) from exc