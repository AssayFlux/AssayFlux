# AssayFlux CLI Services

This module is the AssayFlux-facing entry point for command-line automation and application harnesses.

## Language-first integration

The supported AssayFlux CLI should use the canonical language core for .af parsing, semantic checks, and execution. Application-specific commands must remain modular providers and must not introduce a competing language grammar.

## Current status

**Imported CLI capabilities — native AssayFlux command integration not yet verified.** The imported source is located in [CLI-Anything-main](CLI-Anything-main/README.md), with upstream reference material preserved in [UPSTREAM_README.md](CLI-Anything-main/UPSTREAM_README.md).

## Phase 1 requirements

- Inventory command harnesses, application dependencies, package metadata, and licenses.
- Establish a stable command registry, structured output, consistent exit codes, and permission declarations.
- Review command side effects and make destructive actions explicit.
- Preserve upstream attribution and compatibility references.
- Test command discovery, execution, failures, and packaging before advertising commands as supported.

AssayFlux branding identifies the integration target; it does not imply all imported harnesses already run through the AssayFlux CLI.
