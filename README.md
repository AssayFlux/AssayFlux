# AssayFlux

**One language. One coherent ecosystem. Many specialized capabilities.**

AssayFlux is being developed as a language-centered programming ecosystem. Its canonical language uses .af source files, a consistent grammar, and a shared execution model. CLI tooling, assistants, security tools, platform integrations, quantum providers, and distributed services are intended to build on that foundation—not introduce competing languages or disconnected runtimes.

> **Repository status:** this repository currently contains imported project codebases at different stages of reconciliation. Their presence does not mean they are already integrated with the AssayFlux language core or production-ready.

## Architecture direction

- **Language core:** lexer, parser, AST, semantics, types, module resolution, diagnostics.
- **Runtime:** canonical interpreter and execution interfaces.
- **Developer workflow:** CLI, project validation, testing, packaging, and assistant tooling.
- **Capability services:** operating-system adapters, security analysis, reverse engineering, and quantum providers.
- **Trust and infrastructure:** sandboxing, cryptography, observability, and optional Kubernetes orchestration.

## Language principles

AssayFlux follows the project conventions defined for the language: .af files, plain NAME = expr, project declarations, null, and the specified N-times repetition syntax. These conventions must be implemented and tested by the canonical language pipeline rather than simulated independently by each service.

## Repository layout

The current src/ tree contains eleven imported project codebases. The next integration work is to inventory them, preserve their useful functionality and required notices, define service contracts, and connect capabilities to the language core in reviewable stages.

## Integration status

| Area | Status |
|---|---|
| Imported project inventory | In progress |
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

AssayFlux is the umbrella project identity. Imported components may retain upstream-specific identifiers where required by licensing, dependencies, APIs, build systems, or accurate provenance. See [Branding and Attribution Policy](docs/BRANDING_AND_ATTRIBUTION.md).

## License

The repository's root license applies to material it covers. Imported components may have separate licenses and notices; review the applicable license files before redistributing or modifying each component.
