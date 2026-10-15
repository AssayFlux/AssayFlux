# Contributing

1. Read `docs/LANGUAGE_SPECIFICATION.md` and `docs/SPECIFICATION_STATUS.md`.
2. Preserve the documented syntax unless a language change is intentional and discussed.
3. Add tests for syntax, runtime behavior, error conditions, and source locations.
4. Run `python -m pip install -e ".[dev]"` and `python -m pytest`.
5. Update the spec/status documentation for behavior changes.
6. Keep optional external runtimes optional; core CI should not fail just because a non-core compiler is absent.
7. Never describe a placeholder adapter as a tested integration.
