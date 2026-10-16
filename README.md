# AssayFlux Scientific Systems

**AssayFlux** is an experimental programming language implemented in Python for scientific computing, automation, and multi-runtime orchestration.

- **Language:** AssayFlux
- **Source extension:** `.af`
- **Current development version:** 0.3.0
- **Implementation:** Python
- **Repository:** https://github.com/AssayFlux/AssayFlux

> **Development status:** AssayFlux is an experimental project. Features and integrations may change. An available language adapter does not guarantee that its external runtime is installed or fully supported.

---

## Contents

1. [Features](#features)
2. [Installation](#installation)
3. [Your first program](#your-first-program)
4. [Variables and constants](#variables-and-constants)
5. [Displaying output](#displaying-output)
6. [Conditions](#conditions)
7. [Repeat loops](#repeat-loops)
8. [Stopping and skipping loops](#stopping-and-skipping-loops)
9. [Functions](#functions)
10. [Destroying an interpreter instance](#destroying-an-interpreter-instance)
11. [Python interoperability](#python-interoperability)
12. [Running tests](#running-tests)
13. [Project structure](#project-structure)
14. [Safety and limitations](#safety-and-limitations)
15. [Roadmap](#roadmap)
16. [Contributing](#contributing)

---

## Features

The core language is designed to provide:

- Variables and arithmetic expressions.
- Constant declarations.
- Conditional execution.
- Condition-controlled repeat loops.
- Counted repeat loops.
- Infinite repeat loops with explicit termination.
- User-defined functions.
- Return values.
- Loop control with `stop` and `skip`.
- Python module imports.
- Runtime error reporting.
- Scientific and external-runtime integration through adapters.
- An interpreter-level `destroy()` operation.

Feature availability depends on the implementation and installed dependencies. Consult the source code and tests for the current behavior.

---

## Installation

### Requirements

- Python 3.10 or newer.
- Git.
- A terminal or Python-compatible development environment.

Clone the repository:

```bash
git clone https://github.com/AssayFlux/AssayFlux.git
cd AssayFlux