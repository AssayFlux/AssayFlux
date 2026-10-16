<div align="center">

<img src="assayflux-logo.png" alt="AssayFlux" width="680">

<br>

#

### A Python-Interoperable Programming Language
<br>
**Readable syntax. Structured execution. Python interoperability.**

<br>

<a href="https://github.com/AssayFlux/AssayFlux/actions">
  <img src="https://img.shields.io/badge/BUILD-GitHub%20Actions-3776AB?style=flat-square&logo=githubactions&logoColor=white" alt="GitHub Actions">
</a>
<a href="https://www.python.org/">
  <img src="https://img.shields.io/badge/POWERED%20BY-Python-4B6CB7?style=flat-square&logo=python&logoColor=white" alt="Python">
</a>
<img src="https://img.shields.io/badge/STATUS-Experimental-8A63D2?style=flat-square" alt="Experimental project">

<br><br>

[Overview](#overview) ·
[Features](#features) ·
[Example](#quick-example) ·
[Getting Started](#getting-started) ·
[Testing](#testing) ·
[Roadmap](#roadmap)

</div>

---

<div align="center">

`LANGUAGE DESIGN` &nbsp; | &nbsp; `PYTHON ECOSYSTEM` &nbsp; | &nbsp; `OPEN DEVELOPMENT`

</div>

## Overview

AssayFlux is an experimental programming-language project exploring readable syntax, structured program execution, and interoperability with Python.

The repository contains a language parser, an interpreter, example programs, documentation, and automated tests. Its design provides a foundation for experimenting with language features and building accessible programming tools.

## Features

<table>
<tr>
<td width="50%" valign="top">

#### <span style="color:#E53935">01 / Core language</span>

- Variables and constants
- Arithmetic expressions
- Comparisons and logical operations
- Conditional execution
- Repetition and loop control

</td>
<td width="50%" valign="top">

#### <span style="color:#FB8C00">02 / Program structure</span>

- User-defined functions
- Function arguments and return values
- Output statements
- Structured execution
- Parser and runtime error handling

</td>
</tr>
<tr>
<td width="50%" valign="top">

#### <span style="color:#43A047">03 / Python interoperability</span>

- Python module imports
- Access to supported module functionality
- Integration with the Python ecosystem

</td>
<td width="50%" valign="top">

#### <span style="color:#5E35B1">04 / Development</span>

- Automated test suite
- Example programs
- GitHub-based development
- Continuous integration workflows

</td>
</tr>
</table>

Features reflect the current project implementation; capabilities and syntax may evolve during development.

## Quick Example

A simple AssayFlux program:

```text
app "My First Program"

constant LIMIT = 3

counter = 0

repeat counter < LIMIT
    counter = counter + 1
    show counter
end
```

**Output**

```text
1
2
3
```

### Python interoperability

AssayFlux supports importing Python modules through its language syntax.

```text
import math

show math.sqrt(25)
```

**Output**

```text
5.0
```

Refer to the source code and automated tests for the authoritative description of supported syntax and behavior.

## Getting Started

### Requirements

- Python 3
- Git

### Clone the repository

```bash
git clone https://github.com/AssayFlux/AssayFlux.git
cd AssayFlux
```

### Project structure

| Directory or file | Purpose |
|---|---|
| `assayflux/` | Language implementation |
| `examples/` | Example programs |
| `tests/` | Automated tests |
| `DOCS/` | Project documentation |
| `.github/` | Repository workflows and configuration |
| `pyproject.toml` | Python project configuration |

To execute a program, follow the current project documentation and the execution interface implemented in the repository.

## Testing

Run the unit tests from the repository root:

```bash
python -m unittest discover -s tests -v
```

Alternatively, if `pytest` is installed:

```bash
python -m pytest -v
```

### Continuous integration

GitHub Actions provides automated repository checks.

<div align="center">

[![GitHub Actions](https://img.shields.io/badge/WORKFLOWS-View%20GitHub%20Actions-2088FF?style=for-the-badge&logo=githubactions&logoColor=white)](https://github.com/AssayFlux/AssayFlux/actions)

</div>

## Roadmap

Potential areas of future development include:

<table>
<tr>
<td width="50%" valign="top">

**Language and documentation**

- [ ] Expand language documentation
- [ ] Add tutorials and example programs
- [ ] Extend automated test coverage
- [ ] Improve error diagnostics

</td>
<td width="50%" valign="top">

**Developer experience**

- [ ] Explore interactive coding tools
- [ ] Improve debugging support
- [ ] Explore scientific-computing workflows
- [ ] Improve usability and accessibility

</td>
</tr>
</table>

Roadmap items are development possibilities, not claims of completed functionality.

## Contributing

Contributions, bug reports, documentation improvements, and constructive suggestions are welcome.

1. Review the existing implementation and tests.
2. Open an issue to discuss substantial changes.
3. Submit a pull request with a clear description and relevant tests.

Read the [contribution guidelines](CONTRIBUTING.md) before submitting changes.

## Security

For information about reporting security vulnerabilities, consult the [security policy](SECURITY.md).

## License

The repository contains a `LICENSE` file. Review it for the applicable terms governing use, modification, and redistribution.

## Project Links

<table>
<tr>
<td align="center" width="25%">

**Source**

[Repository](https://github.com/AssayFlux/AssayFlux)

</td>
<td align="center" width="25%">

**Support**

[Issues](https://github.com/AssayFlux/AssayFlux/issues)

</td>
<td align="center" width="25%">

**Automation**

[Actions](https://github.com/AssayFlux/AssayFlux/actions)

</td>
<td align="center" width="25%">

**Guidelines**

[Contributing](CONTRIBUTING.md)

</td>
</tr>
</table>

---

<div align="center">

### <span style="color:#E53935">R</span><span style="color:#FB8C00">e</span><span style="color:#F9A825">a</span><span style="color:#43A047">d</span><span style="color:#1E88E5">a</span><span style="color:#3949AB">b</span><span style="color:#8E24AA">l</span><span style="color:#E53935">e</span> <span style="color:#FB8C00">C</span><span style="color:#F9A825">o</span><span style="color:#43A047">d</span><span style="color:#1E88E5">e</span><span style="color:#3949AB">.</span> <span style="color:#8E24AA">S</span><span style="color:#E53935">c</span><span style="color:#FB8C00">i</span><span style="color:#F9A825">e</span><span style="color:#43A047">n</span><span style="color:#1E88E5">c</span><span style="color:#3949AB">e</span><span style="color:#8E24AA">.</span> <span style="color:#E53935">P</span><span style="color:#FB8C00">o</span><span style="color:#F9A825">s</span><span style="color:#43A047">s</span><span style="color:#1E88E5">i</span><span style="color:#3949AB">b</span><span style="color:#8E24AA">i</span><span style="color:#E53935">l</span><span style="color:#FB8C00">i</span><span style="color:#F9A825">t</span><span style="color:#43A047">i</span><span style="color:#1E88E5">e</span><span style="color:#3949AB">s</span><span style="color:#8E24AA">.</span>

**AssayFlux**

[Explore the source code](https://github.com/AssayFlux/AssayFlux)

</div>