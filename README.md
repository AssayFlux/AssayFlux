# AssayFlux Scientific Systems

**Language name:** AssayFlux Scientific Systems  
**Short name:** AssayFlux  
**Version:** 0.1.0  
**Source extension:** `.af`  
**Project status:** Early development

AssayFlux is an experimental programming language designed to provide a consistent programming interface for scientific computing and multi-language interoperability.

The initial implementation uses Python. Future development aims to integrate selected capabilities from Python, C, C++, Java, JavaScript, and Rust.

These are development goals. A language integration is not considered supported until it has been implemented and tested.

## Project Goals

- Develop a custom programming language with its own syntax.
- Build a lexer, parser, abstract syntax tree, and interpreter.
- Reuse existing Python scientific libraries where appropriate.
- Develop a modular interoperability system.
- Provide clear syntax and runtime errors.
- Build a command-line development experience.
- Eventually develop an Android IDE.

## Language Preview

The following examples illustrate the intended AssayFlux syntax. Some features may not yet work in the current interpreter.

### Hello World

```assayflux
show "Hello, World!"
```

### Variables and Calculations

```assayflux
a = 10
b = 20

result = a + b

show result
```

### Constants

```assayflux
const PI = 3.14159

show PI
```

### Conditions

```assayflux
temperature = 30

if temperature > 35
    show "Very hot"
otherwise temperature > 20
    show "Moderate temperature"
else
    show "Cold"
end
```

### Functions

Function declarations use the `f.` prefix. Function calls do not use that prefix.

```assayflux
f.add(a, b)
    return a + b
end

result = add(10, 20)
show result
```

### Repetition

```assayflux
count = 0

repeat count < 5
    show count
    count = count + 1
end
```

### Python Library Integration — Planned Syntax

The following illustrates the intended direction for Python module integration. It does not guarantee that imports currently work.

```assayflux
import math

result = math.sqrt(25)
show result
```

## Language Rules

AssayFlux follows these intended syntax rules:

- Strings use single or double quotes.
- Comments begin with `#`.
- Output statements use `show`.
- Function declarations use `f.name(parameters)`.
- Function calls use `name(arguments)`.
- Conditions use `if`, `otherwise`, `else`, and `end`.
- Repetition uses `repeat` and `end`.
- `stop` exits the nearest enclosing loop.
- `skip` skips to the next iteration of the nearest enclosing loop.
- Boolean literals are `true` and `false`.
- Logical operators are `and`, `or`, and `not`.
- The not-equal operator is `!=`; `nt=` is invalid.
- Indentation uses four spaces per level.
- Tabs are prohibited for indentation.
- Indentation and matching `end` statements are both mandatory.

Consult the language specification and grammar for the detailed rules.

## Multi-Language Interoperability

AssayFlux aims to provide a consistent interface for supported external functions and libraries.

### Planned Integration Stages

1. **Python:** Import selected modules, call functions, and exchange values.
2. **C and C++:** Investigate native libraries and foreign-function interfaces.
3. **Java:** Investigate integration with the Java Virtual Machine.
4. **JavaScript:** Investigate embedded or separate JavaScript runtimes.
5. **Rust:** Investigate compatible native libraries and extension modules.

Each integration will require explicit rules for values, function calls, errors, dependencies, and platform compatibility.

The initial Python adapter and interoperability infrastructure do not mean that all these languages are already callable from `.af` programs.

## Repository Structure

The repository contains the AssayFlux interpreter, tests, examples, documentation, and interoperability components.

Important directories:

- `assayflux/` — language implementation.
- `assayflux/interop/` — interoperability infrastructure.
- `tests/` — automated tests.
- `examples/` — example AssayFlux programs.
- `docs/` — language specifications and project documentation.

## Development Roadmap

### Phase 1: Language Design and Core Interpreter

- Finalize the language specification and grammar.
- Align the lexer, parser, AST, and interpreter.
- Enforce strict indentation and explicit block endings.
- Implement and test language features.
- Improve error messages and diagnostics.

### Phase 2: Standard Library

- Mathematical utilities.
- String and collection utilities.
- Scientific computing utilities.
- File handling and module support.

### Phase 3: Interoperability

- Connect the Python adapter to AssayFlux programs.
- Define supported value conversions.
- Add integration tests.
- Investigate C, C++, Java, JavaScript, and Rust integration.

### Phase 4: Developer Tools

- Improve command-line execution.
- Add syntax checking.
- Improve diagnostics and debugging.
- Document installation and usage.

### Phase 5: Android IDE

- Design the editor and file manager.
- Add `.af` syntax highlighting.
- Integrate program execution and console output.
- Test on supported Android devices.

## Current Status

AssayFlux is in early development.

The repository includes language implementation components and an interoperability foundation. Individual features must be verified against automated tests before being described as working.

The final language specification defines the intended behavior. Documentation examples may describe planned features that are not yet implemented.

## Documentation

Read these documents in the `docs/` directory:

- `LANGUAGE_SPECIFICATION.md` — language design and rules.
- `GRAMMAR.md` — syntax and grammar.
- `EXAMPLES.md` — example programs.
- `ARCHITECTURE.md` — system architecture.
- `ROADMAP.md` — development plan.
- `DICTIONARY.md` — language terminology.
- `SPECIFICATION_STATUS.md` — feature status and implementation notes.

## Contributing

Before proposing a syntax change, consult the language specification and grammar.

Significant changes should include appropriate tests and documentation.

## License

A license has not yet been selected. Until a license is added, do not assume the repository is available for unrestricted copying, modification, or redistribution .