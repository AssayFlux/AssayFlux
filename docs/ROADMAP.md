# AssayFlux Scientific Systems — Development Roadmap

**Project:** AssayFlux  
**Version:** 0.1.0  
**Source file extension:** `.af`

## Phase 1: Core Language

- [x] Create the GitHub repository.
- [x] Define the initial language syntax.
- [x] Implement the lexer.
- [x] Implement the abstract syntax tree.
- [x] Implement the parser.
- [x] Create the initial interpreter.
- [ ] Verify the lexer, parser, and interpreter with automated tests.
- [ ] Fix implementation errors.
- [ ] Implement user input using `input()`.
- [ ] Improve error messages with line numbers.
- [ ] Add complete variable and data type support.
- [ ] Implement and test functions, conditionals, and loops.

## Phase 2: AssayFlux Standard Library

- [ ] Create built-in functions.
- [ ] Add mathematical utilities.
- [ ] Add string operations.
- [ ] Add list and collection support.
- [ ] Implement a module and import system.
- [ ] Add file handling.
- [ ] Add exception handling.

## Phase 3: Multi-Language Integration

### Python
- [ ] Execute Python functions from AssayFlux.
- [ ] Pass values between AssayFlux and Python.
- [ ] Import selected Python modules.

### C and C++
- [ ] Investigate native function interfaces.
- [ ] Design a safe interface for compiled libraries.
- [ ] Support selected native extensions.

### Java
- [ ] Investigate JVM interoperability.
- [ ] Design a Java class and method interface.

### JavaScript
- [ ] Investigate JavaScript runtime integration.
- [ ] Design a JavaScript function interface.

### Rust
- [ ] Investigate Rust library interoperability.
- [ ] Design interfaces for selected compiled libraries.

## Phase 4: Developer Tools

- [ ] Create a command-line interface.
- [ ] Add syntax checking.
- [ ] Add debugging tools.
- [ ] Add formatted error reports.
- [ ] Create a package and module manager.
- [ ] Publish installation instructions.

## Phase 5: Android IDE

- [ ] Design the AssayFlux editor.
- [ ] Add syntax highlighting for `.af` files.
- [ ] Add a code editor and file manager.
- [ ] Add program execution and console output.
- [ ] Integrate diagnostics.
- [ ] Test on Android devices.

## Phase 6: Release Preparation

- [ ] Complete automated tests.
- [ ] Document the language specification.
- [ ] Document installation and usage.
- [ ] Test supported integrations.
- [ ] Prepare version 0.1.0 for an initial release.

## Architecture Principle

AssayFlux should remain the primary language and provide a consistent interface for supported languages.

Language integrations should be implemented as separate components wherever practical. Each integration must define how values, function calls, errors, dependencies, and execution are handled.

Integration support will be added incrementally. A language should not be described as supported until its integration has been implemented and tested.