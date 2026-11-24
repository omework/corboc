# Omitted bounds on an existing slice

Scope: compiler/core implementation, not a grammar, STD API or rule change.

## Defect and correction

`bind_slice` rejected a slice reborrow unless both bounds were written explicitly.
The backend duplicated that restriction, and its omitted-end expression was only
prepared for fixed arrays. Thus `&mut buf[..]` failed while
`&mut buf[0..buf.len()]` passed. Site 361 incorrectly classified that compiler
restriction as N1 and could attach the enclosing receiver's name.

The checker now accepts omitted bounds on existing slices. Lowering uses zero
for an absent start and the source descriptor's `.len` for an absent end. The
existing checked runtime range and descriptor data pointer are reused. Bounds
are still evaluated once, and explicit checks reject reversed/out-of-range
intervals. Mutable permission, retained target/parent-loan edges, last-use
release and overlapping-loan checks are unchanged. Site 361 is retired without
renumbering other diagnostic identities.

## Focused observations

Runner: `scripts/validate_slice_reborrow.py`.

- Full, prefix, suffix, nested shared and empty slice reborrows, with writes and
  successive mutable loans.
- The reported async method pattern: `if let Some(offset)` followed by returning
  `self.file.read_at(&mut buf[..], offset).await`, using a real two-byte file.
- A runtime out-of-range start with an omitted end.
- Rejection of a mutable reborrow from a shared slice.
- Rejection of overlapping active mutable slice reborrows.

All five observations pass. Positive programs execute with fatal UBSan; the
out-of-bounds program takes the existing runtime range-error path, and both
permission/overlap negatives produce N5. Four directly related compound-await
and explicit-slice-argument regressions also pass. The diagnostic-site audit
passes with 1,019 catalog entries (site 361 retired) and 353 observed state writes.

Installed at `build/check-file/install/bin/corboc` with SHA-256
`da13f965aac2fd591a4e2f83e035274ba5dfa7c8e18eef536d332948ca5de7a0`. Results: `build/slice-reborrow/results.json` and
`build/slice-reborrow/compound-regressions.json`.
No broad rule-breaking campaign, frozen Rust frontend change or platform API
change is included. Execution is on macOS ARM64; Windows ARM64 remains deferred.
SubDB source is unchanged. The focused File witness has a valid offset provider;
it does not assert that every remaining WAL method compiles.
