# AssayFlux Interpreter and Sandbox Infrastructure

This module is the AssayFlux-facing entry point for interpreter-related and isolated-execution infrastructure.

## Core distinction

The canonical AssayFlux language interpreter belongs to the Language Core project. This imported codebase may provide sandbox or code-interpreter infrastructure, but it must not create a competing .af grammar or silently replace canonical runtime semantics.

## Integration status

The language core now includes a host-side client for the imported Code Interpreter HTTP service. It calls `POST /execute`, parses the service's newline-delimited JSON event stream, and can select a language or reuse an explicitly supplied context ID. The server remains a separately deployed FastAPI/Jupyter service; it is not embedded into the AssayFlux package.

```bash
export ASSAYFLUX_CODE_INTERPRETER_URL=http://127.0.0.1:8000
assayflux execute --provider code-interpreter --allow-external-execution \
  --code 'import math; print(math.sqrt(81))'
```

An optional `ASSAYFLUX_CODE_INTERPRETER_TOKEN` is forwarded as `X-Access-Token`. The adapter does not create or delete contexts automatically.

## Remaining verification

- Test against a locally deployed service and verify supported kernels, context lifecycle, cancellation, and error handling.
- Review access-token validation, default-context sharing, code logging, and network exposure in the imported server before exposing it to clients.
- Verify CPU, memory, time, filesystem, process, and network boundaries in the deployed sandbox.
- Preserve upstream license and provenance information.

Adapter unit tests do not prove that a particular Code Interpreter deployment is isolated or safe for untrusted code. The canonical `.af` interpreter remains in the Language Core.
