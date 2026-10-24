# AssayFlux Linux Platform Integration

This directory contains a Linux kernel source tree being evaluated as a platform and systems-integration reference. It is not a replacement for the AssayFlux language core.

## Intended role

AssayFlux may expose Linux-specific capabilities through platform adapters for process management, filesystems, system inspection, and deployment. Kernel source should remain isolated from the compiler and runtime unless a concrete build or runtime dependency is demonstrated.

## Current status

**Imported platform source — AssayFlux integration not verified.** No claim is made that AssayFlux builds, modifies, or ships a Linux distribution.

## Integration requirements

- Inventory licenses, build prerequisites, architecture support, and source provenance.
- Keep kernel code separate from ordinary AssayFlux services.
- Define narrow OS capability interfaces and permission boundaries.
- Test adapters on supported Linux distributions.
- Preserve kernel copyright notices, license files, and required attribution.

The upstream kernel source is located in [linux-master](linux-master/).
