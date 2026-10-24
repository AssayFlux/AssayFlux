# AssayFlux Security Services

This module is the AssayFlux-facing entry point for security assessment and authorized testing capabilities.

## Integration boundaries

- Expose tools through explicit service interfaces and auditable execution records.
- Require authorization and defined target scope for active testing.
- Separate passive inspection from potentially disruptive operations.
- Apply least privilege, allowlists, rate limits, and secret-handling rules.
- Keep the canonical AssayFlux language pipeline separate from tool-specific implementations.

## Current status

**Imported security toolkit — integration and safety controls not yet verified.** The source is located in [hackingtool-master](hackingtool-master/README.md); upstream reference documentation is preserved in [UPSTREAM_README.md](hackingtool-master/UPSTREAM_README.md).

## Phase 1 requirements

Inventory every tool, dependency, license, required privilege, network behavior, and potential side effect. Do not describe a tool as supported or safe until its operating boundaries and tests have been reviewed.

AssayFlux branding identifies the intended service boundary and does not claim ownership of upstream code.
