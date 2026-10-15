# Security policy

AssayFlux is an early-stage interpreter. It is intended for trusted programs and development environments. It is not a sandbox.

## Important execution boundary

- Python imports run with the permissions of the AssayFlux process.
- External-language adapters may launch arbitrary executables.
- Process timeouts do not restrict filesystem access, network access, memory use, or privilege.
- Never run unknown `.af` programs or external-language source on a privileged system.

For untrusted code, use a separately configured operating-system sandbox or isolated container with restricted filesystem and network access, a non-privileged user, and CPU/memory/process limits. The core interpreter does not itself provide these guarantees.

## Reporting issues

For security-sensitive issues, do not publish exploit details before maintainers have had a chance to assess the risk. Contact the repository owner through the private reporting mechanism configured on the GitHub repository.
