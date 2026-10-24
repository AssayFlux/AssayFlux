# AssayFlux Security Services

This directory contains an imported collection of security-testing tools being evaluated for integration as controlled AssayFlux security capabilities.

## Intended role

Security functions should be exposed through explicit, auditable service interfaces with scope restrictions and clear authorization requirements. The language core defines .af syntax; this service must not introduce an alternative language or bypass the runtime's permission model.

## Current integration status

**Imported — integration and safety controls not yet verified.** Tool presence is not evidence that each tool is installed, operational, authorized for a target, or safely constrained.

## Integration requirements

- Require explicit authorization and target scope for security testing.
- Separate passive analysis from active testing and potentially disruptive operations.
- Enforce allowlists, permission checks, rate limits, and auditable execution records.
- Never store credentials or sensitive scan results in source control.
- Validate dependencies and document each tool's purpose and risk.
- Preserve applicable licenses, notices, and required credits.

## Reference documentation

The imported security toolkit's original documentation is preserved in [UPSTREAM_README.md](UPSTREAM_README.md). Review its prerequisites and instructions carefully; they may not match the eventual AssayFlux service interface.

See the repository-level [Branding and Attribution Policy](../../../docs/BRANDING_AND_ATTRIBUTION.md).
