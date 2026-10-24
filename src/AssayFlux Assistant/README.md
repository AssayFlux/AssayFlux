# AssayFlux Assistant Services

This module is the AssayFlux-facing entry point for assistant, knowledge-retrieval, and service-automation capabilities.

## Language-first integration

- Use the canonical AssayFlux language core for parsing, validation, and .af semantics.
- Expose assistant workflows through explicit, versioned service interfaces.
- Keep credentials, network access, data storage, and execution permissions behind policy-controlled adapters.
- Validate generated .af programs with the actual AssayFlux toolchain before execution.

## Current status

**Local diagnostic adapter implemented; Project NOMAD application integration remains unverified.** The language core exposes `assayflux.assistant.OfflineAssistant` and `assayflux assistant` commands backed by Project NOMAD's local `/api/ollama/chat` route, preserving its knowledge-base/RAG pipeline. It checks `/api/health` and installed models, defaults to loopback, performs no cloud fallback, bounds input/output, and returns deterministic diagnostic advice when the local service/model is unavailable. Direct Ollama mode is available as an explicit alternative. Suggestions are advisory and never applied or executed automatically.

The imported application is located in [project-nomad-main](project-nomad-main/README.md); original documentation is preserved in [UPSTREAM_README.md](project-nomad-main/UPSTREAM_README.md). The adapter intentionally uses Ollama's documented API rather than guessing an unverified Project NOMAD route. The adapter now targets verified NOMAD routes, but a live NOMAD stack test and an offline-with-network-disabled test remain outstanding.

## Phase 1 requirements

- Inventory dependencies, external services, configuration, network access, and data storage.
- Audit branding in UI surfaces, deployment files, package metadata, URLs, workflows, and environment variables.
- Preserve upstream licenses, notices, and provenance.
- Define a least-privilege adapter and integration tests before calling this service integrated.

AssayFlux branding here identifies the maintained integration boundary; it does not claim authorship of the imported implementation.
