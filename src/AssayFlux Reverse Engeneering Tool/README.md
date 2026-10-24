# AssayFlux Reverse Engineering Services

This directory contains imported reverse-engineering capabilities being evaluated for integration as modular AssayFlux analysis services.

## Intended role

Analysis tools should be accessible through documented provider interfaces with structured findings, explicit permissions, and clear input/output boundaries. The canonical AssayFlux language pipeline remains separate from binary and application analysis engines.

## Current status

**Imported analysis tools — AssayFlux integration not verified.** The presence of the source does not imply that all tools are installed, functional, or connected to the AssayFlux runtime.

## Integration requirements

- Inventory supported inputs, dependencies, external services, and licenses.
- Define stable APIs and structured result formats.
- Apply authorization, safe file handling, and resource limits.
- Test malformed inputs, failures, and cancellation.
- Preserve upstream documentation, attribution, and notices.

The imported source tree is located in [rea-main](rea-main/).
