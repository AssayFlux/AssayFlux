"""Minimal command-line entry point for the AssayFlux language core."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from assayflux.api import (
    Interpreter,
    SecurityPolicy,
    check,
    parse,
    read_source,
    validate_source,
)
from assayflux.diagnostics.model import AssayFluxError


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="assayflux", description="Run or check .af language files.")
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("run", "check"):
        command = commands.add_parser(name, help=f"{name} an AssayFlux source file")
        command.add_argument("file", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    policy = SecurityPolicy()
    try:
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
