# Contributing to AssayFlux

Thank you for contributing to the AssayFlux AI ecosystem.

## Project principles

- Preserve existing functionality and the existing license.
- Keep independent AI systems separate from shared CORE infrastructure.
- Prefer small, focused, reviewable changes.
- Do not add placeholder model implementations or empty scaffolding as evidence of progress.
- Document dataset provenance and licensing before using data for training.
- Never commit secrets, credentials, large datasets, checkpoints, or generated artifacts by default.
- Never execute model-generated code automatically.
- Report test and benchmark results exactly as observed.

## Branches and pull requests

1. Start from the current `main` branch.
2. Create a focused branch, for example `feature/neural-tokenizer` or `docs/dataset-policy`.
3. Keep commits descriptive and scoped to one logical change.
4. Explain the motivation, design, tests run, and known limitations in the pull request.
5. Do not force-push shared branches or modify `main` directly without explicit authorization.
6. Merge only after review and applicable checks.

Suggested commit prefixes:

- `docs:` documentation and design records.
- `feat:` new functionality.
- `fix:` bug fixes.
- `test:` tests and fixtures.
- `refactor:` behavior-preserving restructuring.
- `build:` build and dependency configuration.
- `security:` security controls and remediation.

## Quality requirements

For code changes:

- Add or update tests for changed behavior.
- Validate configuration and input boundaries.
- Keep APIs typed and documented where practical.
- Make randomness and seeds explicit in experiments.
- Keep training, inference, evaluation, and application layers separated.
- Record reproducible commands and actual outcomes.
- Document unsupported platforms and failure modes.

For datasets:

- Record source, retrieval date, license, permitted use, transformations, and version.
- Check for secrets, credentials, corruption, and duplicates.
- Keep test data isolated from training and tuning.
- Do not infer training permission merely from public accessibility.

For model experiments:

- Record architecture/configuration, tokenizer version, seed, dataset version, code revision, and evaluation.
- Distinguish random initialization from pretrained initialization.
- Do not report capabilities without appropriate held-out evaluation.
- Keep large model artifacts out of Git unless explicitly approved.

## Security

Treat model outputs and imported datasets as untrusted. Do not run arbitrary generated shell commands. Any future code execution feature must use an appropriately isolated, resource-limited environment and explicit user authorization.

## Pull request checklist

- [ ] Change is focused and preserves unrelated functionality.
- [ ] Documentation is updated.
- [ ] Tests were added or updated.
- [ ] Tests actually executed and results are reported.
- [ ] No secrets or unapproved data/artifacts are included.
- [ ] Dataset and third-party licenses are documented where relevant.
- [ ] Limitations and follow-up work are recorded.
- [ ] No unsupported performance or capability claims are made.
