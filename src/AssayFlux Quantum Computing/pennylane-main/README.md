# AssayFlux Quantum Provider Adapter

This directory contains the AssayFlux-facing entry point for the imported quantum-computing framework.

## Intended role

AssayFlux may expose circuit construction, simulation, execution, and result normalization through a stable provider interface. The canonical AssayFlux language core remains responsible for .af syntax and semantics; provider-specific functionality must remain behind service APIs.

## Current status

**Imported provider — native AssayFlux integration not verified.** The upstream implementation and its existing dependencies are preserved. No claim is made that .af programs can currently invoke this provider through a tested AssayFlux interface.

## Integration requirements

- Define backend-neutral circuit and result contracts.
- Separate simulator and hardware-provider capabilities.
- Validate dependency, resource, and backend requirements.
- Preserve the upstream license, notices, package identifiers, API compatibility, and provenance.
- Add adapter and integration tests before advertising native support.

Read [UPSTREAM_README.md](UPSTREAM_README.md) for the original project documentation. See the [AssayFlux Quantum Computing module](../README.md) and [Branding and Attribution Policy](../../../docs/BRANDING_AND_ATTRIBUTION.md).

This README describes the AssayFlux integration boundary; it does not claim authorship of the imported framework.
