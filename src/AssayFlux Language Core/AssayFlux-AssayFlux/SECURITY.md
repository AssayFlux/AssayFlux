# Security policy

AssayFlux is experimental software and is **not a hardened sandbox or security-certified product**. Do not run untrusted AssayFlux programs, Python packages, or generated native binaries with sensitive privileges.

## Reporting a vulnerability

Do not post exploit details, credentials, personal data, or weaponized proof-of-concept code in a public issue. Preserve the affected version, minimal reproduction, impact, and logs with secrets removed, and contact the project maintainer privately before public disclosure.

## Current defensive controls

- Deny-by-default capability checks for Python and project-module imports.
- Hard-denied high-risk Python modules and selected dangerous callables.
- Workspace-constrained project imports, cycle detection, and shared execution budgets.
- Source, AST, numeric-operation, collection, output, loop, and step limits.
- Structured diagnostics with source locations.
- Explicit runtime policy for capabilities and network access.

## Known limitations

- The interpreter runs in the host process; capability checks do not isolate operating-system system calls.
- Third-party Python libraries may perform hidden I/O or invoke native code.
- The language implementation does not yet implement every feature described in `GRAMMAR.md`.
- Static checks and tests cannot prove the absence of bugs.

For hostile code, use a separate OS-enforced sandbox/process with minimal filesystem, network, CPU, memory, and privilege access. Do not treat this language runtime as the isolation boundary.
