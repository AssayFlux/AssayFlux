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
7. Logging, diagnostics, reproducibility, and resource-reporting interfaces.
8. Compute/resource capability reporting (device, memory, accelerator availability, and safe limits) without assuming a specific device.
9. Model registry metadata specification, including lifecycle state and artifact provenance.
10. Optional retrieval/index interfaces only after a concrete consumer and privacy boundary are defined.

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
9. Document resource requirements and limitations, including peak memory, throughput/latency measurement methods, and graceful behavior when resources are insufficient.
10. Add diagnostic hooks for training/inference health, loss curves, timing, memory use, and actionable failures without logging secrets.
11. Evaluate optimization options (for example mixed precision, compilation, and quantization) only against a correct baseline; keep them optional and record quality/resource trade-offs.
12. Define model artifact version metadata and compatibility rules for model, tokenizer, configuration, and checkpoint versions.

**Exit criteria:** Unit and integration tests pass; a small reproducible training run completes; checkpoint recovery is demonstrated; evaluation output is recorded; resource use and diagnostics are measured on a declared environment. Optimizations remain optional and are accepted only with correctness and quality comparisons. This does not imply useful coding ability or target-device support.

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
10. Define context-window construction, truncation, long-input handling, and context provenance for evaluation.
11. If retrieval is needed, specify indexed sources, chunking, ranking, freshness, deletion, and access-control behavior; keep retrieval optional and separate from model weights.

**Exit criteria:** Dataset lineage and license status are recorded; split integrity is tested; evaluation is reproducible and held out from training; context and any retrieval path have leakage, privacy, and access-control tests.

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
11. Explicit reasoning strategies appropriate to the task (for example decomposition, planning, verification, and retry limits), measured for correctness, latency, and token/resource cost.
12. Context and memory management: bounded conversation/session state, explicit retention and deletion semantics, summarization provenance, and protection against cross-user or cross-project leakage.
13. Optional retrieval-augmented generation with source attribution, relevance evaluation, and defenses against untrusted retrieved instructions.

Add languages only when data, tokenizer behavior, tests, and benchmark coverage support them. Report per-language and per-task performance separately. Memory and retrieval must be explicit, bounded, permission-aware, and optional; they must not silently retain sensitive content.

**Exit criteria:** Each claimed capability has a documented benchmark, held-out results, failure analysis, and reproducible evaluation. Reasoning, context, and retrieval features have ablation tests and measured quality/resource trade-offs.

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
8. Tool integration through explicit capability manifests, typed input/output contracts, allowlists, user approval for consequential actions, timeouts, and auditable execution.
9. Permission model for files, network, subprocesses, secrets, and cross-system calls; deny by default and isolate untrusted model/tool outputs.
10. Model lifecycle management: import, validation, versioning, activation, rollback, retirement, and artifact integrity checks.
11. Deployment packaging, local/offline installation, updates, compatibility checks, and recovery from interrupted updates.
12. Operational monitoring and diagnostics for latency, resource use, failures, model/version identity, and privacy-preserving telemetry controls.
13. Quantization and other deployment optimizations validated against task quality, numerical correctness, memory, and latency baselines.
14. End-to-end reliability, privacy, and performance evaluation.

**Exit criteria:** Integrated workflows pass end-to-end tests; model selection and failures are observable; tool permissions and sandbox boundaries are tested; lifecycle and rollback work; offline installation/update recovery is documented; monitoring does not expose private data; performance and quality trade-offs are measured.

## Phase gates and status

| Phase | Current status | Evidence required to close |
| --- | --- | --- |
| 1. Audit and baseline | Documentation baseline prepared | Review audit scope and confirm any external/local language project |
| 2. AI Pool foundation | Planned / documentation started | Architecture and contribution conventions accepted |
| 3. CORE contracts | Not started | Executable contracts with tests and consumer; resource, diagnostics, and artifact metadata contracts specified only where needed |
| 4. Neural experiment | Not started | Reproducible training and checkpoint recovery; measured resource profile, diagnostics, and baseline-vs-optimization comparisons |
| 5. Dataset pipeline | Not started | Validated, licensed, versioned data pipeline; context/retrieval privacy and leakage checks where applicable |
| 6. Coding intelligence | Not started | Held-out benchmark evidence; measured reasoning/context/retrieval gains and bounded memory behavior |
| 7. Independent systems | Not started | Independently tested additional AI system |
| 8. Orchestration/apps | Not started | End-to-end integrated workflows; permissioned tools, lifecycle/rollback, offline deployment, and privacy-preserving monitoring |

## Immediate next work

1. Review this baseline documentation and confirm the project boundaries.
2. Confirm whether the AssayFlux programming language exists in a separate repository or local project that should be linked or integrated later.
3. Create the first focused implementation PR for repository conventions and minimal CORE contracts.
4. Add executable code only alongside tests and documented acceptance criteria.
5. Begin the Neural tokenizer only after its interface, vocabulary format, and test cases are agreed.
6. During CORE design, include only minimal resource-reporting, diagnostics, and artifact metadata contracts with concrete Neural consumers; defer general orchestration, memory, retrieval, and tool frameworks until justified by a real use case.
7. Keep reasoning, memory, retrieval, optimization, tool use, monitoring, and deployment as staged capabilities with explicit safety, privacy, quality, and resource acceptance tests.

## What this roadmap does not claim

- No AI model has been trained.
- No coding capability has been demonstrated.
- No framework has been selected or verified for a specific Android device.
- No device benchmark has been performed.
- No dataset has been approved for training.
- No phase beyond the documentation baseline is complete.
