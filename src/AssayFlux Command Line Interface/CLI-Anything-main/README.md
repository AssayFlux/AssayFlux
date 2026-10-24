# AssayFlux CLI Platform

The AssayFlux CLI is intended to be the primary developer entry point for creating, checking, running, testing, packaging, and managing AssayFlux projects. This directory contains imported CLI automation and application-harness code being assessed for reuse behind that experience.

## Language-first contract

- Use the canonical AssayFlux lexer, parser, semantic checks, and runtime for .af source files.
- Do not create a second grammar or silently accept syntax the language core rejects.
- Keep application-specific command harnesses modular behind service/provider interfaces.
- Make permissions, side effects, errors, and output formats explicit.

## Current integration status

**Initial host-side integration added; application compatibility is not yet verified.** The AssayFlux language-core CLI now discovers installed `cli-anything-*` and `cli-hub` executables with `assayflux tools list`, and can invoke a discovered harness with `assayflux tools run ... --allow-external-tools -- ...`. The adapter does not auto-install packages and never uses a shell. The harnesses remain external programs, not native `.af` syntax. Inventory each harness's dependencies, supported applications, side effects, and licenses before use.

## Integration requirements

- Expand the adapter into a versioned provider/command registry with per-harness metadata and capability declarations.
- Add consistent structured diagnostics and exit codes.
- Validate inputs and make potentially destructive actions explicit.
- Run the language-core test suite and validate representative harnesses in an environment with their target applications installed.
- Preserve required notices and compatibility references for third-party applications.

## Reference documentation

The imported CLI project's original documentation is preserved in [UPSTREAM_README.md](UPSTREAM_README.md). Its original package commands, badges, and external links may refer to the upstream project rather than the AssayFlux CLI.

See the repository-level [Branding and Attribution Policy](../../../docs/BRANDING_AND_ATTRIBUTION.md).
