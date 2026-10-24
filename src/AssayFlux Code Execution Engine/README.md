# AssayFlux Execution Services

This module is the AssayFlux-facing entry point for execution-provider infrastructure.

## Language-first integration

The canonical AssayFlux pipeline must parse and validate .af source before execution. External-language runtimes may be supported as separate providers, but they do not replace the canonical interpreter or define AssayFlux semantics.

## Integration status

A host-side Piston API v2 adapter is available in the AssayFlux language core at `assayflux.execution.providers.PistonProvider`. It calls a separately deployed service; it does not start Docker, install Piston, or install language runtimes. It is an external-language provider, not an alternate runtime for `.af`.

```bash
export ASSAYFLUX_PISTON_URL=http://127.0.0.1:2000
assayflux execute --provider piston --allow-external-execution \
  --language python --version 3.12.0 --code 'print(6 * 7)'
```

Use a runtime/version actually returned by the target service. An optional `ASSAYFLUX_PISTON_TOKEN` environment variable is forwarded as a bearer token when your deployment requires it.

## Remaining verification

- Run the adapter against a controlled Piston deployment and representative compiled/interpreted languages.
- Verify deployed CPU, memory, process, filesystem, and network controls independently of client timeouts.
- Preserve upstream licenses, notices, compatibility identifiers, and provenance.
- Add deployment-level tests before claiming support for untrusted workloads.

The adapter is covered by unit tests, but service connectivity and real workload isolation have not been verified in this repository workflow.
