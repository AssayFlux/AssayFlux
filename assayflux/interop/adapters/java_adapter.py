"""
Java language adapter for AssayFlux.

Compiles and executes Java source code using the Java Development Kit.

The source must define a public class named Main with a main method.

Warning:
Java programs are not sandboxed. Only execute trusted source code.
"""

import math
import shutil
import subprocess
import tempfile
from pathlib import Path

from assayflux.interop.base import ExecutionResult, LanguageAdapter


class JavaAdapter(LanguageAdapter):
    """Compile and execute Java source code."""

    @property
    def language(self) -> str:
        return "java"

    def is_available(self) -> bool:
        """Check whether the Java compiler and runtime are available."""
        return shutil.which("javac") is not None and shutil.which("java") is not None

    def execute(
        self,
        source: str,
        *,
        timeout: float = 10.0,
    ) -> ExecutionResult:
        """Compile and execute trusted Java source code."""
        if not isinstance(source, str):
            raise ValueError("Java source must be a string.")

        if not source.strip():
            raise ValueError("Java source must not be empty.")

        if (
            isinstance(timeout, bool)
            or not isinstance(timeout, (int, float))
            or not math.isfinite(timeout)
            or timeout <= 0
        ):
            raise ValueError("Timeout must be a finite positive number.")

        if not self.is_available():
            raise RuntimeError(
                "Java is unavailable. Install a Java Development Kit "
                "and ensure 'javac' and 'java' are on PATH."
            )

        try:
            with tempfile.TemporaryDirectory(
                prefix="assayflux_java_"
            ) as directory:
                workdir = Path(directory)
                source_path = workdir / "Main.java"

                source_path.write_text(source, encoding="utf-8")

                try:
                    compilation = subprocess.run(
                        ["javac", str(source_path)],
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
                            "Java compilation exceeded the "
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
                        ["java", "-cp", str(workdir), "Main"],
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
                        stdout = stdout.decode("utf-8", errors="replace")
                    if isinstance(stderr, bytes):
                        stderr = stderr.decode("utf-8", errors="replace")

                    message = (
                        "Java execution exceeded the "
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
                f"Could not compile or execute the Java program: {exc}"
            ) from exc