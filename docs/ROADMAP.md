# AssayFlux Scientific Systems — Development Roadmap

**Language:** AssayFlux Scientific Systems  
**Short name:** AssayFlux  
**Version:** 0.1.0  
**Source extension:** `.af`  
**Project status:** Early development

---

## 1. Vision

AssayFlux aims to become a general-purpose programming language with a strong focus on scientific computing and interoperability.

The project will provide its own syntax, parser, interpreter, runtime, and development tools while reusing existing libraries and language runtimes wherever practical.

The long-term vision includes:

- A custom programming language.
- Scientific computing through existing libraries.
- Python integration as the first interoperability target.
- Future integration with C, C++, Java, JavaScript, and Rust.
- A command-line development environment.
- A dedicated Android IDE.
- Clear documentation and automated testing.

These are development goals, not claims that all features are already implemented.

## 2. Development Principles

AssayFlux development follows these principles:

1. **Correctness first:** Implement and test language behavior before expanding features.
2. **Strict syntax:** Four-space indentation and explicit `end` statements are mandatory.
3. **Modular architecture:** Keep the lexer, parser, AST, interpreter, and adapters separate.
4. **Reuse existing technology:** Prefer established libraries over recreating mature scientific functionality.
5. **Incremental development:** Complete and verify one milestone before building on it.
6. **Test-driven verification:** Every significant feature should have automated tests.
7. **Honest status reporting:** Clearly distinguish implemented, partially implemented, and planned features.
8. **Portability:** Document platform and dependency limitations.
9. **Security awareness:** Treat external code execution as potentially unsafe.
10. **Documentation consistency:** Keep specifications, examples, implementation, and tests aligned.

---

# Phase 1 — Finalize the Language Design

**Goal:** Establish one consistent definition of AssayFlux syntax and behavior.

### Tasks

- [x] Establish the initial repository structure.
- [x] Create the initial language specification.
- [x] Define the draft grammar.
- [x] Define the core language syntax.
- [x] Establish strict indentation requirements.
- [x] Require explicit `end` statements for blocks.
- [x] Define the `!=` not-equal operator.
- [x] Define single- and double-quoted strings.
- [x] Define the `f.` function declaration syntax.
- [x] Define the `show` output statement.
- [ ] Review the grammar for ambiguities.
- [ ] Define operator precedence and associativity precisely.
- [ ] Define variable scope and constant semantics.
- [ ] Define function return and argument semantics.
- [ ] Define import behavior and error handling.
- [ ] Verify consistency across all documentation.

**Completion criteria:**

The language specification and grammar must describe compatible syntax and semantics. The grammar should be validated against representative valid and invalid programs before being treated as authoritative.

---

# Phase 2 — Stabilize the Core Interpreter

**Goal:** Make the implemented language behavior match the finalized specification.

## 2.1 Lexer

### Tasks

- [ ] Recognize all supported keywords.
- [ ] Recognize identifiers and literals.
- [ ] Support single- and double-quoted strings.
- [ ] Recognize arithmetic and comparison operators.
- [ ] Recognize `!=` correctly.
- [ ] Reject the invalid `nt=` form.
- [ ] Track source line and column positions.
- [ ] Handle comments consistently.
- [ ] Validate indentation.
- [ ] Reject tabs used for indentation.
- [ ] Detect malformed and unterminated strings.
- [ ] Add lexer unit tests.

## 2.2 Parser

### Tasks

- [ ] Align parsing rules with the finalized grammar.
- [ ] Parse assignments and constants.
- [ ] Parse arithmetic and logical expressions.
- [ ] Parse `show` statements.
- [ ] Parse conditional branches.
- [ ] Parse loops and loop-control statements.
- [ ] Parse function declarations and calls.
- [ ] Parse return statements.
- [ ] Enforce explicit block endings.
- [ ] Enforce the required block structure.
- [ ] Report useful syntax errors.
- [ ] Add parser unit tests.

## 2.3 Abstract Syntax Tree

### Tasks

