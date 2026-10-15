"""Command-line launcher for AssayFlux."""

import argparse
import sys
from pathlib import Path

from assayflux.interpreter import Interpreter


def main():
    parser = argparse.ArgumentParser(
        prog="assayflux",
        description="Run an AssayFlux Scientific Systems program.",
    )

    parser.add_argument(
        "file",
        help="Path to the AssayFlux source file.",
    )

    args = parser.parse_args()
    source_path = Path(args.file)

    if not source_path.is_file():
        print(
            f"Error: file not found: {source_path}",
            file=sys.stderr,
        )
        return 1

    try:
        source = source_path.read_text(encoding="utf-8")
        interpreter = Interpreter()
        interpreter.run(source)
        return 0
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())