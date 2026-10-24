# External Execution Providers

AssayFlux keeps the canonical `.af` pipeline separate from optional external runtimes:

- `assayflux check program.af` parses and validates AssayFlux source.
- `assayflux run program.af` runs it through the canonical AssayFlux interpreter.
- `assayflux execute --provider piston ...` sends a different language to a separately deployed Piston service.
- `assayflux execute --provider code-interpreter ...` sends Python or another supported notebook-kernel language to the imported Code Interpreter service.

Neither external provider accepts `.af` as a substitute for the canonical interpreter. There is no automatic fallback from `assayflux run` to an external service.

## Universal runtime inventory

Use `assayflux languages --json` to inspect runtime versions reported by Piston and the Code Interpreter default path. Code Interpreter is listed only when its health endpoint succeeds. A successful health check is not a sandbox/security certification.

## Piston

Piston is a separately deployed HTTP service. The adapter calls `GET /api/v2/runtimes` and `POST /api/v2/execute`. It does not install Piston, install language runtimes, or start Docker for you.

Configure the service URL in the environment:

```bash
export ASSAYFLUX_PISTON_URL=http://127.0.0.1:2000
# Optional if your Piston deployment requires a bearer token:
export ASSAYFLUX_PISTON_TOKEN=...
```

List the runtimes available on that service before choosing a version:

```bash
assayflux runtimes --json
```

Example:

```bash
assayflux execute --provider piston --allow-external-execution \\
  --language python --version 3.12.0 --code 'print(6 * 7)'

assayflux execute --provider piston --allow-external-execution \\
  --language c++ --version 10.2.0 --filename main.cpp --code '#include <iostream>\nint main(){std::cout << 42;}'
```

Use a language and version returned by your instance's runtime list. The version above is illustrative, not a promise that a given runtime is installed.

## Code Interpreter service

The imported service is a separate FastAPI/Jupyter service. The adapter calls its `POST /execute` endpoint and parses the endpoint's newline-delimited JSON event stream. It does not embed the service inside the language core.

```bash
export ASSAYFLUX_CODE_INTERPRETER_URL=http://127.0.0.1:8000
# Optional; forwarded only as X-Access-Token:
export ASSAYFLUX_CODE_INTERPRETER_TOKEN=...
```

Run code in the service's default Python context:

```bash
assayflux execute --provider code-interpreter --allow-external-execution \\
  --code 'import math; print(math.sqrt(81))'
```

To select a supported language context, pass `--language`. To reuse an existing context, pass `--context-id`; these options are mutually exclusive. Contexts can retain variables and files between calls, so only reuse a context when that persistence is intended.

## Output and failure behavior

- Add `--json` to emit a structured result containing provider, language, version, stdout, stderr, exit status, and provider-specific output events.
- Source requests are limited to 1 MB; provider responses are bounded.
- The client caps its configured wait at 120 seconds. Piston also receives server-side run/compile limits; the imported Code Interpreter API does not accept a hard execution-time limit, so a client timeout does not guarantee that the remote kernel stops.
- Piston receives source as a named file, stdin, arguments, and the timeout limits.
- Credentials are read from environment variables and are never included in the structured result.
- The adapter never silently retries against another provider.

## Security and deployment

The explicit `--allow-external-execution` acknowledgement is required for every external execution command. It is a deliberate-use guard, not a sandbox.

Prefer a locally controlled Piston deployment or an HTTPS endpoint you trust. Review the deployment's isolation settings, network policy, resource limits, and runtime packages. Piston's own deployment may require Docker and cgroup support.

The Code Interpreter integration likewise depends on the deployment's sandbox, Jupyter kernels, filesystem policy, access-token validation, and network configuration. The imported server logs code and has a persistent default context; do not expose it to untrusted clients without adding authentication and isolation appropriate to your threat model. A local HTTP endpoint is intended for local development only.

These providers execute source code outside AssayFlux's bounded `.af` interpreter. Never pass untrusted code or secrets to a provider unless that provider's deployment is explicitly designed and reviewed for that workload. AssayFlux's client-side timeout and response-size checks are not substitutes for server-side CPU, memory, process, filesystem, and network restrictions.


## Optional quantum execution

The core exposes a validated, JSON-based circuit interface backed by PennyLane's local `default.qubit` simulator. Install the optional `quantum` extra on Python 3.12 or later; core installation remains independent of PennyLane. Example:

```bash
assayflux quantum devices
assayflux quantum run --circuit '{"wires": 2, "gates": [{"gate": "H", "wires": [0]}, {"gate": "CNOT", "wires": [0, 1]}], "shots": null}'
```

The adapter permits only a bounded set of gates, up to 16 wires and 1,000 gates, and up to 100,000 shots. It reports computational-basis probabilities. This initial integration is simulator-only; it does not claim hardware access or add quantum syntax to `.af`.

## Local diagnostic assistant

The optional assistant adapter uses a local Ollama HTTP API and never falls back to a cloud model. Configure `ASSAYFLUX_ASSISTANT_URL` (default `http://127.0.0.1:11434`) and `ASSAYFLUX_ASSISTANT_MODEL` (default `llama3.2`). Remote endpoints are rejected unless `ASSAYFLUX_ASSISTANT_ALLOW_REMOTE=1` is explicitly set after review.

```bash
assayflux assistant status
assayflux assistant diagnose --error 'SyntaxError: unexpected token' --context 'file.af, line 12'
```

The diagnostic output is advisory only. The assistant never applies patches or executes generated code. If the local model is unavailable, `diagnose` returns a deterministic fallback. Project NOMAD remains a separate imported application; this adapter uses its documented local-model ecosystem rather than assuming an unverified NOMAD route.
