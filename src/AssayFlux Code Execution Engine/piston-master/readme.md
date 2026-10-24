# AssayFlux Execution Service

This directory contains an imported general-purpose code execution engine being evaluated as a backend for AssayFlux execution workloads.

## Intended role

The target is a common execution adapter for workloads that benefit from isolated worker processes and multi-language support. AssayFlux .af programs must still be parsed and checked by the canonical AssayFlux language pipeline; this component does not replace the AssayFlux interpreter.

## Current integration status

**Imported — integration and security posture not yet verified.** Do not assume the upstream engine is wired into AssayFlux or that its deployment is automatically safe for arbitrary untrusted code. Isolation, resource limits, network policy, lifecycle controls, and threat-model review must be validated before production use.

## Integration requirements

- Define a versioned AssayFlux execution-provider interface.
- Separate .af compilation/validation from any external-language execution.
- Apply explicit limits for CPU, memory, time, processes, filesystem, and network access.
- Test cancellation, timeout, worker failure, and cleanup behavior.
- Preserve supported runtime and package identifiers where they are part of compatibility.
- Keep upstream license and attribution notices intact.

## Reference documentation

The imported engine's original documentation is preserved in [UPSTREAM_README.md](UPSTREAM_README.md). Refer to it for upstream behavior, then validate all configuration and deployment instructions for AssayFlux.

See the repository-level [Branding and Attribution Policy](../../../docs/BRANDING_AND_ATTRIBUTION.md).
