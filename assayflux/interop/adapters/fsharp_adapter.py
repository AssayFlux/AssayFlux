"""
F# language adapter for AssayFlux.

Compiles and executes F# source code using the .NET SDK.

Requirement:
- .NET SDK installed and available through the 'dotnet' command.

Warning:
Executed programs are not sandboxed. Only run trusted code.
"""

import math
import shutil
import subprocess
import tempfile
from pathlib import Path

from assayflux.interop.base import ExecutionResult, LanguageAdapter


class FSharpAdapter(LanguageAdapter):
    """Compile and execute F# source code."""

    @property
    def language(self) -> str:
        return "fsharp"

    def is_available(self) -> bool:
        """Check whether the .NET SDK is available."""
        return shutil.which("dotnet") is not None

    def execute(
        self,
        source: str,
        *,
        timeout: float = 10.0,
    ) -> ExecutionResult:
        """Compile and execute trusted F# source code."""
        if not isinstance(source, str):
            raise ValueError("F# source must be a string.")

        if not source.strip():
            raise ValueError("F# source must not be empty.")

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
                "F# is unavailable. Install the .NET SDK and "
                "ensure the 'dotnet' command is on PATH."
            )

        try:
            with tempfile.TemporaryDirectory(
                prefix="assayflux_fsharp_"
            ) as directory:
                workdir = Path(directory)
                source_path = workdir / "Program.fs"
                project_path = workdir / "AssayFluxFSharp.fsproj"

                source_path.write_text(
                    source,
                    encoding="utf-8",
                )

                project_path.write_text(
                    """<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>net8.0</TargetFramework>
    <GenerateAssemblyInfo>false</GenerateAssemblyInfo>
  </PropertyGroup>
  <ItemGroup>
    <Compile Include="Program.fs" />
  </ItemGroup>
</Project>
""",
                    encoding="utf-8",
                )

                try:
                    compilation = subprocess.run(
                        [
                            dotnet,
                            "build",
                            str(project_path),
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

                    stderr = (
                        f"{stderr.rstrip()}\n"
                        "F# compilation exceeded the "
                        f"{timeout}-second timeout.\n"
                    )

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

                executable = (
                    workdir
                    / "bin"
                    / "Debug"
                    / "net8.0"
                    / "AssayFluxFSharp.dll"
                )

                try:
                    execution = subprocess.run(
                        [dotnet, str(executable)],
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

                    stderr = (
                        f"{stderr.rstrip()}\n"
                        "F# execution exceeded the "
                        f"{timeout}-second timeout.\n"
                    )

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
                f"Could not compile or execute the F# "
                f"program: {exc}"
            ) from exc