# AssayFlux AI Pool Architecture

**Status:** Proposed logical architecture; not an implementation specification for code that already exists.

## 1. Architectural objective

AssayFlux is a pool of independently maintainable AI systems connected through stable shared contracts. It is not one monolithic model. Specialized systems should be able to evolve, train, evaluate, and release independently while reusing common infrastructure where that reuse is justified.

## 2. Architectural layers

### Independent AI systems — `AI/`

Each system owns domain-specific implementation and lifecycle assets:

- Model architecture and configuration.
- Tokenizer or domain-specific input processing.
- Training and inference adapters.
- Dataset references and preprocessing definitions.
- Evaluation tasks and results.
- Tests, documentation, and version metadata.

The first planned system is `AI/Neural`, an experimental coding assistant. Other AI directories should be introduced when a real project is ready to be maintained.

### Shared infrastructure — `CORE/`

CORE provides reusable contracts and implementations only where multiple systems can benefit from them.

| Component | Responsibility |
| --- | --- |
| Interfaces | Stable contracts for models, tokenizers, datasets, trainers, and evaluators |
| Runtime | Model lifecycle and runtime configuration |
| Tokenizers | Shared tokenizer abstractions and utilities |
| Training Engine | Reusable training-loop primitives and callbacks |
| Inference Engine | Shared generation/inference contracts |
| Model Registry | Model identity, version, configuration, and artifact metadata |
| Dataset Manager | Dataset manifests, validation, provenance, and split handling |
| Evaluation Engine | Common evaluation protocol and result recording |
| Orchestrator | Future task routing and coordination between systems |
| Shared Utilities | Logging, diagnostics, reproducibility, and resource helpers |

Do not implement generic abstractions before a concrete use case exists. Avoid circular dependencies between CORE and individual AI systems.

### Dataset governance — `DATASETS/`

Track dataset identity, source, retrieval date, license, permitted use, transformations, filtering, deduplication, split assignment, version, and integrity metadata. A public URL is not proof that content is licensed for model training. Dataset payloads should be stored outside normal Git history unless small, licensed, and intentionally versioned.

### Applications — `APPS/`

Android, desktop, and web applications are presentation and interaction layers. They must call documented model/runtime interfaces rather than embedding training logic or coupling directly to a particular model implementation.

### Quality and operations

- `BENCHMARKS/`: reproducible task and performance benchmarks.
- `TESTS/`: cross-module and system integration tests.
- `DOCUMENTATION/`: design records, operating guides, and project status.
- `SCRIPTS/`: deterministic development, validation, and maintenance scripts.

## 3. Initial Neural boundary

AssayFlux Neural is an independent Python project. It should depend on CORE contracts, not on CORE implementation details that are irrelevant to it.

Initial intended modules:

- Custom tokenizer.
- Small randomly initialized decoder-only Transformer.
- Reproducible training loop.
- Checkpoint save/restore.
- Diagnostics and evaluation.
- Tests for each behavior.

No pretrained weights, external AI APIs, or mandatory remote inference are part of the initial design.

## 4. Dependency direction

Preferred dependency direction:

```text
Applications ───────► CORE interfaces ◄────── AI systems
                           ▲
                           │
                     CORE services
```

CORE must not import a specific AI project as a requirement for its own import or tests. AI systems may use CORE contracts and optional shared services. Applications should use supported runtime/service boundaries.

## 5. Artifact and version policy

- Source code and small configuration/manifests belong in Git.
- Large datasets, checkpoints, and generated artifacts do not belong in ordinary Git history by default.
- Every model release should identify source revision, configuration, tokenizer version, dataset versions, training seed, and evaluation results.
- Every dataset version should identify source, license, transformations, split policy, and integrity information.
- Evaluation results must be reproducible or clearly labeled as non-reproducible exploratory observations.

## 6. Security boundaries

- Model output is untrusted data, never privileged application instructions.
- Generated code is not executed automatically.
- Any future execution environment must be isolated and resource-limited.
- Dataset ingestion must validate formats and avoid secrets/credentials.
- Shell commands must not be assembled from untrusted model output and executed without explicit, safe mediation.
- Logs and checkpoints must not leak environment secrets.

## 7. Maturity labels

Use these terms consistently:

1. **Proposed** — documented design only.
2. **Implemented** — source code exists.
3. **Unit tested** — isolated tests executed successfully.
4. **Integration tested** — connected components tested together.
5. **Device tested** — verified on a named target device and recorded environment.
6. **Production ready** — security, reliability, performance, maintenance, and operational criteria have been met.

A directory, interface stub, or passing import is not proof of a functioning AI capability.