- [ ] Verify that AST nodes represent supported syntax.
- [ ] Keep AST structures independent of unnecessary source-format details.
- [ ] Ensure parser output is consistent.
- [ ] Add tests for AST construction.
- [ ] Avoid adding nodes for unsupported features without a clear implementation plan.

## 2.4 Interpreter

### Tasks

- [ ] Implement and verify variable assignment.
- [ ] Implement and verify constant declarations.
- [ ] Implement supported arithmetic operations.
- [ ] Implement comparison and logical operations.
- [ ] Implement `show`.
- [ ] Implement `if`, `otherwise`, and `else`.
- [ ] Implement `repeat`.
- [ ] Implement `stop` and `skip`.
- [ ] Implement function declarations and calls.
- [ ] Implement return behavior.
- [ ] Define and test variable scope.
- [ ] Report runtime errors clearly.
- [ ] Add interpreter integration tests.

**Completion criteria:**

The supported core syntax must execute correctly, invalid programs must be rejected, and automated tests must pass.

---

# Phase 3 — Establish the Language Test Suite

**Goal:** Make language behavior verifiable and prevent regressions.

### Tasks

- [ ] Organize lexer, parser, interpreter, and interoperability tests.
- [ ] Add tests for every implemented language feature.
- [ ] Test valid programs.
- [ ] Test invalid syntax.
- [ ] Test incorrect indentation.
- [ ] Test missing `end` statements.
- [ ] Test nested conditional blocks.
- [ ] Test nested loops.
- [ ] Test function arguments and return values.
- [ ] Test undefined names.
- [ ] Test constant reassignment.
- [ ] Test runtime error reporting.
- [ ] Add complete `.af` program tests.
- [ ] Run the complete test suite through GitHub Actions.

**Completion criteria:**

All tests in the supported feature set pass in the intended development environment. Unsupported features are documented instead of being assumed to work.

---

# Phase 4 — Complete Python Interoperability

**Goal:** Allow AssayFlux programs to reuse selected Python libraries through a defined integration interface.

The repository already contains an interoperability foundation and a Python adapter. The next task is to connect that foundation to the actual AssayFlux language runtime.

## 4.1 Adapter Infrastructure

- [x] Establish a common adapter interface.
- [x] Establish an adapter registry.
- [x] Establish an adapter loader.
- [x] Establish an interoperability runtime.
- [x] Create an initial Python adapter.
- [x] Add initial adapter tests.
- [ ] Verify the current adapter implementation against its tests.
- [ ] Document the adapter API.
- [ ] Define consistent error handling.

## 4.2 Connect Imports to AssayFlux

- [ ] Define the exact import grammar.
- [ ] Parse `import module`.
- [ ] Parse `import module as alias`.
- [ ] Resolve supported Python modules.
- [ ] Store imported modules in the appropriate environment.
- [ ] Support member access on imported modules.
- [ ] Connect function calls to supported external functions.
- [ ] Define argument conversion.
- [ ] Define return-value conversion.
- [ ] Propagate external exceptions appropriately.
- [ ] Add import integration tests.
- [ ] Verify that `.af` programs can use supported Python modules.

### Intended Syntax

```assayflux
import math

result = math.sqrt(25)
show result
```

The example represents the intended interface. It should be considered supported only after the implementation and integration tests pass.

## 4.3 Scientific Libraries

Investigate and test integration with:

- NumPy — numerical arrays and computation.
- SciPy — scientific algorithms.
- SymPy — symbolic mathematics.
- pandas — tabular data.
- Matplotlib — plotting and visualization.

### Tasks

- [ ] Establish how optional Python dependencies are managed.
- [ ] Test library availability.
- [ ] Document supported versions.
- [ ] Test representative library calls.
- [ ] Document platform limitations.
- [ ] Avoid requiring every scientific library as a mandatory dependency.

**Completion criteria:**

A documented set of Python modules can be imported and used from AssayFlux programs, with tested value conversion and error handling.

---

# Phase 5 — Improve the Command-Line Experience

**Goal:** Make AssayFlux practical to execute and test.

### Tasks

