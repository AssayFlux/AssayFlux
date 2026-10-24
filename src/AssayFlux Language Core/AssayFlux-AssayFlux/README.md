# AssayFlux

**One language. Clear rules. Controlled execution.**

AssayFlux is an experimental programming language with canonical `.af` source files, a grammar-driven lexer/parser, source-located AST, semantic checks, and a budgeted interpreter.

## Quick start

Requires Python 3.11 or newer.

```bash
python -m pip install -e ".[dev]"
assayflux check examples/hello.af
assayflux run examples/hello.af
```

## Language example

```af
project "Hello AssayFlux"

name = "AssayFlux"
answer = 6 * 7

f.greet(person):
    show "Hello, " + person
end

greet(name)
show answer

3 times:
    show "Build. Test. Improve."
end
```

## Canonical choices

- Files use `.af`.
- Project declaration: `project "Name"`.
- Assignment: `NAME = expression`.
- Functions: `f.name(parameters): ... end`.
- Null and booleans: `null`, `true`, `false`.
- Counted repetition: `N times:`.
- Compound statements use indentation and a matching `end`.

Read [GRAMMAR.md](GRAMMAR.md) for syntax and [SECURITY.md](SECURITY.md) for runtime boundaries.

## Core architecture

- `src/assayflux/language/grammar.lark` — canonical grammar and token rules.
- `src/assayflux/language/parser.py` — lexer/parser integration and AST construction.
- `src/assayflux/language/ast_nodes.py` — source-located AST.
- `src/assayflux/language/ast_validator.py` — structural AST validation.
- `src/assayflux/language/semantic.py` — name resolution and conservative type checks.
- `src/assayflux/runtime/interpreter.py` — budgeted interpreter.
- `src/assayflux/runtime/python_bridge.py` — constrained interop with approved Python callables.
- `src/assayflux/integrations/cli_anything.py` — host-side adapter for installed CLI-Anything harnesses.
- `src/assayflux/execution/` — provider-neutral request/result models and adapters for Piston and Code Interpreter services.
- `src/assayflux/diagnostics/` — structured compiler/runtime errors.
- `src/assayflux/security/` — source validation and runtime policy.
- `src/assayflux/cli.py` and `src/assayflux/api.py` — command-line and public APIs.

The lexer is provided by Lark's contextual lexer from the canonical grammar; token definitions should not be duplicated in a second, divergent lexer.

## CLI-Anything integration

CLI-Anything harnesses remain separately installed Python entry points; AssayFlux discovers them on `PATH` and invokes them through an adapter. This avoids copying application-specific logic into the language runtime.

```bash
# List discovered harnesses (human-readable or machine-readable)
assayflux tools list
assayflux tools list --json

# Invoke a harness. The opt-in is mandatory because tools can edit files
# or launch external applications. The -- separates AssayFlux flags from
# the arguments that should be passed to the harness.
assayflux tools run --allow-external-tools cli-anything-blender -- --json project list
```

The adapter uses argument arrays (never `shell=True`), validates executable names, and applies a configurable timeout capped at 300 seconds. It does not install harnesses automatically. Install the relevant harness in the active Python environment and review its license, dependencies, and side effects before use.

## Universal external execution interface

Use one `execute` command for external code, and `languages` to inspect what the configured providers report. `--provider auto` is the default: requests with an explicit runtime version, stdin, or program arguments route to Piston; simple requests without those features route to the Code Interpreter service. Piston requests still require both `--language` and `--version`. Specify `--provider` to force a backend. The native `.af` `run` and `check` commands remain separate and never fall back to an external runtime.

```bash
# Inspect the provider-backed runtime inventory
assayflux languages
assayflux languages --json

# One execution interface; explicit version selects Piston
assayflux execute --allow-external-execution --language python \\
  --version 3.12.0 --code 'print(6 * 7)'

# No version selects the Code Interpreter default
assayflux execute --allow-external-execution --code 'print(6 * 7)'
```

`languages` reports live Piston runtimes as `available`. It reports the Code Interpreter's default Python path only after its health endpoint responds successfully; the adapter does not expose a runtime-list endpoint, so additional kernels are not advertised without evidence. Inventory is provider/deployment-specific and is not a claim that every language in a proposed catalog works.

## External execution providers

The optional Piston and Code Interpreter adapters connect to separately deployed services. They are for explicitly requested Python or other supported-language execution, not for running `.af` programs. Native `assayflux run file.af` always uses the canonical AssayFlux parser, semantic checks, and interpreter; there is no automatic fallback.

See [EXECUTION_PROVIDERS.md](EXECUTION_PROVIDERS.md) for service setup, environment variables, examples, and security limitations.

```bash
# Discover languages and versions installed on your Piston service
assayflux runtimes --json

# Piston API v2; choose a language/version available on your own instance
assayflux execute --provider piston --allow-external-execution \
  --language python --version 3.12.0 --code 'print(6 * 7)'

# Imported Code Interpreter service; defaults to its Python context
assayflux execute --provider code-interpreter --allow-external-execution \
  --code 'import math; print(math.sqrt(81))'

# Structured machine-readable result
assayflux exec --provider code-interpreter --allow-external-execution \
  --json --code 'print("ready")'
```

External execution requires an explicit opt-in, a configured provider service, and server-side isolation appropriate for the workload. Client timeouts and response-size limits are not OS sandboxing.

## Python library interoperability

AssayFlux and its language core run on Python 3.11+. The host environment can install compatible Python packages with `pip`; the language's Python bridge is intentionally more restrictive than ordinary Python. Its default allowlist is small, and privileged Python-call capabilities remain disabled unless explicitly granted through trusted project configuration. The bridge validates values crossing the language boundary.

This supports packages such as NumPy, pandas, Pillow, and scientific or machine-learning libraries, but **an installed package is not automatically callable from an `.af` program**. Add explicit trusted grants to an `assayflux.toml` file beside the source file:

```toml
[python]
modules = ["numpy", "pandas"]
calls = ["numpy.mean", "numpy.std", "pandas.isna"]
```

Only list modules installed in the Python environment running AssayFlux, and grant only the public functions your project needs. Configured module and callable grants enable the Python bridge capabilities for that project. Calls still pass through the bridge's input/output value checks and hard-denied module/call rules. Review each package's side effects; broad unrestricted Python access would defeat the interpreter's security controls. AssayFlux is not an OS-enforced sandbox.

## Development

```bash
python -m pip install -e ".[dev]"
python -m pytest
python -m ruff check src tests
```

Separate services and application adapters should connect through explicit, tested APIs. No photo-editing functionality is part of the language core.

AssayFlux is experimental software, not an OS-enforced sandbox. Do not run untrusted programs with sensitive privileges.
