# AssayFlux Master Workflow

**This file is the controlling project workflow.** Read it before every task, implementation session, pull request, or architectural change. If another plan conflicts with this file, stop and reconcile the conflict here before coding.

Last reviewed: 2026-11-04
Current repository head at scaffold verification: `main` (`7a48020b30eaf4c05392ea5172a2ea8f2cfd4cdd`). Use a feature branch for all subsequent changes.
Project status: foundation and documentation scaffold; no model or training implementation is claimed.

## 1. Mandatory start-of-task procedure

Before doing any work:

1. Read this entire file.
2. Read `README.md` and the relevant sections of `DOCUMENTATION/BASELINE_AUDIT.md`, `DOCUMENTATION/ARCHITECTURE.md`, and `DOCUMENTATION/ROADMAP.md`.
3. Inspect the current branch, working tree/remote diff, recent commits, and open pull requests. Do not assume a previous session's branch or commit is still current.
4. Inspect the target directory and its existing files before creating, moving, or replacing anything.
5. Search for existing AssayFlux language/model code and reuse or integrate it only after auditing its behavior, license, tests, and compatibility. Never overwrite working code based on assumptions.
6. Identify the active phase, its dependencies, acceptance criteria, and the smallest useful deliverable.
7. Record the intended change and any risks in the relevant design/plan document before substantial implementation.

If this file is missing, contradictory, or stale, stop feature work and repair/review the workflow first.

## 2. Mandatory end-of-task procedure

At the end of every task:

1. Run relevant formatting, static checks, and tests; record exact commands and honest results.
2. Review the full diff for accidental deletions, secrets, generated artifacts, unrelated changes, and license issues.
3. Update this file's **Current execution state** and **Change log**.
4. Update the roadmap phase status only when its exit criteria have evidence. Directory creation or documentation alone does not complete an implementation phase.
5. Update architecture/decision records when interfaces or boundaries change.
6. Commit to a focused feature branch; do not push directly to `main`.
7. Report changed paths, commit/PR, checks performed, checks not performed, and remaining blockers.
8. Leave the repository in a coherent state that another contributor can continue.

## 3. Product vision and non-negotiable principles

AssayFlux is an independent AI ecosystem / central pool of specialized systems. Each AI system must be independently developable, testable, versioned, and replaceable. Shared infrastructure belongs in CORE only when multiple real consumers justify it.

- Offline-first by design; cloud services must be optional, explicit, and replaceable.
- Preserve existing working AssayFlux language and project code.
- No pretrained weights or external AI APIs as a hidden dependency for the first Neural experiment; the initial model is randomly initialized.
- Keep model training, inference, evaluation, and app layers separate.
- Build small, testable components; avoid premature frameworks and orchestration.
- Dataset provenance, licensing, privacy, quality, deduplication, and split integrity are mandatory.
- Never execute model-generated code automatically. Use isolated, permission-limited execution for evaluation.
- Do not commit datasets, credentials, private data, checkpoints, or large generated artifacts by default.
- Never claim a capability, test, benchmark, device compatibility, or completion without evidence.
- Distinguish **planned**, **implemented**, **tested**, **device-tested**, and **production-ready**.

## 4. Target repository structure

Create real directories only with a README or meaningful tracked file. Keep each README short and explain ownership, allowed contents, dependencies, and the next concrete task.

```text
.
├── README.md
├── WORKFLOW.md
├── CONTRIBUTING.md
├── SECURITY.md
├── LICENSE
├── .gitignore
├── .github/
│   └── PULL_REQUEST_TEMPLATE.md
├── AI/
│   └── NEURAL/
├── CORE/
│   └── contracts/
├── DATASETS/
│   ├── manifests/
│   └── sources/
├── APPS/
│   ├── ANDROID/
│   ├── DESKTOP/
│   └── WEB/
├── BENCHMARKS/
│   └── NEURAL/
├── TESTS/
│   ├── unit/
│   ├── integration/
│   └── system/
├── SCRIPTS/
│   └── dev/
└── DOCUMENTATION/
    ├── decisions/
    ├── BASELINE_AUDIT.md
    ├── ARCHITECTURE.md
    └── ROADMAP.md
```

This is a logical ownership layout, not a mandate to implement every subsystem immediately. A directory may remain documentation-only until an approved, testable implementation is ready. Avoid duplicate code and circular imports.

## 5. Architecture boundaries

### AI/<SYSTEM>
Owns each specialized system's model architecture, tokenizer/input processing, training, inference, evaluation adapters, configuration, tests, and system-specific docs. AI systems must not import another AI system's private internals.

### CORE
Owns only stable shared contracts and proven reusable infrastructure: configuration, interfaces, artifact metadata, logging, reproducibility, registry, resource reporting, and shared dataset/evaluation utilities. Depend on contracts, not Neural implementation details.

### DATASETS
Owns manifests, source attribution, license review, validation rules, preprocessing descriptions, split definitions, and data quality reports. Raw data is stored outside Git unless a source's license and size make repository storage explicitly appropriate.

### APPS
Owns user-facing Android, desktop, and web clients. Apps call documented CORE/runtime interfaces; they do not embed model training logic.

### BENCHMARKS and TESTS
Keep benchmark tasks/results distinct from unit/integration/system correctness tests. Evaluation datasets must be held out from training where required and protected against leakage.

### SCRIPTS
Only reproducible, documented developer utilities. Scripts must be safe by default, explicit about destructive actions, and tested where practical.

