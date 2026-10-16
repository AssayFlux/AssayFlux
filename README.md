# AssayFlux Scientific Systems

**AssayFlux** is an experimental programming language implemented in Python for scientific computing, automation, and multi-runtime orchestration.

- **Language:** AssayFlux
- **Source extension:** `.af`
- **Development version:** 0.3.0
- **Implementation:** Python
- **Repository:** https://github.com/AssayFlux/AssayFlux

> **Development status:** AssayFlux is experimental software. Features and integrations may change. An available language adapter does not guarantee that its external runtime is installed or fully supported.

---

## Contents

1. [Features](#features)
2. [Installation](#installation)
3. [Your First Program](#your-first-program)
4. [Variables and Constants](#variables-and-constants)
5. [Displaying Output](#displaying-output)
6. [Conditions](#conditions)
7. [Repeat Loops](#repeat-loops)
8. [Stopping and Skipping Loops](#stopping-and-skipping-loops)
9. [Functions](#functions)
10. [Destroying an Interpreter Instance](#destroying-an-interpreter-instance)
11. [Python Interoperability](#python-interoperability)
12. [Running Tests](#running-tests)
13. [Project Structure](#project-structure)
14. [Safety and Limitations](#safety-and-limitations)
15. [Roadmap](#roadmap)
16. [Contributing](#contributing)

---

## Features

AssayFlux is designed to provide:

- Variables and arithmetic expressions.
- Constant declarations.
- Conditional execution.
- Condition-controlled repeat loops.
- Counted repeat loops.
- Infinite repeat loops with explicit termination.
- User-defined functions.
- Function return values.
- Loop control using `stop` and `skip`.
- Python module imports.
- Runtime error reporting.
- Scientific-computing integration.
- External-runtime orchestration through adapters.
- Interpreter-level execution termination using `destroy()`.

Feature availability depends on the implementation and installed dependencies. Consult the source code and automated tests for the current behavior.

---

## Installation

### Requirements

- Python 3.10 or newer.
- Git.
- A terminal or Python-compatible development environment.

### Clone the repository

```bash
git clone https://github.com/AssayFlux/AssayFlux.git
cd AssayFlux
```

### Install AssayFlux

From the repository root, run:

```bash
python -m pip install .
```

For development, install the project in editable mode:

```bash
python -m pip install -e .
```

Install pytest if it is not already available:

```bash
python -m pip install pytest
```

If the project defines a development dependency group, you can install it with:

```bash
python -m pip install -e ".[dev]"
```

### Run a program

If the package's command-line entry point is configured, run:

```bash
assayflux examples/hello.af
```

Alternatively, try:

```bash
python -m assayflux examples/hello.af
```

The available command depends on the project's package configuration.

---

## Your First Program

Create a file named `hello.af`:

```af
app "Hello AssayFlux"

constant GREETING = "Hello, AssayFlux!"

show GREETING
```

Run the program using the available AssayFlux command.

Expected output:

```text
Hello, AssayFlux!
```

The `app` declaration sets application metadata. The `constant` declaration creates a name that cannot be reassigned. The `show` statement displays its value.

---

## Variables and Constants

### Variables

Variables store values that can change during program execution.

```af
count = 10

show count

count = 20

show count
```

Expected output:

```text
10
20
```

### Constants

Declare a constant using the `constant` keyword.

```af
constant PI = 3.14159
constant MAX_RETRIES = 5
constant APPLICATION_NAME = "AssayFlux"

show PI
show MAX_RETRIES
show APPLICATION_NAME
```

A constant cannot be reassigned after its declaration.

```af
constant LIMIT = 100

LIMIT = 200
```

Attempting to reassign `LIMIT` raises an `AssayFluxRuntimeError`.

Declaring the same constant name again in the same scope also raises an error.

**Current limitation:** Constants prevent reassignment of their declared names. This does not necessarily make every mutable object reachable through a constant deeply immutable.

---

## Displaying Output

Use `show` to display a value.

```af
show "Hello"
show 100
show 3.14
show true
show false
```

Expected output:

```text
Hello
100
3.14
true
false
```

The interpreter prints displayed values to standard output and stores them in its internal output buffer.

Calling `destroy()` clears that interpreter's internal output buffer.

---

## Conditions

Use `if`, `otherwise`, and `else` to control which statements execute.

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

Expected output:

```text
Warm
```

Conditional blocks must be closed with `end`.

### Comparisons

Examples include:

```af
show 10 > 5
show 10 < 5
show 10 == 10
show 10 != 5
show 10 >= 10
show 10 <= 5
```

Boolean operators such as `and`, `or`, and `not` depend on the syntax supported by the current parser.

---

## Repeat Loops

AssayFlux supports condition-controlled, counted, and infinite repeat-loop forms.

### 1. Condition-Controlled Repeat

A condition-controlled loop continues while its condition is true.

```af
counter = 0

repeat counter < 5
    show counter
    counter = counter + 1
end
```

Expected output:

```text
0
1
2
3
4
```

The condition is checked before each iteration.

### 2. Counted Repeat

Use `repeat count` to request a fixed number of iterations.

```af
repeat count 3
    show "AssayFlux"
end
```

Expected output:

```text
AssayFlux
AssayFlux
AssayFlux
```

A count of zero performs no iterations.

```af
repeat count 0
    show "This will not appear"
end
```

Counted loops require a non-negative whole number. Negative, fractional, and excessively large counts are rejected by the interpreter.

You can also use a variable as the count if the parser and expression evaluator support the corresponding expression.

```af
iterations = 4

repeat count iterations
    show "Running"
end
```

### 3. Infinite Repeat

Use `repeat forever` when a loop should continue until explicitly stopped.

```af
counter = 0

repeat forever
    counter = counter + 1
    show counter

    if counter >= 3
        stop
    end
end
```

Expected output:

```text
1
2
3
```

Infinite loops require a termination strategy. The interpreter also enforces a maximum iteration limit to help reduce accidental unbounded execution.

---

## Stopping and Skipping Loops

### The `stop` Statement

`stop` exits the nearest active repeat loop.

```af
counter = 0

repeat forever
    counter = counter + 1

    if counter == 3
        stop
    end
end

show counter
```

Expected output:

```text
3
```

### The `skip` Statement

`skip` skips the remaining statements in the current iteration and advances to the next iteration.

```af
counter = 0
total = 0

repeat counter < 5
    counter = counter + 1

    if counter == 3
        skip
    end

    total = total + counter
end

show total
```

Expected output:

```text
12
```

Both `stop` and `skip` must be used inside a repeat loop.

---

## Functions

Define a function using `f.name(parameters)` and close the definition with `end`.

```af
f.add(a, b)
    return a + b
end

show add(10, 20)
```

Expected output:

```text
30
```

### Functions Without Return Values

```af
f.announce()
    show "AssayFlux is running"
end

announce()
```

Expected output:

```text
AssayFlux is running
```

### Returning Values

```af
f.square(number)
    return number * number
end

show square(5)
```

Expected output:

```text
25
```

Function calls must supply the expected number of arguments.

The interpreter also limits function-call depth to reduce runaway recursion.

---

## Destroying an Interpreter Instance

AssayFlux provides a built-in `destroy()` function.

It terminates the current AssayFlux program and disables the current interpreter instance.

```af
show "Starting"

destroy()

show "This statement will not execute"
```

Execution stops when `destroy()` is called.

### What `destroy()` Does

- Marks the current interpreter instance as destroyed.
- Stops the current AssayFlux execution.
- Clears the interpreter's internal output buffer.
- Clears the interpreter's global variables and constants.
- Clears application metadata held by that instance.
- Prevents that interpreter instance from running another program.

### What `destroy()` Does Not Do

- It does not delete files from your phone or computer.
- It does not delete your GitHub repository.
- It does not erase the operating system.
- It does not clear unrelated Python processes.
- It does not permanently disable the AssayFlux installation.
- It is not a secure memory-erasure mechanism.

### Creating a New Interpreter

After one interpreter has been destroyed, a separate instance can be created for another execution.

Example using Python:

```python
from assayflux.interpreter import Interpreter

first = Interpreter()
first.run('show "First program"\ndestroy()')

second = Interpreter()
second.run('show "Second program"')
```

The first interpreter remains destroyed. The second is a separate instance.

**Important:** `destroy()` is an interpreter lifecycle operation, not an operating-system shutdown command or a secure memory-erasure guarantee.

---

## Python Interoperability

AssayFlux can import Python modules available in the installed Python environment.

Example:

```af
import math

show math.sqrt(25)
```

Expected output:

```text
5.0
```

The available modules depend on your Python installation.

AssayFlux also includes an interoperability layer for coordinating with external runtimes.

External runtimes and libraries may require separate installation and configuration.

**Security warning:** Imported Python modules execute with the permissions of the Python process. AssayFlux is not a secure sandbox for untrusted code.

---

## Running Tests

Run tests from the repository root.

### Using pytest

```bash
python -m pytest -v
```

### Using unittest

```bash
python -m unittest discover -s tests -v
```

The regression tests are intended to cover:

- Parsing and basic execution.
- Arithmetic and output.
- Condition-controlled repeat loops.
- Counted and infinite repeat loops.
- Loop termination and skipping.
- Constant reassignment errors.
- Function calls and return values.
- Python module imports.
- Interpreter destruction.
- Runtime error handling.

A test file existing in the repository does not guarantee that all tests pass. Run the commands and review the actual results.

If a test fails, preserve the complete error message so the implementation can be corrected.

---

## Project Structure

The main project components include:

| Path | Purpose |
|---|---|
| `assayflux/lexer.py` | Converts source code into tokens |
| `assayflux/parser.py` | Parses AssayFlux syntax |
| `assayflux/ast_nodes.py` | Defines abstract syntax tree nodes |
| `assayflux/interpreter.py` | Executes parsed programs |
| `assayflux/interop/` | Interoperability and runtime adapters |
| `examples/` | Example `.af` programs |
| `tests/` | Automated regression tests |
| `docs/` | Language specifications and development documentation |
| `README.md` | Project overview and usage instructions |

The exact contents may change as development continues.

---

## Safety and Limitations

AssayFlux is experimental software. Keep the following limitations in mind.

1. **Not a security sandbox:** Python imports can access resources permitted to the Python process.
2. **External runtimes:** An adapter's existence does not prove that its external runtime is installed or functional.
3. **Execution limits:** Loop and function-call limits help reduce runaway execution but do not make arbitrary code safe.
4. **Constants:** Preventing name reassignment is not equivalent to deep immutability.
5. **Destruction:** `destroy()` clears selected state belonging to one interpreter instance. It does not guarantee secure memory erasure.
6. **Scientific correctness:** Scientific calculations and instrument-control workflows require independent validation before real laboratory use.
7. **Third-party dependencies:** Imported modules and external runtimes may have their own security and compatibility limitations.

Do not run untrusted programs with access to sensitive data or privileged resources.

---

## Roadmap

Potential development areas include:

- Expanding automated regression coverage.
- Improving syntax and runtime diagnostics.
- Strengthening constant and type semantics.
- Adding validated scientific-computing workflows.
- Improving interoperability and external-runtime management.
- Expanding language examples and documentation.
- Developing editor and mobile development workflows.
- Adding clearer runtime configuration and execution controls.
- Improving automated build and release processes.

Roadmap items are development goals, not guarantees that a feature is already implemented.

---

## Contributing

When changing AssayFlux:

1. Review the existing implementation before modifying behavior.
2. Update the language specification when syntax or semantics change.
3. Add regression tests for new features and bug fixes.
4. Run the test suite.
5. Review backward compatibility.
6. Update documentation to match actual implementation behavior.
7. Report unsupported integrations honestly.

Bug reports should include:

- A minimal source-code example.
- Expected behavior.
- Actual behavior.
- The relevant error message.
- Python and AssayFlux versions.
- Relevant test results, if available.

---

## License

See the repository's license file for the applicable license terms.