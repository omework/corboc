# Thread transfer eligibility

User-approved core/grammar extension: `#(thread: transfer=false)` opts a nominal
struct or enum out of moves between threads. Absence means eligible unless owned
components propagate a restriction. Same-thread moves remain valid. The annotation
is independent of N4 validity, N5 synchronization and branch completion.

## Representation and integration

The parser stores `thread` metadata and its `transfer=false` property. Declaration
metadata is excluded from layout/signature field lists but retained by raw AST
ownership and generic rendering. A separate monotone fact table maps concrete
nodes to the originating restriction annotation. Owned types, fields, aggregate
values, bindings, assignments, projections and generated closure capture records
propagate those facts. Shared/reference annotations stop owned-field propagation;
this feature does not introduce a Sync-like reference classification.

Async summaries combine owned parameters, output types, nested awaited state and
locals retained across suspension. Lexical scope exit or an explicit preceding
drop can discharge a local's retained state. Native worker blocks additionally
inspect external capture bindings. Native thread, spawn, spawn_blocking and
functions/methods carrying branch contracts check arguments/state and results.
A restricted resource wholly created and destroyed in one worker remains allowed.
No lock acquisition, runtime thread identity check or type-name privilege is added.

## Focused executed evidence

Run `python3 scripts/validate_thread_transfer.py` with development compiler
`build/thread-transfer/corboc`. Its source was built by `build/object-lock/corboc`
using the existing pinned STD/runtime (`c8bbadf15094f0d297c68fffcab4693cffbc8102`).
Language working-tree specification changes add TR1; no STD/runtime implementation
change or lock update is needed for this development build.

Five accepted fixtures execute at O1 with fatal UBSan:

- Ordinary moves and synchronous consumption of a marked object (42).
- A local closure owning a marked capture (42).
- A restricted resource created wholly inside a worker (true).
- An unmarked owned record moved to a worker (true).
- A local destroyed at lexical block exit before async suspension (42, true).

Fourteen invalid fixtures reject with transfer rule 8 or malformed-metadata rule 1:
direct, nested-field, selected-field, array and generic-wrapper moves; closure
captures; async owned captures, retained local state, nested await and output;
worker output; duplicate annotation and function placement. Results are retained
in `validation/thread-transfer-results.json`.

The existing object-lock suite also passes: six fatal-UBSan executions and ten
refusals, including the real-lock three-thread witness. Results are retained in
`validation/thread-transfer-lock-regressions.json`.

## Limits

This is focused functional validation, not an independent safety audit or a
mutation campaign. Summaries conservatively union possible owned paths and
payloads. Complex destructuring and unresolved projections may retain a broader
restriction rather than proving a narrower component eligible. Suspension liveness
uses lexical scope and explicit drop facts; it can conservatively retain a
restriction after more complex move/cleanup paths. Nominal projection tracing is
bounded to 64 steps and unresolved projections retain the owner restriction.
Foreign/unchecked implementations remain developer-owned.

No target runtime, assembly backend or ABI changed. Native execution above is
macOS ARM64; cross-platform runtime suites were not replayed for this static
analysis change. Windows ARM64 execution remains deferred. The frozen Rust
frontend and installed release binary are unchanged.

## Self-hosting check

The development compiler emits its own package successfully, producing 14,495,342
bytes in 25.46 seconds, identical to the seed-built C at that point. The final
projection and signature-mode guards are subsequently rebuilt and checked against
the focused fixtures.

## Publication pin

`corbo.lock` now pins committed Corbo revision `2fe441daa495175c8e098a9376d4b4f8e5e9e662`.
The source-lock and generated-runtime checks use that exact revision.
