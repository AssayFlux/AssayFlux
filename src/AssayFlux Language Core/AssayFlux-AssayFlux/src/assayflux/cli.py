"""Command-line entry point for the AssayFlux language and integrations."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from assayflux.api import (
    Interpreter,
    check,
    parse,
    read_source,
    validate_source,
)
from assayflux.diagnostics.model import (
    AssayFluxError,
    SecurityError,
    SourceError,
    SourceLocation,
)
from assayflux.execution import ExecutionRequest, get_provider
from assayflux.integrations.cli_anything import discover_harnesses, run_harness
from assayflux.security.project_config import load_security_policy


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="assayflux",
        description="Check and run .af source files, and manage installed integrations.",
    )
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("run", "check"):
        command = commands.add_parser(name, help=f"{name} an AssayFlux source file")
        command.add_argument("file", type=Path)

    runtimes = commands.add_parser("runtimes", help="list runtimes installed in a Piston service")
    runtimes.add_argument("--provider", choices=("piston",), default="piston")
    runtimes.add_argument("--json", action="store_true", dest="json_output")

    execute = commands.add_parser("execute", aliases=["exec"], help="execute code through an explicitly configured external provider")
    execute.add_argument("--provider", choices=("piston", "code-interpreter"), required=True)
    source = execute.add_mutually_exclusive_group(required=True)
    source.add_argument("--code", help="source code supplied directly on the command line")
    source.add_argument("--file", type=Path, help="read source code from a file")
    execute.add_argument("--filename", help="filename presented to the external runtime (important for compiled languages)")
    execute.add_argument("--language", help="runtime language; required for Piston, optional for Code Interpreter")
    execute.add_argument("--version", help="runtime version selector required by Piston")
    execute.add_argument("--stdin", default="", help="text supplied to the program's standard input (Piston only)")
    execute.add_argument("--arg", action="append", default=[], dest="program_args", help="program argument; may be repeated (Piston only)")
    execute.add_argument("--context-id", help="reuse an existing Code Interpreter context")
    execute.add_argument("--timeout", type=int, default=10, help="execution timeout in seconds (1-120)")
    execute.add_argument("--json", action="store_true", dest="json_output", help="print the structured execution result as JSON")
    execute.add_argument("--allow-external-execution", action="store_true", help="required acknowledgement: code will run outside the local .af interpreter")

    tools = commands.add_parser("tools", help="discover and invoke installed CLI-Anything harnesses")
    tool_commands = tools.add_subparsers(dest="tools_command", required=True)
    list_command = tool_commands.add_parser("list", help="list installed CLI-Anything harnesses")
    list_command.add_argument("--json", action="store_true", dest="json_output")

    run_command = tool_commands.add_parser("run", help="invoke a harness (requires explicit side-effect opt-in)")
    run_command.add_argument("name", help="installed executable, e.g. cli-anything-blender")
    run_command.add_argument(
        "--allow-external-tools",
        action="store_true",
        help="confirm that the external harness may edit files or launch applications",
    )
    run_command.add_argument("--timeout", type=int, default=60, help="timeout in seconds (1-300)")
    run_command.add_argument("--cwd", type=Path, help="existing working directory for the harness")
    run_command.add_argument(
        "harness_args",
        nargs=argparse.REMAINDER,
        help="arguments passed to the harness; use -- before harness arguments",
    )
    return parser


def _run_tools(args: argparse.Namespace) -> int:
    if args.tools_command == "list":
        harnesses = discover_harnesses()
        if args.json_output:
            print(json.dumps([{"name": item.name, "executable": item.executable} for item in harnesses], indent=2))
        elif not harnesses:
            print("No CLI-Anything harnesses found on PATH.")
        else:
            for item in harnesses:
                print(f"{item.name}\t{item.executable}")
        return 0

    harness_args = list(args.harness_args)
    if harness_args and harness_args[0] == "--":
        harness_args = harness_args[1:]
    result = run_harness(
        args.name,
        harness_args,
        allow_external_tools=args.allow_external_tools,
        timeout=args.timeout,
        cwd=args.cwd,
    )
    if result.stdout:
        print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, file=sys.stderr, end="")
    return result.returncode


def _run_external_execution(args: argparse.Namespace) -> int:
    if not args.allow_external_execution:
        raise SecurityError(
            "External execution requires --allow-external-execution",
            suggestion="Review the configured provider and its isolation model before opting in.",
        )
    if not 1 <= args.timeout <= 120:
        raise SecurityError("Execution timeout must be between 1 and 120 seconds")
    if args.file is not None:
        try:
            if args.file.stat().st_size > 1_000_000:
                raise SecurityError("Execution source exceeds the 1 MB request limit")
            code = args.file.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            raise SourceError("Unable to read external execution source", location=SourceLocation(str(args.file)), details=type(exc).__name__) from exc
        filename = args.filename or args.file.name
    else:
        code = args.code
        filename = args.filename or "main.py"

    request = ExecutionRequest(
        code=code,
        language=args.language,
        version=args.version,
        filename=filename,
        stdin=args.stdin,
        args=tuple(args.program_args),
        timeout_seconds=args.timeout,
        context_id=args.context_id,
    )
    provider = get_provider(args.provider)
    result = provider.execute(request)
    if args.json_output:
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    else:
        if result.stdout:
            print(result.stdout, end="")
        if result.provider == "code-interpreter":
            for event in result.outputs:
                if event.get("type") == "result" and event.get("text"):
                    print(event["text"])
        if result.stderr:
            print(result.stderr, file=sys.stderr, end="")
        if result.signal:
            print(f"Execution terminated by signal: {result.signal}", file=sys.stderr)
    return result.exit_code if result.exit_code is not None else 1


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.command == "runtimes":
        try:
            runtimes = get_provider(args.provider).list_runtimes()
            if args.json_output:
                print(json.dumps(runtimes, ensure_ascii=False, indent=2))
            else:
                for runtime in runtimes:
                    aliases = ", ".join(runtime.get("aliases", []))
                    suffix = f" (aliases: {aliases})" if aliases else ""
                    print(f"{runtime.get('language', '?')}\\t{runtime.get('version', '?')}{suffix}")
            return 0
        except AssayFluxError as exc:
            print(f"AssayFlux: {exc}", file=sys.stderr)
            return 1
    if args.command in {"execute", "exec"}:
        try:
            return _run_external_execution(args)
        except AssayFluxError as exc:
            print(f"AssayFlux: {exc}", file=sys.stderr)
            return 1
    if args.command == "tools":
        try:
            return _run_tools(args)
        except AssayFluxError as exc:
            print(f"AssayFlux: {exc}", file=sys.stderr)
            return 1

    try:
        if args.file.suffix != ".af":
            raise SourceError(
                "AssayFlux source files must use the .af extension",
                location=SourceLocation(str(args.file)),
                suggestion="Rename the source file with a .af extension.",
            )
        policy = load_security_policy(args.file.resolve().parent)
        source = read_source(args.file, policy)
        validate_source(source, str(args.file), policy)
        tree = parse(source, filename=str(args.file))
        check(tree)
        if args.command == "check":
            print(f"OK: {args.file}")
            return 0
        output: list[str] = []
        interpreter = Interpreter(policy, output_fn=output.append, workspace=args.file.resolve().parent)
        interpreter.run(tree)
        for line in output:
            print(line)
        return 0
    except AssayFluxError as exc:
        print(f"AssayFlux: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
