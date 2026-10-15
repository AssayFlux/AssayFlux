# AssayFlux Scientific Systems — Architecture

**Language:** AssayFlux Scientific Systems  
**Short name:** AssayFlux  
**Version:** 0.1.0  
**Status:** Early development

---

## 1. Overview

AssayFlux is a custom programming language designed for scientific computing and multi-language interoperability.

Its architecture separates language processing, execution, external language integration, testing, and developer tools into modular components.

The initial implementation uses Python. The long-term goal is to enable AssayFlux programs to reuse capabilities from Python, C, C++, Java, JavaScript, and Rust.

These integrations are development goals and must not be considered supported until implemented and tested.

## 2. Architectural Goals

The architecture should provide:

- A clear separation between language components.
- Predictable parsing and execution.
- Strict indentation and explicit block endings.
- Reusable scientific libraries.
- A modular interoperability system.
- Consistent error reporting.
- Automated testing.
- Portability across supported environments.
- A foundation for a future Android IDE.

## 3. High-Level Architecture

The intended execution pipeline is:

```text
AssayFlux Source File (.af)
          |
          v
       Source Reader
          |
          v
         Lexer
          |
          v
         Tokens
          |
          v
         Parser
          |
          v
 Abstract Syntax Tree (AST)
          |
          v
      Interpreter
          |
          +--------------------+
          |                    |
          v                    v
   Native Language       Interoperability
     Operations              Runtime
                               |
                   +-----------+-----------+
                   |           |           |
                   v           v           v
                Python     Native Code   Other Runtimes
                            Integration   (Future)
```

This diagram describes the intended architecture. The exact implementation may evolve.

## 4. Repository Structure

The repository is organized into implementation, interoperability, testing, examples, and documentation.

```text
AssayFlux/
|
|-- assayflux/
|   |-- __init__.py
|   |-- lexer.py
|   |-- ast_nodes.py
|   |-- parser.py
|   |-- interpreter.py
|   |-- __main__.py
|   |
|   |-- interop/
|       |-- __init__.py
|       |-- base.py
|       |-- registry.py
|       |-- loader.py
|       |-- runtime.py
|       |
|       |-- adapters/
|           |-- python_adapter.py
|
|-- tests/
|-- examples/
|-- docs/
|-- .github/
|   |-- workflows/
|       |-- tests.yml
|
|-- pyproject.toml
|-- README.md
|-- .gitignore
```

This is a conceptual overview of the project structure. Check the repository for the actual files currently present.

## 5. Source Reader

The source reader obtains AssayFlux source code from a file or another supported input source.

### Responsibilities

- Read `.af` source files.
- Preserve source locations where possible.
- Pass source text to the lexer.
- Report file-reading errors.

The source reader should not execute program instructions.

## 6. Lexer

The lexer converts source text into tokens.

### Responsibilities

- Recognize identifiers and keywords.
- Recognize numbers and string literals.
- Recognize operators and punctuation.
- Recognize comments.
- Detect invalid characters.
- Track line and column positions.
- Support strict indentation validation, either directly or through a dedicated layout-processing component.

### Language Rules

- Strings use single or double quotes.
- Comments begin with `#`.
- The not-equal operator is `!=`.
- The invalid form `nt=` must not be accepted as a not-equal operator.
- Indentation uses four spaces per level.
- Tabs are prohibited for indentation.

The lexer should provide useful error locations when tokenization fails.

## 7. Parser

The parser transforms tokens into an Abstract Syntax Tree.

### Responsibilities

- Recognize valid statements.
- Parse expressions according to operator precedence.
- Parse assignments and constants.
- Parse conditional branches.
- Parse loops.
- Parse function declarations and calls.
- Parse return statements.
- Parse import statements when implemented.
- Enforce block structure and matching `end` statements.
- Reject invalid syntax.

The parser should report syntax errors without silently accepting malformed programs.

## 8. Abstract Syntax Tree

The AST represents the structure of an AssayFlux program.

Potential node categories include:

| Node | Purpose |
|---|---|
| Program | Represents the complete program. |
| Literal | Represents a literal value. |
| Variable reference | Reads a named value. |
| Assignment | Assigns a value to a variable. |
| Constant declaration | Declares a constant. |
| Binary expression | Represents an operation with two operands. |
| Unary expression | Represents a single-operand operation. |
| Output statement | Represents `show`. |
| Conditional statement | Represents `if`, `otherwise`, and `else`. |
| Loop statement | Represents `repeat`. |
| Function declaration | Represents an `f.` function definition. |
| Function call | Represents a call to a function. |
| Return statement | Returns a value from a function. |
| Import statement | Represents a module import. |