## 6. Implementation order and phase gates

### Phase 0 — Repository scaffold and workflow
- Keep the original license and ignore policy.
- Add the directory ownership map and this workflow.
- Add security and contribution conventions.
- Verify links, tree, and diff.
- Gate: every tracked directory has a clear purpose; no fake source/model code or empty placeholder files.

### Phase 1 — Baseline audit and architecture
- Inspect all tracked files and relevant project context.
- Inventory existing language implementation, dependencies, tests, data, and workflows.
- Record gaps, assumptions, risks, and scope limitations.
- Gate: audit and architecture are accurate and reviewed.

### Phase 2 — CORE contract design
- Specify configuration validation.
- Specify model/tokenizer protocols.
- Specify dataset manifest schema.
- Specify training/inference interfaces.
- Specify checkpoint metadata and save/restore contract.
- Specify evaluation result schema and reproducibility metadata.
- Gate: contracts have semantics, tests, and at least one real consumer before being treated as stable.

### Phase 3 — AssayFlux Neural minimum experiment
- Confirm language/runtime and dependency strategy based on measured constraints.
- Implement tokenizer format and round-trip tests.
- Implement a small decoder-only Transformer with random initialization.
- Test shapes, causal attention mask, forward pass, loss, and deterministic behavior.
- Implement minimal train/validation loop, checkpoint recovery, and separate inference.
- Gate: reproducible tiny training run, passing tests, successful checkpoint restore, documented limitations. This does not prove coding ability.

### Phase 4 — Dataset governance and evaluation
- Review source license and usage permissions.
- Create versioned manifests and source lineage.
- Validate formats, remove secrets, inspect quality, deduplicate, and prevent leakage.
- Define held-out coding tasks and a reproducible evaluator.
- Gate: data lineage, license decisions, split integrity, and evaluation reproducibility documented.

### Phase 5 — Measured coding capability
- Start with a narrow language/task family.
- Progress through syntax/token modeling, completion, constrained generation, explanation, error detection, debugging, refactoring, algorithms, and multi-file tasks.
- Add a capability only with held-out benchmark results and failure analysis.
- Gate: every public capability claim maps to reproducible evidence.

### Phase 6 — Additional independent systems
- Add research, math, writing, data, vision, audio, or automation systems only when there is a concrete scope.
- Keep ownership, datasets, tests, and releases independent.
- Extract shared abstractions only after repeated stable use.
- Gate: an additional system runs and tests independently through documented interfaces.

### Phase 7 — AI Pool integration and applications
- Add model discovery, lifecycle, resource-aware routing, permissions, and orchestration.
- Build app clients against stable runtime APIs.
- Validate offline packaging, privacy, reliability, and end-to-end behavior.
- Gate: end-to-end workflows are tested; failure modes and security boundaries are documented.

## 7. Quality and safety gates

Every executable component should include, as appropriate:
- Unit tests for deterministic behavior and edge cases.
- Integration tests for component boundaries.
- Type/static checks and formatting.
- Reproducible configuration and random seeds.
- Clear errors and structured logs without secrets.
- Resource limits and safe handling of untrusted inputs.
- Documentation for setup, usage, limitations, and recovery.

Model-generated code must be treated as untrusted. Never run it on the host with ambient credentials or unrestricted filesystem/network access. Use a disposable sandbox with resource/time limits and explicit test fixtures.

## 8. Dataset and artifact rules

Every dataset manifest should identify source, retrieval/version date, license and evidence, permitted use, transformations, filtering, deduplication, splits, checksums, and known limitations. Unknown licensing means do not use for training until resolved.

Keep large datasets and model checkpoints in an appropriate artifact store or local ignored location. Commit small metadata/manifests, not bulk artifacts. Never commit secrets or personal/private data.

## 9. Branch, commit, and review rules

- Use focused branches such as `feature/neural-tokenizer` or `fix/core-config-validation`.
- Never rewrite shared history or force-push unless explicitly authorized and coordinated.
- Never commit directly to `main`.
- Use descriptive commits: `docs:`, `feat:`, `fix:`, `test:`, `refactor:`, `security:`.
- PRs state scope, design, tests run, tests not run, risks, and follow-up work.
- Do not merge a PR without explicit user authorization.
- Keep changes small enough to review; split unrelated work.

## 10. Current execution state

- [x] Initial repository baseline audit documented.
- [x] AI Pool architecture and staged roadmap documented.
- [x] Contribution guidance added.
- [x] Add and verify the tracked directory scaffold.
- [x] Add security policy and pull request template.
- [ ] Review scaffold PR and merge only with authorization.
- [ ] Design minimal CORE contracts.
- [ ] Implement Neural tokenizer and model only after contract/design review.

**Active phase:** Phase 0 — Repository scaffold and workflow.
**Next task:** Design the minimal CORE contracts on a focused feature branch, after confirming whether an existing AssayFlux language implementation lives outside this repository.
**Known non-claims:** No trained model, tokenizer, training engine, dataset approval, coding benchmark, or device verification is claimed.

## 11. Change log

- 2026-11-04: Added the documentation-first directory scaffold, ownership READMEs, security policy, PR template, and root workflow on the existing feature branch. Verified on 2026-11-04: all scaffold README files, policy files, workflow, and original LICENSE/.gitignore are present on `main`. No source implementation or tests were added in this scaffold.
