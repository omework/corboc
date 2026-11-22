# Committed compiler rebuild — 2026-11-23

This release groups semantic source diagnostics, tuple projections and tuple
patterns in for loops. Author and committer: Jabar.

The shared-source pin advances to `834c1d5e04d37eec0bfbd9fb8aecefc55fae7fbe` for the committed grammar and
language documentation. STD and runtime code are identical to the previous pin.
The focused validation evidence remains in SEMANTIC_DIAGNOSTICS_CYCLE.md and
TUPLE_ITERATION_CYCLE.md. Compiler code from `a3ec17f` was rebuilt locally using the preceding installed
self-hosted compiler. The resulting binary atomically replaces
`build/check-file/install/bin/corboc`, which the user's interactive zsh resolves
as `corboc`. The installed shared-source lock is updated to the same committed
pin.

A separate package passes `corboc check`, builds through the installed
`corboc build`, and its executable prints `3` and `7` after mutable tuple-pattern
iteration. Runtime source consistency and both working-tree whitespace checks
pass. This is a focused macOS ARM64 installation check; it does not repeat the
previous corpus or cross-platform validation.

[Build and smoke evidence](COMMIT_BUILD_2026_11_23.json).
