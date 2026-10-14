# AssayFlux System Architecture

**Project:** AssayFlux Scientific Systems
**Language:** AssayFlux
**Version:** 0.1.0
**Status:** Initial Architecture Proposal

---

## 1. Project Vision

AssayFlux is a programming language project designed to provide a unified environment for scientific computing and multi-language integration.

The goal is to let developers write programs using AssayFlux syntax while accessing capabilities implemented in other programming languages.

AssayFlux will initially be developed as a Python-based language implementation.

The architecture should allow additional runtimes and language integrations to be introduced progressively.

---

## 2. Core Architecture

The initial architecture consists of these components:

1. Source Code
2. Lexer
3. Parser
4. Abstract Syntax Tree
5. Semantic Analyzer
6. Runtime and Interpreter
7. Standard Library
8. Foreign Language Integration
9. Error Reporting
10. Development Tools

Each component has a separate responsibility.

---

## 3. Source Code

Source code contains programs written in the AssayFlux language.

Example:

    x = 10
    y = 20
    result = x + y
    show result

The source code will eventually be stored in files using the `.afx` extension.

Example filename:

    main.afx

The `.afx` extension is the proposed default extension for AssayFlux programs.

---

## 4. Lexer

The lexer converts source text into a sequence of tokens.

It identifies elements such as:

- Keywords
- Identifiers
- Numbers
- Strings
- Operators
- Parentheses
- Commas
- Newlines

Example source:

    show `Hello`

Conceptual tokens:

    KEYWORD_SHOW
    STRING_LITERAL

The lexer should report invalid characters and include source location information in its errors.

---

## 5. Parser

The parser receives tokens from the lexer and checks whether they follow the AssayFlux grammar.

It constructs a structured representation of the program.

The parser must support the finalized syntax for:

- Variable assignments
- Expressions
- Conditional statements
- Repetition statements
- Functions
- Return statements
- Output statements
- Import statements

The parser must not silently accept invalid syntax.

---

## 6. Abstract Syntax Tree

The Abstract Syntax Tree, or AST, represents the structure of a parsed program.

The initial implementation may include these node types:

- ProgramNode
- AssignmentNode
- NumberNode
- StringNode
- BooleanNode
- IdentifierNode
- BinaryOperationNode
- UnaryOperationNode
- ShowNode
- IfNode
- RepeatNode
- StopNode
- SkipNode
- FunctionDefinitionNode
- FunctionCallNode
- ReturnNode
- ImportNode

The exact node structure will be determined during implementation.

The AST should remain independent of the source formatting wherever possible.

---

## 7. Semantic Analyzer

The semantic analyzer checks whether a syntactically valid program makes sense.

Its responsibilities may include:

- Detecting undefined variables
- Detecting duplicate declarations where prohibited
- Checking function calls
- Checking function arguments
- Checking return statements
- Validating import declarations
- Reporting invalid operations
- Checking language interoperability declarations

Some checks may occur at runtime rather than during semantic analysis.

The implementation must document which checks happen at each stage.

---

## 8. Runtime and Interpreter

The initial AssayFlux implementation will use an interpreter written in Python.

The interpreter will execute the AST.

Its responsibilities include:

- Managing variable environments
- Evaluating expressions
- Executing conditional statements
- Executing repetition statements
- Calling functions
- Handling return values
- Processing output statements
- Managing runtime errors

The interpreter is the first execution engine planned for AssayFlux.

A separate compiler may be considered in a later development phase.

---

## 9. Runtime Control Flow

AssayFlux will provide structured control flow.

### Conditional Statements

Planned keywords:

- if
- otherwise
- else
- end

The `if` branch is evaluated first.

Each `otherwise` branch introduces an additional condition.

The `else` branch provides an unconditional fallback.

Only the first matching branch executes.

### Repetition Statements

Planned keywords:

- repeat
- stop
- skip
- end

The exact repetition syntax and execution behavior must be finalized before implementation.

`stop` is intended to exit the nearest enclosing loop.

`skip` is intended to move to the next iteration of the nearest enclosing loop.

---

## 10. Function System

AssayFlux will use the `f.` prefix for function declarations.

Proposed declaration:

    f.add(a, b)
        return a + b
    end

Functions should support:

- Named parameters
- Local variables
- Function calls
- Return values
- Runtime argument validation
- Clear error messages

The final grammar must explicitly define how function declarations differ from function calls.

The language specification must also determine how recursion and variable scope work.

---

## 11. Standard Library

The AssayFlux standard library will provide reusable functionality.

Proposed modules include:

- assayflux.math
- assayflux.strings
- assayflux.collections
- assayflux.files
- assayflux.science
- assayflux.statistics
- assayflux.units
- assayflux.errors

The standard library should initially use Python where appropriate.

Modules should have stable interfaces so that their internal implementations can change without unnecessarily breaking AssayFlux programs.

These modules are planned components, not existing implementations.

---

## 12. Multi-Language Integration Strategy

Multi-language integration is a central design goal.

AssayFlux should provide a common interface for accessing functions and capabilities implemented in other languages.

Integration will be introduced in stages.

### Stage 1: Python Integration

Python will be the initial implementation language for the interpreter.

The first integration milestone is to expose selected Python functionality through a controlled AssayFlux interface.

### Stage 2: Native Libraries

AssayFlux should eventually be able to call compatible native libraries through an appropriate interoperability layer.

Possible technologies include Python's Foreign Function Interface facilities and native extension modules.

The selected approach must account for platform compatibility, memory safety, and dependency management.

### Stage 3: C and C++

C and C++ integration may use native extension modules, compatible shared libraries, or foreign-function interfaces.

