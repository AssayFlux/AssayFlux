# AssayFlux CLI Platform

The AssayFlux CLI is intended to be the primary developer entry point for creating, checking, running, testing, packaging, and managing AssayFlux projects. This directory contains imported CLI automation and application-harness code being assessed for reuse behind that experience.

## Language-first contract

- Use the canonical AssayFlux lexer, parser, semantic checks, and runtime for .af source files.
- Do not create a second grammar or silently accept syntax the language core rejects.
- Keep application-specific command harnesses modular behind service/provider interfaces.
- Make permissions, side effects, errors, and output formats explicit.

## Current integration status

**Imported — integration not yet verified.** The presence of CLI harnesses does not mean that they already implement native AssayFlux commands or follow the final language grammar. Inventory each harness, dependencies, supported applications, and licenses before adapting it.

## Integration requirements

- Establish a stable command registry and plugin contract.
- Add consistent structured diagnostics and exit codes.
- Validate inputs and make potentially destructive actions explicit.
- Test command discovery, execution, failure handling, and packaging.
- Preserve required notices and compatibility references for third-party applications.

## Reference documentation

The imported CLI project's original documentation is preserved in [UPSTREAM_README.md](UPSTREAM_README.md). Its original package commands, badges, and external links may refer to the upstream project rather than the AssayFlux CLI.

See the repository-level [Branding and Attribution Policy](../../../docs/BRANDING_AND_ATTRIBUTION.md).
