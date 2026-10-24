# AssayFlux macOS Platform Integration

This directory contains XNU source being evaluated as a platform and systems-integration reference. It is not a replacement for the AssayFlux language core.

## Intended role

AssayFlux can provide macOS-specific implementations behind shared platform interfaces where operating-system APIs differ. The presence of kernel source does not mean AssayFlux builds or distributes macOS.

## Current status

**Imported platform source — AssayFlux integration not verified.**

## Integration requirements

- Inventory licensing, build requirements, hardware assumptions, and provenance.
- Keep platform source separate from the compiler and runtime.
- Define supported host APIs and permission boundaries.
- Test adapters on supported macOS versions.
- Preserve all upstream copyright and license notices.

The imported source tree is located in [xnu-main](xnu-main/).
