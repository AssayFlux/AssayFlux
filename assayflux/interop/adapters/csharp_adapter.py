"""
C# language adapter for AssayFlux.

Compiles and executes C# source code using the .NET SDK.

Requirements:
- .NET SDK available through the 'dotnet' command.

Expected source format:
- A C# program with top-level statements or a suitable entry point.

Warning:
Executed programs are not sandboxed. Only run trusted code.
"""

import math
import shutil
import subprocess
import tempfile
from pathlib import Path

from assayflux.interop.base import ExecutionResult, LanguageAdapter


class CSharpAdapter(LanguageAdapter):
    """Compile and execute C# source code using .NET."""

    @property
    def language(self) -> str:
        return "csharp"

    def is_available(self) -> bool:
        """Check whether the .NET SDK is available."""
        return shutil.which("dotnet") is not None

    def execute(
        self,
        source: str,
        *,
        timeout: float = 10.0,
    ) -> ExecutionResult:
        """Build and execute trusted C# source code."""
        if not isinstance(source, str):
            raise ValueError("C# source must be a string.")

        if not source.strip():
            raise ValueError("C# source must not be empty.")

        if (
            isinstance(timeout, bool)
            or not isinstance(timeout, (int, float))
            or not math.isfinite(timeout)
            or timeout <= 0
        ):
            raise ValueError(
                "Timeout must be a finite positive number."
            )

        dotnet = shutil.which("dotnet")

        if dotnet is None:
            raise RuntimeError(
                ".NET is unavailable. Install the .NET SDK and "
                "ensure the 'dotnet' command is on PATH."
            )

        try:
            with tempfile.TemporaryDirectory(
                prefix="assayflux_csharp_"
            ) as directory:
                workdir = Path(directory)

                project_file = workdir / "AssayFluxProgram.csproj"
                source_file = workdir / "Program.cs"

                project_file.write_text(
                    "<Project Sdk=\"Microsoft.NET.Sdk\">\n"
                    "  <PropertyGroup>\n"
                    "    <OutputType>Exe</OutputType>\n"
                    "    <TargetFramework>net8.0</TargetFramework>\n"
                    "    <ImplicitUsings>enable</ImplicitUsings>\n"
                    "    <Nullable>enable</Nullable>\n"
                    "  </PropertyGroup>\n"
                    "</Project>\n",
                    encoding="utf-8",
                )

                source_file.write_text(source, encoding="utf-8")

                try:
                    compilation = subprocess.run(
                        [
                            dotnet,
                            "build",
                            str(project_file),
                            "--nologo",
                            "--verbosity",
                            "quiet",
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
                            "C# compilation exceeded the "
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

                program_dll = (
                    workdir
                    / "bin"
                    / "Debug"
                    / "net8.0"
                    / "AssayFluxProgram.dll"
                )

                try:
                    execution = subprocess.run(
                        [dotnet, str(program_dll)],
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
                        "C# execution exceeded the "
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
                "Could not compile or execute the C# program: "
                f"{exc}"
            ) from exc