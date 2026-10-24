# AssayFlux Reverse-Engineering Provider

This directory contains the AssayFlux-facing entry point for the imported reverse-engineering framework.

## Intended role

Expose useful binary, application, and runtime-analysis capabilities through modular provider interfaces with structured findings, explicit permissions, and clear input/output boundaries. The canonical AssayFlux language pipeline remains responsible for .af syntax and semantics.

## Current status

**Imported provider — native AssayFlux integration not verified.** The source tree retains upstream-specific commands, dependencies, APIs, and documentation. Its presence does not mean all tools are installed, functional, or connected to the AssayFlux runtime.

## Integration requirements

- Inventory supported inputs, runtime dependencies, external services, and licenses.
- Define stable APIs and structured result formats.
- Apply authorization, safe file handling, resource limits, and cancellation.
- Preserve upstream licenses, notices, API identifiers, and provenance.
- Add provider and integration tests before claiming native AssayFlux support.

Read [UPSTREAM_README.md](UPSTREAM_README.md) for the original project documentation. See the [AssayFlux Reverse Engineering module](../README.md) and [Branding and Attribution Policy](../../../docs/BRANDING_AND_ATTRIBUTION.md).

This README identifies the maintained AssayFlux integration boundary; it does not claim authorship of the imported framework.
