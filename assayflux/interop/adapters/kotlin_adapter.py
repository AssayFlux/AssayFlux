"""
Kotlin language adapter for AssayFlux.

Compiles and executes Kotlin source code using the Kotlin compiler
and Java runtime.

Requirements:
- Kotlin compiler (kotlinc)
- Java runtime (java)

Warning:
Executed programs are not sandboxed. Only run trusted code.
"""

import math
import shutil
import subprocess
import tempfile
from pathlib import Path

from assayflux.interop.base import ExecutionResult, LanguageAdapter


class KotlinAdapter(LanguageAdapter):
    """Compile and execute Kotlin source code."""

    @property
    def language(self) -> str:
        return "kotlin"

    def is_available(self) -> bool:
        """Check whether Kotlin and Java are available."""
        return (
            shutil.which("kotlinc") is not None
            and shutil.which("java") is not None
        )

    def execute(
        self,
        source: str,
        *,
        timeout: float = 10.0,
    ) -> ExecutionResult:
        """Compile and execute trusted Kotlin source code."""
        if not isinstance(source, str):
            raise ValueError("Kotlin source must be a string.")

        if not source.strip():
            raise ValueError("Kotlin source must not be empty.")

        if (
            isinstance(timeout, bool)
            or not isinstance(timeout, (int, float))
            or not math.isfinite(timeout)
            or timeout <= 0
        ):
            raise ValueError(
                "Timeout must be a finite positive number."
            )

        compiler = shutil.which("kotlinc")
        java = shutil.which("java")

        if compiler is None or java is None:
            raise RuntimeError(
                "Kotlin is unavailable. Install the Kotlin compiler "
                "and a Java runtime, and ensure 'kotlinc' and 'java' "
                "are on PATH."
            )

        try:
            with tempfile.TemporaryDirectory(
                prefix="assayflux_kotlin_"
            ) as directory:
                workdir = Path(directory)
                source_path = workdir / "Main.kt"
                jar_path = workdir / "program.jar"

                source_path.write_text(source, encoding="utf-8")

                try:
                    compilation = subprocess.run(
                        [
                            compiler,
                            str(source_path),
                            "-include-runtime",
                            "-d",
                            str(jar_path),
                        ],
                        cwd=workdir,
                        capture_output=True,
                        text=True,
                        timeout=timeout,
                        check=False,
                    )
                except subprocess.TimeoutExpired:
                    return ExecutionResult(
                        language=self.language,
                        stdout="",
                        stderr=(
                            "Kotlin compilation exceeded the "
                            f"{timeout}-second timeout.\n"
                        ),
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
                        [
                            java,
                            "-jar",
                            str(jar_path),
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
                        "Kotlin execution exceeded the "
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
                "Could not compile or execute the Kotlin program: "
                f"{exc}"
            ) from exc