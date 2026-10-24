# AssayFlux Language Core

This directory is the entry point for the canonical AssayFlux language implementation. The implementation and grammar reference are located in [AssayFlux-AssayFlux](AssayFlux-AssayFlux/README.md).

## Core authority

The language core owns the canonical .af grammar, parsing, AST, semantic checks, runtime semantics, diagnostics, and public language APIs. Other services must use these interfaces rather than invent parallel syntax or execution rules.

## Integration priorities

- Preserve lexer/parser behavior and the documented language conventions.
- Keep grammar, examples, and tests synchronized.
- Version public APIs before external services depend on them.
- Test every language change against the CLI and runtime.
- Keep sandbox guarantees distinct from language-level validation.

The core is experimental; it is not an OS-enforced security boundary. See the nested README and SECURITY.md for the implementation's current scope.
