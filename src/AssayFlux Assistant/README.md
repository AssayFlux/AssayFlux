# AssayFlux Assistant Services

This module is the AssayFlux-facing entry point for assistant, knowledge-retrieval, and service-automation capabilities.

## Language-first integration

- Use the canonical AssayFlux language core for parsing, validation, and .af semantics.
- Expose assistant workflows through explicit, versioned service interfaces.
- Keep credentials, network access, data storage, and execution permissions behind policy-controlled adapters.
- Validate generated .af programs with the actual AssayFlux toolchain before execution.

## Current status

**Imported capability — native AssayFlux integration not yet verified.** The underlying source is located in [project-nomad-main](project-nomad-main/README.md). Its original documentation is preserved as [UPSTREAM_README.md](project-nomad-main/UPSTREAM_README.md).

## Phase 1 requirements

- Inventory dependencies, external services, configuration, network access, and data storage.
- Audit branding in UI surfaces, deployment files, package metadata, URLs, workflows, and environment variables.
- Preserve upstream licenses, notices, and provenance.
- Define a least-privilege adapter and integration tests before calling this service integrated.

AssayFlux branding here identifies the maintained integration boundary; it does not claim authorship of the imported implementation.
