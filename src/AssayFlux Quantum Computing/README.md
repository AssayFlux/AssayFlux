# AssayFlux Quantum Computing Services

This directory contains an imported quantum software framework being evaluated as a provider for AssayFlux quantum-computing capabilities.

## Intended role

AssayFlux should expose a stable quantum provider interface for circuit construction, simulation, execution, and result normalization. The language core remains responsible for .af syntax and semantics; quantum functionality belongs behind a service API.

## Current status

**Imported provider — AssayFlux integration not verified.** No claim is made that .af programs can currently invoke this framework through a native AssayFlux interface.

## Integration requirements

- Define backend-neutral circuit and result contracts.
- Separate simulator and hardware-provider capabilities.
- Validate dependencies, resource costs, and backend availability.
- Normalize errors and results without hiding provider-specific constraints.
- Preserve all upstream licenses, notices, and dependency identifiers.

The imported provider source is located in [pennylane-main](pennylane-main/).
