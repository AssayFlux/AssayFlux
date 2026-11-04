# AssayFlux

**An independent AI ecosystem built as a central pool of specialized systems.**

AssayFlux is a long-term project to develop, train, evaluate, integrate, and deploy independently maintainable AI systems. The ecosystem is intended to support specialized capabilities such as programming, scientific research, mathematics, writing, data analysis, vision, audio, and automation.

The project is being developed incrementally. Architecture proposals, planned capabilities, implemented components, tested components, and production-ready systems are deliberately distinguished.

## Project status

The repository is at its baseline/foundation stage.

- The initial repository audit is documented in [DOCUMENTATION/BASELINE_AUDIT.md](DOCUMENTATION/BASELINE_AUDIT.md).
- The staged implementation plan is documented in [DOCUMENTATION/ROADMAP.md](DOCUMENTATION/ROADMAP.md).
- The mandatory task-by-task operating rules are in [WORKFLOW.md](WORKFLOW.md). Read this file before every change.
- The intended component boundaries are documented in [DOCUMENTATION/ARCHITECTURE.md](DOCUMENTATION/ARCHITECTURE.md).
- No AI model, tokenizer, training engine, inference engine, or device benchmark is currently claimed as implemented.
- AssayFlux Neural is the planned first independent AI system.

## Vision

AssayFlux is not intended to be a single chatbot. It is intended to become a central AI pool in which specialized systems can be developed independently and connected through stable, documented interfaces.

Each AI system should own the components specific to its domain, including model architecture, input processing, training, inference, datasets, evaluation, tests, documentation, and versioning where applicable. Shared infrastructure should provide reusable capabilities without coupling every system to one model implementation.

## Planned architecture

The repository now contains a documentation-first directory scaffold. The presence of a directory does not mean its software component is implemented:

| Area | Responsibility |
| --- | --- |
| `AI/` | Independently maintained specialized AI projects |
| `CORE/` | Shared interfaces and reusable runtime, training, inference, registry, dataset, and evaluation infrastructure |
| `DATASETS/` | Dataset manifests, provenance, licensing, validation, and preprocessing documentation |
| `APPS/` | Android, desktop, and web applications |
| `BENCHMARKS/` | Reproducible capability and performance evaluations |
| `TESTS/` | Cross-component and system-level tests |
| `DOCUMENTATION/` | Architecture, audit, roadmap, design decisions, and operational guidance |
| `SCRIPTS/` | Reproducible development and maintenance utilities |

Each scaffolded directory has an ownership README. Executable components will be added only when there is a concrete design, acceptance criteria, and tests.

## First system: AssayFlux Neural

AssayFlux Neural is planned as an independently developed coding assistant, initially implemented in Python.

Its experimental starting point is a small decoder-only Transformer with random initialization, a custom tokenizer, reproducible local training, checkpoint recovery, diagnostics, and evaluation. It will not depend on pretrained weights, external AI APIs, or mandatory cloud inference.

Programming-language coverage and coding capabilities will be claimed only after training and evaluation provide evidence.

## Development principles

1. Audit before modifying; preserve existing working functionality.
2. Build incrementally and keep changes on feature branches.
3. Prefer small, testable interfaces over premature complexity.
4. Keep specialized AI systems independent from shared infrastructure.
5. Track dataset origin, licensing, transformations, and versions.
6. Keep large datasets and checkpoints out of ordinary Git history.
7. Do not execute generated code automatically.
8. Measure actual behavior; never invent test results, benchmarks, or capabilities.
9. Treat offline-first operation as a design constraint.
10. Record limitations and distinguish implemented, tested, device-tested, and production-ready work.

## Development roadmap

See [DOCUMENTATION/ROADMAP.md](DOCUMENTATION/ROADMAP.md) for phases, tasks, dependencies, and exit criteria.

The immediate sequence is repository baseline, architecture foundation, shared interfaces, and then the independently testable AssayFlux Neural components. Device-specific training backend selection and performance claims require actual device measurements; no such measurements are asserted in this repository baseline.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for the proposed contribution and quality-control workflow. Changes should be focused, documented, tested where applicable, and submitted through a pull request.

## License

This repository currently includes the MIT License. See [LICENSE](LICENSE) for its terms. Dataset and third-party asset licenses must be reviewed separately; repository licensing does not automatically grant rights to external training data.
