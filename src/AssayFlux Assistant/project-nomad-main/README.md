# AssayFlux Assistant & Knowledge Services

This directory contains an imported knowledge-server and assistant capability codebase being evaluated for integration into the AssayFlux ecosystem.

## Intended role

The target architecture is to expose useful knowledge retrieval, assistant workflows, and service-management capabilities through modular AssayFlux service interfaces. The AssayFlux language core remains the authority for .af syntax and semantics; this component must not define a competing language.

## Current integration status

**Imported — integration not yet verified.** The source tree still contains upstream-specific application assumptions, configuration, URLs, deployment workflows, and service names. Do not treat this component as a native .af service until its adapter, permission model, configuration, and integration tests are implemented.

## Integration requirements

- Inventory runtime dependencies, network access, data storage, and external services.
- Define explicit service APIs and permission scopes.
- Keep secrets out of source files and logs.
- Add tests for configuration, failure handling, and data boundaries.
- Reconcile branding and deployment references without breaking upstream-derived functionality.
- Preserve applicable license and attribution notices.

## Reference documentation

The imported project's original documentation is preserved in [UPSTREAM_README.md](UPSTREAM_README.md). Its original instructions and URLs may describe the upstream deployment rather than the AssayFlux integration target, so validate them before use.

See the repository-level [Branding and Attribution Policy](../../../docs/BRANDING_AND_ATTRIBUTION.md).
