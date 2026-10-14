# AssayFlux Scientific Systems

**AssayFlux** is an experimental programming language project designed to provide a unified programming experience with an emphasis on scientific computing and multi-language interoperability.

**Version:** 0.1.0  
**Status:** Early Development  
**Repository:** AssayFlux

---

## Project Vision

The goal of AssayFlux is to develop a programming language that allows developers to write programs using AssayFlux syntax and eventually access functionality implemented in other programming languages.

The project will begin with a Python-based interpreter. Additional language integrations will be explored incrementally.

AssayFlux aims to provide:

- A custom programming language and grammar.
- A modular interpreter architecture.
- Scientific computing capabilities.
- A standard library.
- Multi-language interoperability.
- Clear error messages and debugging support.
- Potential future development tools for Android.

These are project goals, not claims of existing functionality.

---

## Language Preview

The following examples illustrate the proposed AssayFlux syntax.

### Hello World

```assayflux
show `Hello, World!`
```

### Variables and Calculations

```assayflux
a = 10
b = 20

result = a + b

show result
```

### Conditional Statements

```assayflux
temperature = 30

if temperature > 35
    show `Very hot`
otherwise temperature > 20
    show `Moderate temperature`
else
    show `Cold`
end
```

### Function Declaration

```assayflux
f.add(a, b)
    return a + b
end
```

These examples describe intended syntax. They are not guaranteed to execute until the interpreter is implemented and tested.

---

## Multi-Language Integration

AssayFlux is intended to explore interoperability with languages such as:

- Python
- C
- C++
- Java
- JavaScript
- Rust

Integration methods will depend on each language's runtime, available libraries, platform compatibility, and data types.

The project will introduce integrations gradually rather than claiming universal compatibility from the beginning.

---

## Project Structure

The repository is being organized as follows:

```text
AssayFlux/
├── assayflux/
├── docs/
│   ├── LANGUAGE_SPECIFICATION.md
│   ├── GRAMMAR.md
│   ├── EXAMPLES.md
│   └── ARCHITECTURE.md
├── pyproject.toml
└── README.md
```

Additional source files, tests, modules, and development tools will be added as implementation progresses.

---

## Development Roadmap

### Phase 1: Language Design

- Define language syntax and grammar.
- Specify variables, expressions, and data types.
- Define conditional and repetition statements.
- Specify functions and return values.
- Document language architecture.

### Phase 2: Core Interpreter

- Implement lexical analysis.
- Implement parsing.
- Build the Abstract Syntax Tree.
- Implement expression evaluation.
- Implement statements and functions.
- Add meaningful error reporting.

### Phase 3: Standard Library

- Mathematical operations.
- String utilities.
- Collection utilities.
- Scientific computing utilities.

### Phase 4: Multi-Language Interoperability

- Establish an interoperability interface.
- Integrate selected Python functionality.
- Investigate native library integration.
- Evaluate bridges for additional languages.
- Add integration tests.

### Phase 5: Developer Tools

- Command-line execution.
- Source file execution.
- Improved diagnostics.
- Debugging support.

### Phase 6: Android Development Environment

- Evaluate a suitable Android architecture.
- Integrate the AssayFlux runtime.
- Develop an editor and execution interface.
- Test on supported Android devices.

---

## Current Status

AssayFlux is in its initial design stage.

The repository currently focuses on establishing the project structure, language specification, grammar, examples, and architecture.

The interpreter, compiler, standard library, multi-language integrations, and Android development environment must be implemented and tested before they can be considered available features.

---

## Contributing

Contributions and design discussions may help improve the language.

Before proposing significant syntax changes, consult the language specification and grammar documentation.

As the project develops, contribution guidelines and testing instructions will be added.

---

## License

A license has not yet been selected.

Until a license is added, do not assume that the project is available for unrestricted copying, modification, or redistribution.