ASSAYFLUX REPAIR PATCH

This patch restores two files from the known-good AssayFlux v0.2.0 source archive:
- assayflux/lexer.py
- assayflux/interop/adapters/perl_adapter.py

Why: the current replacement lexer broke the token interface expected by parser.py and the tests. The registry also imports perl_adapter.py, which is missing from the active repository.

GitHub Android instructions:
1. Download and extract this ZIP on your phone.
2. In your GitHub repository, open assayflux/lexer.py, tap Edit, select all, and replace it with the extracted lexer.py contents; commit.
3. Open assayflux/interop/adapters. Use Add file > Upload files and upload perl_adapter.py from the extracted folder; commit. If the file already exists, edit/replace it instead.
4. Open Actions and rerun AssayFlux Auto Run.

Validation against the included full source baseline: python -m compileall -q assayflux passed; pytest reported 96 passed, 81 subtests passed; hello, conditions, functions, loops and variables examples all executed successfully.