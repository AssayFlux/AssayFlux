<div align="center">

<img src="assayflux-logo.png" alt="AssayFlux" width="620">



### A Python-Interoperable Programming Language

Readable syntax. Structured execution. Python interoperability.

<br>

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)
![Version](https://img.shields.io/badge/Version-0.3.0-00A99D?style=flat-square)
![Status](https://img.shields.io/badge/Status-Experimental-8B5CF6?style=flat-square)
![Tests](https://img.shields.io/badge/Tests-Automated-22C55E?style=flat-square)
![License](https://img.shields.io/badge/License-Open_Source-F59E0B?style=flat-square)

[Overview](#overview) ·
[Features](#features) ·
[Example](#quick-example) ·
[Installation](#getting-started) ·
[Testing](#testing) ·
[Roadmap](#roadmap)

</div>

---

<div align="center">

`LANGUAGE DESIGN` &nbsp; │ &nbsp; `PYTHON ECOSYSTEM` &nbsp; │ &nbsp; `OPEN DEVELOPMENT`

</div>

## Overview

AssayFlux is an experimental programming-language project exploring readable syntax, structured execution, and interoperability with Python.

The repository contains a language lexer, parser, abstract syntax tree, interpreter, command-line interface, automated tests, examples, and adapters for external programming-language runtimes.

<table>
<tr>
<td width="50%" valign="top">

### <span style="color:#EF4444">Core Language</span>

- Variables and constants
- Arithmetic expressions
- Conditions and comparisons
- Repeat loops
- Functions and return values
- Structured program execution

</td>
<td width="50%" valign="top">

### <span style="color:#F59E0B">Program Structure</span>

- Readable source syntax
- Lexer and parser
- Abstract syntax tree
- Runtime error handling
- Loop control
- Command-line execution

</td>
</tr>
<tr>
<td width="50%" valign="top">

### <span style="color:#10B981">Python Interoperability</span>

- Python module imports
- Supported Python functionality
- Integration with the Python ecosystem
- External-runtime adapters

</td>
<td width="50%" valign="top">

### <span style="color:#8B5CF6">Development</span>

- Automated test suite
- Example programs
- GitHub Actions
- Runtime integration tests
- Language documentation

</td>
</tr>
</table>

## Quick Example

Create a file named `hello.af`:

```text
app "Hello AssayFlux"

constant GREETING = "Hello, AssayFlux!"

show GREETING