These categories describe the intended design. Names and exact structures depend on the implementation.

The AST should be independent of source formatting wherever possible, while the parser remains responsible for enforcing formatting requirements.

## 9. Interpreter

The interpreter evaluates the AST and executes program statements.

### Responsibilities

- Evaluate expressions.
- Manage variables and constants.
- Execute output statements.
- Evaluate conditional branches.
- Execute loops.
- Handle loop control.
- Define and invoke functions.
- Implement return behavior.
- Resolve supported imports.
- Propagate runtime errors.
- Invoke interoperability components when required.

The interpreter should not contain unnecessary language-specific adapter logic. External execution should be handled by the interoperability layer.

## 10. Environment and Scope

The runtime environment stores names and their associated values.

### Responsibilities

- Store variable bindings.
- Store constant bindings.
- Resolve identifiers.
- Manage function definitions.
- Manage local and global scope.
- Report undefined names.
- Enforce constant reassignment rules.

The exact scope rules must be defined by the language specification.

Function-local variables should not accidentally overwrite global variables unless the language explicitly defines that behavior.

## 11. Function Execution

AssayFlux function declarations use the `f.` prefix.

Example:

```assayflux
f.add(a, b)
    return a + b
end

result = add(10, 20)
show result
```

### Intended Execution Process

1. Parse the function declaration.
2. Register the function in the appropriate environment.
3. Evaluate the arguments when the function is called.
4. Bind arguments to parameters.
5. Execute the function body.
6. Process the return statement.
7. Return the resulting value to the caller.

Recursive calls, argument validation, scope behavior, and return semantics must be covered by tests.

## 12. Strict Block Formatting

AssayFlux requires indentation and explicit block endings.

### Rules

- Use four spaces per indentation level.
- Do not use tabs for indentation.
- Indent statements inside blocks.
- Indent nested blocks further.
- Align `otherwise` and `else` with their corresponding `if`.
- Align `end` with the block-opening keyword.
- Require a matching `end` for every block that needs one.

Example:

```assayflux
if true
    show "Outer block"

    if true
        show "Inner block"
    end
end
```

Formatting validation should produce clear errors rather than silently correcting invalid indentation.

## 13. Interoperability Architecture

The interoperability layer separates AssayFlux language semantics from external execution mechanisms.

### Main Components

#### Base Adapter

Defines the common interface expected from interoperability adapters.

#### Adapter Registry

Associates supported language identifiers with adapter implementations.

#### Adapter Loader

Loads or retrieves supported adapters.

#### Interoperability Runtime

Provides the interface through which the interpreter can request external execution.

#### Language Adapters

Implement language-specific execution and value conversion.

The existing Python adapter and interoperability infrastructure provide a foundation. They do not automatically mean that external code can be called from AssayFlux source programs.

## 14. Python Integration

Python is the first intended external integration target.

### Goals

- Import supported Python modules.
- Call supported functions.
- Pass compatible arguments.
- Return results to AssayFlux.
- Report Python exceptions.
- Manage execution timeouts.
- Document dependency requirements.

Potential scientific libraries include NumPy, SciPy, SymPy, pandas, and Matplotlib.

Their availability depends on the Python environment and the implementation of module integration.

### Execution Safety

If Python source is executed through a subprocess, that subprocess must not be treated as a security sandbox.

Untrusted Python code may access files, processes, networks, and other resources available to the executing account.

External execution must be treated as potentially unsafe.

## 15. Future Language Integrations

AssayFlux may eventually support selected capabilities from other languages.

| Language | Potential approach | Status |
|---|---|---|
| Python | Python adapter and module integration | Initial integration target |
| C | Native libraries and foreign-function interfaces | Planned |
| C++ | Native libraries and compatible interoperability mechanisms | Planned |
| Java | JVM-based integration | Planned |
| JavaScript | Embedded or external runtime | Planned |
| Rust | Native libraries and compatible interfaces | Planned |

Each integration requires its own design, dependencies, error handling, value conversions, and tests.

The architecture should avoid requiring a complete rewrite of the interpreter whenever a new adapter is introduced.

## 16. Error Handling

Errors may occur during source reading, lexing, parsing, interpretation, or external execution.

### Error Categories

