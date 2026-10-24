# AssayFlux Execution Services

This module is the AssayFlux-facing entry point for execution-provider infrastructure.

## Language-first integration

The canonical AssayFlux pipeline must parse and validate .af source before execution. External-language runtimes may be supported as separate providers, but they do not replace the canonical interpreter or define AssayFlux semantics.

## Current status

**Imported execution engine — integration and isolation guarantees not yet verified.** The imported source is located in [piston-master](piston-master/readme.md), with upstream reference material preserved in [UPSTREAM_README.md](piston-master/UPSTREAM_README.md).

## Phase 1 requirements

- Inventory supported runtimes, dependencies, worker lifecycle, and deployment configuration.
- Define a versioned execution-provider interface and structured diagnostics.
- Audit CPU, memory, time, process, filesystem, and network controls before running untrusted workloads.
- Preserve upstream licenses, notices, compatibility identifiers, and provenance.
- Add integration and failure-path tests before claiming native support.

An AssayFlux-facing README does not imply that the imported engine is connected to the .af runtime or safe for arbitrary untrusted code.
