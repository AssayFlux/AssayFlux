# AssayFlux Interpreter and Sandbox Infrastructure

This module is the AssayFlux-facing entry point for interpreter-related and isolated-execution infrastructure.

## Core distinction

The canonical AssayFlux language interpreter belongs to the Language Core project. This imported codebase may provide sandbox or code-interpreter infrastructure, but it must not create a competing .af grammar or silently replace canonical runtime semantics.

## Current status

**Imported sandbox infrastructure — integration and isolation guarantees not yet verified.** The source is located in [code-interpreter-main](code-interpreter-main/README.md), with upstream reference material preserved in [UPSTREAM_README.md](code-interpreter-main/UPSTREAM_README.md).

## Phase 1 requirements

- Trace the current canonical interpreter implementation and identify any duplicate or competing runtime.
- Inventory local and remote execution paths, SDKs, secrets, storage, and provider dependencies.
- Verify CPU, memory, time, filesystem, process, and network boundaries.
- Preserve upstream license and provenance information.
- Require adapter and isolation tests before claiming that this module securely executes .af programs.

AssayFlux branding identifies the integration target; it does not establish that the imported code is the canonical interpreter.
