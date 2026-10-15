# AssayFlux Scientific Systems

**AssayFlux** is an experimental, Python-implemented programming language for scientific computing and multi-runtime orchestration. Source files use `.af`. Current release: `0.2.0`.

> Status: early-stage developer release, not a security sandbox and not yet a production-ready 30-language platform. The core interpreter and a subset of integrations are implemented; other adapters require runtime-specific verification.

## Install from GitHub

Requires Python 3.10 or newer and Git.

```bash
git clone https://github.com/OWNER/AssayFlux.git
cd AssayFlux
python -m pip install .
assayflux examples/hello.af
```

Replace `OWNER/AssayFlux` with the actual GitHub owner/repository after publishing the repository. For development and tests:

```bash
python -m pip install -e ".[dev]"
python -m pytest
```

If the repository does not define the optional `dev` extra, use `python -m pip install pytest` before running tests.

## First program

```af
app "Hello AssayFlux"
constant GREETING = "Hello, AssayFlux!"
show GREETING
```

Save as `hello.af`, then run `assayflux hello.af` or `python -m assayflux hello.af`.

## Language examples

### Variables and arithmetic

```af
amount = 10
price = 2.5
show amount * price
```

### Constants

```af
constant PI = 3.14159
show PI
# PI = 3.14  # Runtime error: constants cannot be reassigned
```

### Conditions

```af
temperature = 25
if temperature > 30
    show "Hot"
otherwise temperature > 20
    show "Warm"
else
    show "Cold"
end
```

### Condition-controlled loop

```af
count = 0
repeat count < 5
    show count
    count = count + 1
end
```

### Functions

```af
f.add(a, b)
    return a + b
end
show add(10, 20)
```

### Python libraries

```af
import math
show math.sqrt(25)
```

Python imports execute with the permissions of the AssayFlux process. Only run trusted code.

## Your keywords

| AssayFlux syntax | Meaning |
|---|---|
| `show` | Display a value |
| `otherwise` | Additional conditional branch, like `elif` |
| `repeat` | Condition-controlled loop, like `while` |
| `stop` | Exit the nearest loop |
| `skip` | Continue with the next loop iteration |
| `constant` | Declare a non-reassignable name |
| `end` | Explicitly close a block |
| `f.name(args)` | Declare a function; calls use `name(args)` |
| `true`, `false` | Boolean literals |
| `app "Name"` | Set application metadata |

Blocks use four spaces per indentation level and require an explicit `end`. Strings use single or double quotes; comments begin with `#`.

## Architecture

- `assayflux/lexer.py` — source tokenization
- `assayflux/parser.py` — syntax parser
- `assayflux/ast_nodes.py` — abstract syntax tree nodes
- `assayflux/interpreter.py` — execution and scope
- `assayflux/interop/` — adapter registry and external runtime execution
- `examples/` — runnable `.af` examples
- `tests/` — automated regression tests
- `docs/` — language specification, grammar, status, and interoperability design

## Multi-language goal

AssayFlux is designed to orchestrate other runtimes through a common adapter interface. Python is the core implementation language. External runtimes must be installed separately. HTML and CSS are web assets rendered by a browser/WebView, not general-purpose languages executed by the AssayFlux interpreter. JavaScript is executable only when an appropriate runtime is installed and its adapter is verified.

The repository contains adapter implementations for multiple languages, but **an adapter file does not guarantee a working runtime or supported integration**. Check `docs/SPECIFICATION_STATUS.md` and `docs/INTEROPERABILITY_AND_WEB.md`. Never run untrusted code: subprocess timeouts are not a sandbox.

## Contributing and releases

1. Update the language specification before changing semantics.
2. Add regression tests for new syntax and runtime behavior.
3. Run `python -m pytest`.
4. Update the implementation status table honestly.
5. Use tagged versions and release notes for public releases.

See `docs/ROADMAP.md` for the phased plan.