- File-reading errors.
- Lexical errors.
- Syntax errors.
- Indentation errors.
- Undefined-name errors.
- Type errors.
- Function-call errors.
- Import errors.
- Runtime errors.
- Interoperability errors.
- External execution timeouts.

### Diagnostic Requirements

Where possible, errors should include:

- A useful description.
- The relevant source file.
- The line and column.
- The cause of the failure.
- Guidance for correction.

External errors should be translated into useful AssayFlux diagnostics without hiding important information.

## 17. Testing Architecture

Testing verifies that the language follows its specification.

### Unit Tests

Test individual components such as:

- Lexer tokenization.
- AST node behavior.
- Parser rules.
- Expression evaluation.
- Variable and constant handling.
- Function execution.
- Loop behavior.
- Indentation validation.

### Interoperability Tests

Test:

- Adapter registration.
- Adapter loading.
- Argument and return-value handling.
- External execution results.
- Error propagation.
- Timeout behavior.
- Missing dependencies.

### Integration Tests

Test complete AssayFlux programs that pass through the source reader, lexer, parser, AST, interpreter, and any required adapter.

### Continuous Integration

The GitHub Actions workflow should run the automated test suite when applicable changes are pushed or submitted.

A passing test suite verifies only the behavior covered by its tests. It does not prove that every planned feature is complete.

## 18. Command-Line Interface

The command-line interface is intended to provide a practical way to execute AssayFlux programs.

Potential capabilities include:

- Running a `.af` file.
- Reporting syntax errors.
- Displaying program output.
- Returning appropriate process exit codes.
- Providing help and usage information.

The CLI must use the actual implemented entry point defined by the project configuration.

## 19. Android IDE Architecture

A future Android IDE may include:

- A source editor.
- `.af` syntax highlighting.
- File management.
- Program execution.
- Console output.
- Error navigation.
- Project management.
- Documentation access.

The Android application should use a clearly defined interface to communicate with the AssayFlux execution engine.

The execution engine and IDE should remain separate components so that language development does not depend on the user interface.

## 20. Dependency Management

Dependencies should be declared and managed explicitly.

The project should distinguish between:

- Required runtime dependencies.
- Optional scientific libraries.
- Development and testing dependencies.
- Platform-specific dependencies.
- Dependencies required only by an external adapter.

Importing an optional library should produce a useful error when that library is unavailable.

The project should avoid silently installing packages during normal program execution.

## 21. Compatibility and Versioning

AssayFlux must document changes that affect syntax or runtime behavior.

Important compatibility areas include:

- Keyword changes.
- Operator changes.
- Indentation rules.
- Block termination.
- Function declaration and call syntax.
- Import semantics.
- Value conversion.
- Runtime error behavior.

Changes to the language specification should be reflected in the implementation, tests, examples, and documentation.

## 22. Development Priorities

Recommended implementation order:

1. Finalize the language grammar.
2. Align lexer behavior with the grammar.
3. Implement strict indentation validation.
4. Align the parser and AST with the finalized syntax.
5. Implement interpreter behavior for the supported language features.
6. Add and run comprehensive automated tests.
7. Connect Python imports to the interoperability runtime.
8. Add integration tests for imported modules.
9. Improve the command-line experience.
10. Investigate additional language adapters.
11. Develop the Android IDE.

The order may change when testing identifies a blocking dependency, but language semantics should remain consistent.

## 23. Architecture Principles

AssayFlux follows these design principles:

1. **Modularity:** Keep components focused on distinct responsibilities.
2. **Separation of concerns:** Separate parsing, interpretation, and external execution.
3. **Explicit behavior:** Define language semantics instead of relying on accidental implementation details.
4. **Testability:** Design components for automated testing.
5. **Extensibility:** Allow additional adapters without unnecessary changes to the core interpreter.
6. **Transparency:** Distinguish implemented features from planned features.
7. **Portability:** Document and test supported environments.
8. **Security awareness:** Treat external code execution as potentially unsafe.
9. **Maintainability:** Keep source code and documentation synchronized.
10. **Compatibility:** Make language changes deliberate and documented.

## 24. Current Status

AssayFlux is in early development.

The repository contains core language components and an interoperability foundation. The exact capabilities available to users depend on the current implementation and its tests.

This document describes the intended architecture. It must not be interpreted as proof that every component, language integration, or IDE feature is already complete.

For current implementation details, consult `docs/SPECIFICATION_STATUS.md`.

---

**End of AssayFlux Architecture**