- [ ] Verify the configured command-line entry point.
- [ ] Implement or stabilize file execution.
- [ ] Support running `.af` source files.
- [ ] Display program output.
- [ ] Report syntax errors with useful locations.
- [ ] Report runtime errors clearly.
- [ ] Return appropriate process exit codes.
- [ ] Provide help and usage information.
- [ ] Document installation and execution.
- [ ] Add command-line tests.

### Intended Usage

The exact command depends on the implemented CLI.

A future usage example may look like:

```bash
assayflux examples/hello.af
```

This command must not be documented as working until the corresponding entry point and file execution behavior are implemented and tested.

**Completion criteria:**

Users can install the package in a documented environment and execute supported `.af` files through a tested command-line interface.

---

# Phase 6 — Design the Standard Library

**Goal:** Provide useful built-in functionality while reusing established external libraries.

### Potential Components

- Mathematical utilities.
- String operations.
- Collection operations.
- Type conversion.
- File handling.
- Path handling.
- Error utilities.
- Basic scientific helpers.

### Tasks

- [ ] Identify functionality that genuinely belongs in the language.
- [ ] Avoid duplicating established libraries unnecessarily.
- [ ] Define stable interfaces.
- [ ] Implement only documented features.
- [ ] Add unit tests.
- [ ] Document examples and limitations.

**Completion criteria:**

The standard library has a clearly defined scope, stable behavior, and automated tests.

---

# Phase 7 — Explore Additional Language Integrations

**Goal:** Extend AssayFlux interoperability beyond Python.

These integrations should begin only after the adapter interface and Python integration are sufficiently stable.

## 7.1 C

Potential approaches:

- Native library integration.
- Foreign-function interfaces.
- Compiled extension modules.

Tasks:

- [ ] Evaluate suitable interoperability mechanisms.
- [ ] Define function and type conversions.
- [ ] Handle native errors and resource ownership.
- [ ] Build a small proof of concept.
- [ ] Add integration tests.

## 7.2 C++

Potential approaches:

- Native libraries.
- C-compatible interfaces.
- Compatible extension mechanisms.

Tasks:

- [ ] Evaluate ABI and compiler compatibility.
- [ ] Define supported types.
- [ ] Define memory-management rules.
- [ ] Build a proof of concept.
- [ ] Add integration tests.

## 7.3 Java

Potential approaches:

- JVM-based execution.
- Java interoperability layers.
- Supported external Java processes.

Tasks:

- [ ] Evaluate runtime requirements.
- [ ] Define value conversion.
- [ ] Define exception handling.
- [ ] Build a proof of concept.
- [ ] Test supported environments.

## 7.4 JavaScript

Potential approaches:

- Embedded JavaScript runtime.
- External JavaScript runtime.
- A defined adapter interface.

Tasks:

- [ ] Evaluate runtime availability.
- [ ] Define execution and data-exchange semantics.
- [ ] Handle errors and timeouts.
- [ ] Build a proof of concept.
- [ ] Add integration tests.

## 7.5 Rust

Potential approaches:

- Native libraries.
- C-compatible interfaces.
- Compiled extension modules.

Tasks:

- [ ] Evaluate suitable interoperability mechanisms.
- [ ] Define supported data types.
- [ ] Handle ownership and resource lifetimes.
- [ ] Build a proof of concept.
- [ ] Add integration tests.

**Completion criteria:**

Each additional integration must have a documented implementation, explicit limitations, reproducible setup instructions, and automated tests.

No language should be marked as supported merely because a possible integration mechanism has been identified.

---

# Phase 8 — Improve Developer Tools

**Goal:** Make AssayFlux easier to develop, debug, and maintain.

### Potential Features

- Syntax checking.
- Improved diagnostics.
- Source location tracking.
- Debugging support.
- Better error messages.
- Module inspection.
- Package management improvements.
- Formatting and linting tools.

### Tasks

- [ ] Identify the most useful developer features.
- [ ] Define their interfaces.
- [ ] Implement them incrementally.
- [ ] Add automated tests.
- [ ] Document their usage.

**Completion criteria:**

Each released tool has a documented purpose, predictable behavior, and appropriate tests.

