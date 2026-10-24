# AssayFlux Branding and Attribution Policy

## Goal

Present AssayFlux as the unified product and language ecosystem while preserving legal notices, technical compatibility, and truthful provenance for imported code.

## Branding rules

1. Use **AssayFlux** as the umbrella product name and use consistent AssayFlux names for maintained service entry points, documentation, examples, and supported CLI commands.
2. Prefer language-first naming such as **AssayFlux CLI**, **AssayFlux Execution Service**, **AssayFlux Assistant**, and **AssayFlux Security Service** where the implementation and integration status justify those names.
3. Do not imply an imported component is already integrated with .af, the canonical runtime, or AssayFlux security controls unless tests prove it.
4. Replace upstream branding in maintained user-facing surfaces when it does not break functionality or misrepresent the origin of code.
5. Keep third-party product names where they identify an actual dependency, API, package, file format, supported platform, or necessary compatibility target.
6. Preserve upstream licenses, copyright notices, patent notices, attribution requirements, and other legally required material. Do not rewrite third-party licenses to claim AssayFlux ownership.
7. Retain original documentation as UPSTREAM_README.md when replacing a module's default README with an AssayFlux-facing integration guide. The upstream document is provenance/reference material, not a statement that integration is complete.
8. Review URLs, badges, package names, Docker image names, workflow references, environment variables, and executable names before changing them. A branding replacement must not silently break a build, update mechanism, or external API.
9. Do not remove security advisories, vulnerability reporting details, or required credits during rebranding.
10. Keep a record of components, source origins, versions/commits where known, licenses, local modifications, and outstanding integration work.

## Status vocabulary

- **Imported:** source is present but has not yet been fully reconciled.
- **Adapted:** local changes align selected interfaces or behavior with AssayFlux.
- **Integrated:** a defined AssayFlux interface is implemented and integration tests pass.
- **Verified:** documented acceptance tests and relevant security checks pass.
- **Planned:** not yet implemented.

## Migration sequence

1. Reconcile the repository inventory and identify all user-facing branding surfaces.
2. Rebrand top-level entry points and module documentation without discarding original reference material.
3. Review package metadata, build scripts, container labels, workflows, links, and UI assets component by component.
4. Update branding only after validating all affected references and tests.
5. Audit licenses and notices before release.

Branding changes must not be used to obscure provenance or suggest that upstream code was originally authored by AssayFlux.
