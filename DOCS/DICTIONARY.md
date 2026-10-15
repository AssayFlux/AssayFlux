# AssayFlux Scientific Systems — Language Dictionary

**Language:** AssayFlux Scientific Systems  
**Short name:** AssayFlux  
**Version:** 0.2.0  
**File extension:** `.af`  
**Document status:** Language reference for early development

---

## 1. Purpose

This dictionary defines the terminology, keywords, operators, syntax conventions, and core concepts of AssayFlux.

AssayFlux is a custom programming language designed for scientific computing, general-purpose programming, and interoperability with existing programming languages and libraries.

Its initial implementation is based on Python, with the long-term goal of integrating selected capabilities from Python, C, C++, Java, JavaScript, and Rust.

**Important:** A documented feature is not necessarily implemented. Actual support must be verified against the interpreter and automated tests.

---

## 2. Basic Language Terms

| Term | Meaning |
|---|---|
| AssayFlux | Short name of the programming language. |
| AssayFlux Scientific Systems | Full language name. |
| `.af` | File extension for AssayFlux source files. |
| Source code | Instructions written in AssayFlux. |
| Lexer | Converts source text into tokens. |
| Token | A meaningful unit recognized by the lexer. |
| Parser | Processes tokens according to the language grammar. |
| Abstract Syntax Tree (AST) | Structured representation of a program. |
| Interpreter | Executes a parsed AssayFlux program. |
| Runtime | The environment in which a program executes. |
| Expression | Code that produces a value. |
| Statement | An instruction that performs an action. |
| Identifier | A name used for a variable, constant, function, or module. |
| Literal | A value written directly in source code. |
| Scope | The region in which a name can be accessed. |
| Module | A reusable unit of code or library. |
| Interoperability | Communication between AssayFlux and another language or runtime. |
| Adapter | A component that connects AssayFlux to an external runtime or implementation. |

---

## 3. Variables

A variable is a named storage location whose value can be assigned or changed.

### Syntax

```assayflux
name = expression
```

### Example

```assayflux
name = "AssayFlux"
version = 0.1
count = 10

show name
show version
show count
```

### Rules

