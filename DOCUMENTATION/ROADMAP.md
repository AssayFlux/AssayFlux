# AssayFlux Development Roadmap

**Roadmap status:** Planned; phase completion requires evidence.  
**Baseline:** `main` at `670252f07755bf222fca3f69fe9b570d27c41af3`.

This roadmap orders work by dependency and risk. It deliberately separates repository foundation, shared infrastructure, the first independent model, capability training, and ecosystem expansion.

## Delivery rules

- Work on a dedicated feature branch.
- Preserve existing files and behavior.
- Keep pull requests focused and reviewable.
- Add tests with executable components.
- Record exact commands and genuine results.
- Do not mark a phase complete because documentation or directory scaffolding exists.
- Keep model weights, datasets, and generated artifacts outside ordinary Git history by default.
- Do not claim device compatibility or performance without measurements on the actual target device.

## Phase 1 — Repository audit and baseline

**Objective:** Establish the actual starting point and safe boundaries.

Tasks:
1. Record repository, default branch, baseline commit, and tracked tree.
2. Inspect every tracked file and the initial commit.
3. Inventory source code, dependencies, tests, workflows, documentation, and releases.
4. Identify any existing AssayFlux language implementation in this repository or supplied project context before integration.
5. Record limitations of the audit (including local untracked files and other repositories not inspected).
6. Publish the baseline audit and architecture/roadmap documents.

**Exit criteria:** Baseline commit and tracked files are recorded; preservation boundaries are documented; no unsupported claims are made.

## Phase 2 — AI Pool foundation

**Objective:** Establish project conventions without fake implementations.

Tasks:
1. Define naming, ownership, versioning, and maturity labels for AI projects.
2. Document the boundary between independent AI systems and CORE.
3. Define dataset and model artifact policies.
4. Define security and safe-execution principles.
5. Improve the root README and contribution workflow.
6. Introduce directories only when meaningful files are ready to be added.

**Exit criteria:** Architecture is reviewed; repository conventions and component responsibilities are clear; existing license and ignore rules are preserved.

## Phase 3 — Shared CORE contracts

**Objective:** Create minimal, testable contracts that support Neural and later systems.

Suggested order:
1. Configuration schema and validation.
2. Model and tokenizer protocols.
3. Dataset manifest schema and validation.
4. Training and inference contracts.
5. Checkpoint metadata and save/restore interface.
6. Evaluation result schema.
7. Logging, reproducibility, and resource-reporting interfaces.
8. Model registry metadata specification.

Implement only the pieces that have concrete consumers and tests. Avoid a premature plugin framework or orchestrator.

**Exit criteria:** Contracts have documented semantics, import tests, validation tests, and at least one real consumer where applicable.

## Phase 4 — AssayFlux Neural experimental system

**Objective:** Build the first independently maintained, randomly initialized coding-model experiment.

Tasks:
1. Establish a minimal Python package and reproducible environment.
2. Implement a custom tokenizer and round-trip tests.
3. Implement a small decoder-only Transformer from random initialization.
4. Test tensor shapes, causal masking, forward pass, and loss.
5. Implement deterministic training and validation loops.
6. Implement checkpoint saving and recovery, including optimizer and random-state metadata as appropriate.
7. Add diagnostics and evaluation.
8. Keep inference separate from training.
9. Document resource requirements and limitations.

**Exit criteria:** Unit and integration tests pass; a small reproducible training run completes; checkpoint recovery is demonstrated; evaluation output is recorded. This does not imply useful coding ability.

## Phase 5 — Dataset pipeline and coding evaluation

**Objective:** Build a legally and technically responsible path from data sources to measurable coding tasks.

Tasks:
1. Define source and license review requirements.
2. Create versioned dataset manifests.
3. Validate records and file formats.
4. Detect duplicates and near-duplicates where appropriate.
5. Filter secrets, credentials, and corrupted samples.
6. Define reproducible train/validation/test splits and prevent leakage.
7. Document every preprocessing transformation.
8. Create held-out coding benchmarks and evaluation harnesses.
9. Start with one programming language and a narrow task family.

**Exit criteria:** Dataset lineage and license status are recorded; split integrity is tested; evaluation is reproducible and held out from training.

## Phase 6 — Coding intelligence development

**Objective:** Improve capability through measured training and evaluation, not claims.

Progressive capabilities:
1. Code token and syntax pattern modeling.
2. Code completion.
3. Code generation for constrained tasks.
4. Code explanation.
5. Syntax error identification.
6. Controlled debugging.
7. Refactoring with behavior-preservation tests.
8. Algorithmic reasoning.
9. Multi-file context handling.
10. Repository analysis and project generation.

Add languages only when data, tokenizer behavior, tests, and benchmark coverage support them. Report per-language and per-task performance separately.

**Exit criteria:** Each claimed capability has a documented benchmark, held-out results, failure analysis, and reproducible evaluation.

## Phase 7 — Additional independent AI systems

**Objective:** Expand only when shared contracts are proven by real systems.

Candidate domains:
- Research.
- Mathematics.
- Writing.
- Data analysis.
- Vision.
- Voice/audio.
- Automation.

Each project receives its own ownership, configuration, data policy, tests, evaluation, documentation, and versioning. Shared code is extracted only after repeated, stable use cases emerge.

**Exit criteria:** At least one additional system is independently testable and integrates through documented CORE contracts without coupling its internals to Neural.

## Phase 8 — AI Pool orchestration and applications

**Objective:** Integrate mature systems into a usable ecosystem.

Tasks:
1. Model discovery and lifecycle management.
2. Resource-aware model selection.
3. Task routing and orchestration.
4. Explicit inter-model message contracts.
5. Permission and security boundaries for tools/actions.
6. Android, desktop, and web clients.
7. Offline model packaging and update strategy.
8. End-to-end reliability, privacy, and performance evaluation.

**Exit criteria:** Integrated workflows pass end-to-end tests; model selection and failures are observable; security boundaries and offline behavior are documented.

## Phase gates and status

| Phase | Current status | Evidence required to close |
| --- | --- | --- |
| 1. Audit and baseline | Documentation baseline prepared | Review audit scope and confirm any external/local language project |
| 2. AI Pool foundation | Planned / documentation started | Architecture and contribution conventions accepted |
| 3. CORE contracts | Not started | Executable contracts with tests and consumer |
| 4. Neural experiment | Not started | Reproducible training and checkpoint recovery |
| 5. Dataset pipeline | Not started | Validated, licensed, versioned data pipeline |
| 6. Coding intelligence | Not started | Held-out benchmark evidence |
| 7. Independent systems | Not started | Independently tested additional AI system |
| 8. Orchestration/apps | Not started | End-to-end integrated workflows |

## Immediate next work

1. Review this baseline documentation and confirm the project boundaries.
2. Confirm whether the AssayFlux programming language exists in a separate repository or local project that should be linked or integrated later.
3. Create the first focused implementation PR for repository conventions and minimal CORE contracts.
4. Add executable code only alongside tests and documented acceptance criteria.
5. Begin the Neural tokenizer only after its interface, vocabulary format, and test cases are agreed.

## What this roadmap does not claim

- No AI model has been trained.
- No coding capability has been demonstrated.
- No framework has been selected or verified for a specific Android device.
- No device benchmark has been performed.
- No dataset has been approved for training.
- No phase beyond the documentation baseline is complete.
