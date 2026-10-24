# AssayFlux

**One language. One coherent ecosystem. Many specialized capabilities.**

AssayFlux is a language-centered programming ecosystem. Its canonical language uses `.af` source files, a consistent grammar, and a shared execution model. CLI tooling, assistants, security tools, platform integrations, quantum providers, and distributed services are intended to build on that foundation—not introduce competing languages or disconnected runtimes.

> **Repository status:** this repository contains eleven imported project codebases at different stages of reconciliation. Their presence does not mean they are already integrated with the AssayFlux language core or production-ready.

## Architecture direction

- **Language core:** lexer, parser, AST, semantics, types, module resolution, diagnostics.
- **Runtime:** canonical interpreter and execution interfaces.
- **Developer workflow:** CLI, project validation, testing, packaging, and assistant tooling.
- **Capability services:** operating-system adapters, security analysis, reverse engineering, and quantum providers.
- **Trust and infrastructure:** sandboxing, cryptography, observability, and optional Kubernetes orchestration.

## Language principles

AssayFlux follows the project conventions defined for the language: `.af` files, `plain NAME = expr`, `project` declarations, `null`, and the specified N-times repetition syntax. These conventions must be implemented and tested by the canonical language pipeline rather than simulated independently by each service.

## Repository layout

The `src/` tree contains eleven imported project codebases. Their outer AssayFlux directories provide integration entry points; nested upstream code remains isolated until dependencies, licensing, build requirements, and service contracts are reconciled.

### AssayFlux service and platform entry points

- [AssayFlux Assistant](src/AssayFlux%20Assistant/README.md)
- [AssayFlux Code Execution Engine](src/AssayFlux%20Code%20Execution%20Engine/README.md)
- [AssayFlux Command Line Interface](src/AssayFlux%20Command%20Line%20Interface/README.md)
- [AssayFlux Ethical Hacking Tools](src/AssayFlux%20Ethical%20Hacking%20Tools/README.md)
- [AssayFlux Interpreter and Sandbox Infrastructure](src/AssayFlux%20Interpreter/README.md)
- [AssayFlux Language Core](src/AssayFlux%20Language%20Core/README.md)
- [AssayFlux Linux Platform Integration](src/AssayFlux%20LinuxOS/README.md)
- [AssayFlux macOS Platform Integration](src/AssayFlux%20MacOS/README.md)
- [AssayFlux Quantum Computing Services](src/AssayFlux%20Quantum%20Computing/README.md)
- [AssayFlux Reverse Engineering Services](src/AssayFlux%20Reverse%20Engeneering%20Tool/README.md)
- [AssayFlux Windows Platform Integration](src/AssayFlux%20WindowsOS/README.md)

These are branded integration entry points, not a claim that every imported implementation is already integrated or verified.

## Phase 1: repository intelligence

The initial audit confirmed all eleven top-level service/platform directories and found that the imported repository is exceptionally large. GitHub reports that the merge of PR #1 introduced 135,902 changed files and 59,950,683 added lines. The recursive tree response is truncated, so this is not yet a complete file-by-file audit.

See the [Phase 1 Repository Audit](docs/REPOSITORY_AUDIT.md) for findings and limitations, and the [per-module tree inventory](docs/PHASE1_TREE_INVENTORY.md) for the latest structural snapshot.

## Integration status

| Area | Status |
|---|---|
| Top-level project inventory | Identified |
| Complete file-level inventory | In progress; recursive tree is truncated |
| Canonical language and service contracts | To be verified |
| CLI-to-runtime workflow | To be verified |
| Sandboxing and cryptographic controls | To be verified |
| Service-by-service integration | In progress |
| Kubernetes deployment | Planned where needed |

Status labels describe the integration effort, not the maturity of every imported upstream component. No completion percentages are published until backed by code inspection and automated tests.

## Development principles

1. **Language first:** one grammar and one semantic authority.
2. **Modular by contract:** services integrate through stable interfaces.
3. **Preserve before replacing:** inspect dependencies and test equivalence before removing code.
4. **Secure by design:** permissions and isolation must be enforced at real security boundaries.
5. **Evidence over claims:** document capabilities only when implementation and tests support them.
6. **Respect provenance:** retain applicable third-party licenses, notices, and attribution.

## Branding and third-party notices

AssayFlux is the umbrella project identity. Maintained entry points and integration documentation should use AssayFlux branding. Imported components may retain upstream-specific identifiers where required by licensing, dependencies, APIs, build systems, compatibility, or truthful provenance. See [Branding and Attribution Policy](docs/BRANDING_AND_ATTRIBUTION.md).

## License

The repository's root license applies to material it covers. Imported components may have separate licenses and notices; review the applicable license files before redistributing or modifying each component.
