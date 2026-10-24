# AssayFlux Quantum Computing Services

This directory contains an imported quantum software framework being evaluated as a provider for AssayFlux quantum-computing capabilities.

## Intended role

AssayFlux should expose a stable quantum provider interface for circuit construction, simulation, execution, and result normalization. The language core remains responsible for .af syntax and semantics; quantum functionality belongs behind a service API.

## Current status

**Adapter implemented; live dependency validation pending.** The AssayFlux language core now exposes `assayflux.quantum.list_devices()` and `assayflux.quantum.run_circuit()` plus `assayflux quantum` CLI commands. The first adapter supports only PennyLane's local `default.qubit` simulator, a validated JSON gate schema, bounded wires/gates/shots, and normalized probability output. It does not add quantum syntax to `.af` or claim hardware support.

Install the optional `quantum` extra on Python 3.12+. The core itself continues to support Python 3.11 without PennyLane. Automated tests cover input validation; the live PennyLane simulation still needs to be run in a Python 3.12+ environment.

## Integration requirements

- Define backend-neutral circuit and result contracts.
- Separate simulator and hardware-provider capabilities.
- Validate dependencies, resource costs, and backend availability.
- Normalize errors and results without hiding provider-specific constraints.
- Preserve all upstream licenses, notices, and dependency identifiers.

The imported provider source is located in [pennylane-main](pennylane-main/).