The implementation must document calling conventions, data types, memory ownership, and error propagation.

### Stage 4: Java

Java integration may use a bridge or a separate runtime integration layer.

The design must account for the Java Virtual Machine and the availability of compatible runtime components.

### Stage 5: JavaScript

JavaScript integration may use an embedded runtime or a separate execution process.

The selected approach must define how values, function calls, errors, and asynchronous operations are exchanged.

### Stage 6: Rust

Rust integration may use native libraries or extension modules with clearly defined interfaces.

The implementation must define how Rust values and errors cross the language boundary.

These integrations are development goals. No integration should be described as implemented until it has been built and tested.

---

## 13. Foreign Function Interface

A future Foreign Function Interface, or FFI, should provide a consistent way to call supported external functions.

Its responsibilities may include:

- Loading approved external libraries
- Resolving function names
- Mapping data types
- Passing arguments
- Receiving return values
- Propagating errors
- Managing resource ownership
- Reporting compatibility problems

The interface should avoid exposing unnecessary implementation details to AssayFlux programs.

The first version should support a small, explicitly documented set of types.

---

## 14. Type Interoperability

The interoperability layer will need rules for translating values between languages.

Initial conceptual mappings include:

- AssayFlux integer to a compatible integer type
- AssayFlux floating-point value to a compatible floating-point type
- AssayFlux boolean to a compatible boolean type
- AssayFlux string to a compatible string representation
- AssayFlux collection to a supported collection representation

Actual mappings must be specified separately for each integration.

The system must reject incompatible conversions or report them clearly.

It must not assume that identically named types have identical representations in different languages.

---

## 15. Import System

AssayFlux will eventually support importing modules and external capabilities.

The import system must define:

- Module naming rules
- Module search paths
- Import resolution
- Duplicate import behavior
- Circular import handling
- External library declarations
- Import error reporting

External libraries must not be loaded automatically without a defined and documented loading policy.

---

## 16. Error Reporting

Errors should be understandable and actionable.

The error system should distinguish between:

- Lexical errors
- Syntax errors
- Semantic errors
- Runtime errors
- Import errors
- Foreign-function errors
- Compatibility errors

Where possible, an error should include:

- Error category
- Source filename
- Line number
- Column number
- Explanation
- Suggested correction

Errors originating in another language should preserve useful diagnostic information from the original source whenever possible.

---

## 17. Security and Reliability

Language interoperability introduces risks.

The architecture should consider:

- Untrusted source code
- External library loading
- File system access
- Process execution
- Native memory errors
- Dependency security
- Resource exhaustion
- Platform compatibility

Calling native code can compromise process safety.

The initial implementation should document which capabilities are available and which operations require additional controls.

The interpreter must not be described as a secure sandbox unless appropriate isolation has been implemented and tested.

---

## 18. Platform Strategy

The initial language implementation will use Python.

The repository should aim to keep the core language implementation separate from platform-specific user interfaces.

This separation will make it easier to develop command-line tools first and consider an Android development environment later.

Android support will require separate decisions about Python availability, packaging, native dependencies, and runtime compatibility.

A future Android IDE must not be treated as a prerequisite for implementing the core language.

---

## 19. Testing Architecture

Each major component should have its own tests.

Planned test groups include:

- Lexer tests
- Parser tests
- AST tests
- Semantic analysis tests
- Interpreter tests
- Function tests
- Standard library tests
- Import system tests
- Interoperability tests
- Error reporting tests

Integration tests should verify that components work together.

Tests for external language integrations must run only when their required runtimes and dependencies are available.

---

## 20. Development Phases

### Phase 1: Specification

- Finalize lexical rules
- Finalize grammar
- Define expression precedence
- Define variable behavior
- Define function behavior
- Define loop behavior
- Define module behavior

### Phase 2: Core Interpreter

- Implement the lexer
- Implement the parser
- Build the AST
- Implement the interpreter
- Implement basic error reporting

### Phase 3: Language Features

- Implement variables
- Implement expressions
- Implement conditions
- Implement repetition
- Implement functions
- Implement imports

### Phase 4: Standard Library

- Add mathematical functions
- Add string utilities
- Add collection utilities
- Add scientific utilities

### Phase 5: Multi-Language Integration

- Establish the interoperability interface
- Add controlled Python integration
- Investigate native library integration
- Evaluate additional language bridges
- Add integration tests

### Phase 6: Developer Tools

- Add a command-line interface
- Add source file execution
- Improve diagnostic messages
- Add debugging capabilities

### Phase 7: Android Development Environment

- Evaluate a suitable Android architecture
- Integrate the interpreter
- Build an editor interface
- Add execution controls
- Test on supported Android devices

---

## 21. Architecture Principles

AssayFlux development should follow these principles:

1. Keep the language specification authoritative.
2. Separate parsing from execution.
3. Keep components modular.
4. Test every major feature.
5. Document language interoperability explicitly.
6. Avoid claiming support for unimplemented features.
7. Prefer clear errors over silent failures.
8. Keep platform-specific code separate from the core language.
9. Introduce integrations incrementally.
10. Preserve compatibility where practical.

---

## 22. Current Status

Version 0.1.0 defines the initial architectural direction.

This document describes planned components and development goals.

It does not mean that the lexer, parser, interpreter, standard library, foreign-function interface, compiler, or Android IDE has already been implemented.

Implementation status should be updated as each component is developed and tested.

---

## 23. Future Architecture Changes

Architecture decisions may change as the project develops.

Significant changes should be documented with their reasons and consequences.

The architecture must evolve alongside the language specification and the results of implementation testing.