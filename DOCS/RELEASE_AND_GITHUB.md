# Publishing AssayFlux to GitHub and installing it

## 1. Before publishing

1. Create a GitHub repository named `AssayFlux` (or choose your own name).
2. Upload the contents of this project folder, not the ZIP file nested inside the repository.
3. Confirm `pyproject.toml`, `assayflux/`, `tests/`, `examples/`, and `docs/` are at the repository root.
4. Run the test suite locally: `python -m pip install -e ".[dev]"` then `python -m pytest`.
5. Push the repository to GitHub and wait for the CI workflow to pass.

## 2. Install from GitHub

Replace `OWNER` and `REPOSITORY` with the actual account and repository names:

```bash
python -m pip install "git+https://github.com/OWNER/REPOSITORY.git"
assayflux path/to/program.af
```

For a private repository, configure Git authentication before installation. Do not embed access tokens in shell history or project files.

## 3. Install locally for development

```bash
python -m pip install -e ".[dev]"
python -m pytest
assayflux examples/hello.af
```

## 4. Release discipline

- Keep the language specification and tests in the same commit as behavior changes.
- Tag published versions (for example `v0.2.0`) only after CI passes.
- Record supported Python versions and external runtime versions in release notes.
- Do not claim a language adapter is supported until its runtime and integration tests pass in a defined environment.
