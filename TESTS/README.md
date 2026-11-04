# TESTS

Correctness and reliability tests live here when they are not best colocated with a package.

- `unit/`: isolated functions, schemas, and components.
- `integration/`: boundaries between packages and services.
- `system/`: end-to-end workflows and application behavior.

Tests must be deterministic where practical, use small fixtures, avoid network access by default, and never execute untrusted generated code outside a sandbox. Package-local tests may remain beside the package they test.
