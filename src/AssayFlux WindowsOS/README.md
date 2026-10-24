# AssayFlux Windows Platform Integration

This directory contains an imported Windows-compatible operating-system source tree being evaluated for platform and systems-integration work. It is not a replacement for the AssayFlux language core.

## Intended role

AssayFlux should expose Windows-specific functionality through platform adapters that implement shared interfaces for processes, filesystems, environment access, and system capabilities. Kernel or operating-system source should remain isolated unless a concrete dependency requires otherwise.

## Current status

**Imported platform source — AssayFlux integration not verified.** The source being present does not mean AssayFlux builds, modifies, or distributes a Windows operating system.

## Integration requirements

- Verify source provenance, license compatibility, build requirements, and supported architectures.
- Separate OS source from language runtime modules.
- Apply least privilege and test platform adapters.
- Preserve all upstream notices and required attribution.

The imported source tree is located in [reactos-master](reactos-master/).
