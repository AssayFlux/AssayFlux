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
from assayflux.diagnostics.model import AssayFluxError, SourceError, SourceLocation
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
        print(result.stdout, end="" if result.stdout.endswith("\n") else "\n")
    if result.stderr:
        print(result.stderr, file=sys.stderr, end="" if result.stderr.endswith("\n") else "\n")
    return result.returncode


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
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
