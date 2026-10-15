# AssayFlux Interoperability and Web Technologies

## Design objective

AssayFlux is the orchestration language. Its Python implementation owns parsing, validation, values, execution context, diagnostics, and the common adapter API. It can delegate specialized work to other runtimes through registered adapters. An adapter does not make a runtime available by itself, and it does not sandbox untrusted code.

## Language and technology categories

- **Core interpreter:** AssayFlux source (`.af`) is lexed, parsed into an AST, then interpreted.
- **Python integration:** Python modules can be imported where permitted by the host environment. This is powerful and executes with the host process's permissions.
- **External language runtimes:** C, C++, C#, COBOL, Crystal, D, Dart, Elixir, Erlang, Fortran, F#, Go, Haskell, Java, JavaScript, Julia, Kotlin, Lua, Nim, OCaml, Perl, PHP, R, Ruby, Rust, Scala, Swift, TypeScript, Zig, and other languages must be treated as separate runtime integrations. Runtime installation, adapter implementation, passing tests, and supported status are distinct states.
- **Web technologies:** HTML describes document structure; CSS describes presentation; JavaScript provides browser-side behavior. HTML and CSS are not standalone general-purpose interpreter targets. AssayFlux should manage them as web assets and use a browser/WebView or web server to render them. JavaScript can be delegated to a JavaScript runtime or run by the browser.
- **Data systems:** SQL requires a configured database driver/connection and parameterized queries. A registered adapter alone does not provide a database.

## Recommended stable adapter contract

Every external execution adapter should report a canonical identifier, runtime availability, version/capabilities where known, and execute source with a timeout. Results should normalize stdout, stderr, exit status, duration, and structured diagnostics. Adapters should declare whether they execute source, compile it, call an API, or render an asset. Never infer production support from a filename or registry entry alone.

## Recommended project layout for web assets

```text
my_project/
  main.af
  web/
    index.html
    styles.css
    app.js
  assets/
```

The project runner should resolve assets relative to an explicit project root, reject path traversal outside that root, and offer a browser/WebView preview. Keep HTML and CSS as their native source formats rather than pretending they are Python modules.

## Security boundaries

The interpreter and adapters are not security sandboxes. Python imports and external programs can read files, access networks, and execute arbitrary commands with the process's permissions. For untrusted code, use an isolated process/container or OS sandbox with resource limits, restricted filesystem/network access, and explicit permissions. Do not execute untrusted code in a privileged server process.

## Implementation status policy

For each integration track these separately:

1. `planned` — interface/design only.
2. `adapter_present` — adapter code exists.
3. `runtime_available` — required runtime is found on this machine.
4. `tested` — automated integration tests pass for the documented behavior.
5. `supported` — maintained, versioned, documented, and tested in CI or a defined compatibility matrix.

Do not advertise all 30+ adapters as production-ready merely because adapter files exist.
