# Offline reference and local documentation server

Scope: documentation/build tooling and a Corbo CLI server; no grammar or language-rule changes.

The build bundles a searchable static HTML reference with STD declarations, compiler-owned types and operations, runtime internals, C ABI, source links and feature examples. Internal/private declarations are labeled. Compiler-owned APIs are maintained in BUILTIN_REFERENCE.json; source-defined APIs use existing documentation comments. The default appearance is black/charcoal with restrained accents.

`corboc doc` serves the bundled snapshot on loopback and opens the browser. `--no-open` disables opening; `--port` selects a port (zero chooses an available port). The installed command needs no Python or network assets. Ctrl+C stops the server. The server is written in Corbo; browser launching uses small platform helpers.

## Executed validation

- Candidate rebuilt from current Corbo compiler sources.
- 521 HTML pages; 94,150 local links and 2,181 search entries resolve.
- Compiler-managed primitive, collection and task families are included.
- Actual HTTP assets match the generated files; HEAD, partial requests, malformed paths, missing files, unsupported methods and invalid CLI arguments pass.
- Isolated headless Chrome exercised search, keyboard selection, desktop/mobile layout and a collection type page; no horizontal overflow observed.
- Existing SubDB WAL file check passes with the candidate.
- The generated-source receiver lookup now bounds-checks metadata before treating it as an AST node ID. This removes a crash encountered while integrating the server.

Evidence: [machine-readable results](OFFLINE_REFERENCE_RESULTS.json). Host execution: macOS ARM64. Linux/Windows browser helpers are implemented but not executed in this cycle; Windows ARM64 remains deferred. No broad language-safety claim or full-platform validation is made.

The bundled STD remains pinned to ccbeff271605a7a7c3b35d9105c41c2dd07031c2. Uncommitted language-guide edits will enter the bundled snapshot after publication and a deliberate pin update. No commit or push was requested for this cycle.

## Publication

Corbo documentation and grammar are committed at `6007d05366476a31f9c4ba99c8d6ab55becaf77c`. The compiler lock now pins that revision. STD and runtime source code are unchanged by this documentation/grammar revision; the executable observations above remain those actually recorded before publication.

The published-snapshot refresh passes the local HTTP checks and resolves 94,257 links across 522 HTML pages and 2,182 search entries. `OFFLINE_REFERENCE_RESULTS.json` records that refreshed run.