---

# Phase 9 — Build the Android IDE

**Goal:** Provide an Android application for writing, managing, and executing AssayFlux programs.

The initial target device is a Motorola Moto G54 5G running Android 15.

The development environment may use Google Colab, with the repository maintained on GitHub.

## 9.1 Project Design

- [ ] Select the Android application architecture.
- [ ] Determine how the interpreter will run on Android.
- [ ] Identify required runtime dependencies.
- [ ] Establish a build and testing process.
- [ ] Define the communication interface between the IDE and execution engine.

## 9.2 Editor

- [ ] Create a source editor.
- [ ] Support `.af` files.
- [ ] Add syntax highlighting.
- [ ] Display line numbers.
- [ ] Provide indentation assistance.
- [ ] Display syntax and runtime errors.

## 9.3 Project Management

- [ ] Open existing AssayFlux projects.
- [ ] Create and edit `.af` files.
- [ ] Save project files.
- [ ] Manage examples and modules.
- [ ] Provide clear file-operation errors.

## 9.4 Execution

- [ ] Run supported AssayFlux programs.
- [ ] Display standard output and errors.
- [ ] Provide execution status.
- [ ] Handle long-running programs appropriately.
- [ ] Prevent the user interface from freezing during execution.
- [ ] Define permissions and security boundaries.

## 9.5 Device Testing

- [ ] Build the application.
- [ ] Install it on the target device.
- [ ] Test file access.
- [ ] Test program execution.
- [ ] Test editor usability.
- [ ] Test error reporting.
- [ ] Document known limitations.

**Completion criteria:**

The Android IDE can edit, save, and execute supported AssayFlux programs on documented devices and environments.

---

# Phase 10 — Release Preparation

**Goal:** Prepare a reproducible and maintainable release.

### Tasks

- [ ] Review the language specification.
- [ ] Verify all documented syntax.
- [ ] Run automated tests.
- [ ] Review dependencies.
- [ ] Document installation.
- [ ] Document supported platforms.
- [ ] Document known limitations.
- [ ] Review security implications.
- [ ] Update the changelog.
- [ ] Select and add an appropriate open-source license if intended.
- [ ] Define versioning rules.
- [ ] Tag the release when its criteria are satisfied.

**Completion criteria:**

A release must have reproducible setup instructions, verified functionality, passing tests, and accurate documentation.

---

# Milestone Summary

| Milestone | Main objective | Status |
|---|---|---|
| M1 | Establish repository and language design | In progress |
| M2 | Stabilize lexer, parser, AST, and interpreter | In progress |
| M3 | Establish reliable automated testing | In progress |
| M4 | Connect Python interoperability to `.af` programs | Planned |
| M5 | Stabilize the command-line interface | To be verified |
| M6 | Design and test the standard library | Planned |
| M7 | Investigate additional language integrations | Planned |
| M8 | Improve developer tools | Planned |
| M9 | Build the Android IDE | Planned |
| M10 | Prepare a verified release | Planned |

Milestone status must be updated based on actual code and test results, not documentation changes alone.

---

# Immediate Next Actions

The recommended next steps are:

1. Finish aligning the documentation with the finalized language design.
2. Inspect the current lexer, parser, AST, and interpreter before changing code.
3. Compare the implementation with `docs/GRAMMAR.md`.
4. Implement strict four-space indentation validation.
5. Enforce explicit block endings.
6. Implement and test the finalized string and operator syntax.
7. Run the full automated test suite.
8. Update `docs/SPECIFICATION_STATUS.md` with verified results.
9. Connect Python imports to the existing interoperability runtime.
10. Continue toward the command-line interface and Android IDE.

Do not skip implementation verification just to advance the roadmap.

---

# Definition of Done

A feature is complete only when:

- Its intended behavior is documented.
- Its implementation exists.
- Its automated tests cover the relevant behavior.
- The tests pass in the intended environment.
- Its dependencies and limitations are understood.
- Its status is accurately recorded.
- Related examples and documentation are consistent.

A planned feature is not a supported feature.

---

**End of AssayFlux Development Roadmap**