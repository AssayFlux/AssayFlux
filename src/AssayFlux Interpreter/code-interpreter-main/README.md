# AssayFlux Sandbox Runtime Integration

This directory contains imported sandbox/code-interpreter infrastructure being evaluated for safe execution workflows. It is not, by itself, the canonical AssayFlux language interpreter.

## Intended role

AssayFlux source must be parsed and semantically validated by the language core. Sandbox infrastructure may provide an isolation boundary for selected execution workloads, subject to explicit policies and a supported runtime adapter.

## Current integration status

**Imported — integration and isolation guarantees not yet verified.** Do not assume this source tree provides a complete sandbox, that its hosted services are available locally, or that its defaults meet AssayFlux's threat model.

## Integration requirements

- Define a backend-neutral sandbox interface.
- Validate CPU, memory, time, filesystem, process, and network boundaries.
- Keep API keys and other secrets outside the repository and execution logs.
- Test lifecycle cleanup, timeout handling, cancellation, and failed starts.
- Document which execution paths are local, remote, or provider-dependent.
- Preserve applicable upstream licenses, notices, and compatibility requirements.

## Reference documentation

The imported sandbox project's original documentation is preserved in [UPSTREAM_README.md](UPSTREAM_README.md). Review provider-specific setup and SDK details before using them in an AssayFlux deployment.

See the repository-level [Branding and Attribution Policy](../../../docs/BRANDING_AND_ATTRIBUTION.md).
