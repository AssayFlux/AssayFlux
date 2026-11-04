# Security Policy

## Scope

This policy applies to the AssayFlux repository, development workflow, model/data artifacts, and future applications or runtime components.

## Reporting a vulnerability

Do not publish exploit details, credentials, private datasets, or sensitive personal information in a public issue. Use GitHub's private vulnerability reporting feature if enabled. Otherwise contact repository maintainers through a private channel with impact, reproduction steps, and affected version. Do not include real secrets.

## Development requirements

- Treat datasets, model outputs, generated code, archives, and external contributions as untrusted input.
- Never execute generated code with host privileges or ambient credentials. Use an isolated sandbox with filesystem, network, CPU, memory, and time limits.
- Do not commit credentials, tokens, private keys, personal data, or private datasets.
- Validate paths, file types, sizes, and serialized input before processing.
- Pin and review dependencies; minimize permissions and network access.
- Keep large model/dataset artifacts outside normal Git history and verify provenance/checksums.
- Make destructive scripts opt-in and require explicit flags.
- Document security assumptions and known limitations.

## Disclosure

Coordinate fixes and disclosure with maintainers. Avoid public disclosure until a fix or mitigation is available and maintainers have had a reasonable opportunity to respond.
