# Original-source compiler diagnostics

Date: 2026-11-22. Scope: compiler tooling and diagnostic provenance. The Rust
frontend, STD pin, runtime, grammar and normative rules are unchanged.

`check`, `check --watch` and normal `build` now print original filenames, line and
column, source excerpts and carets. Rule messages describe the relevant invariant;
unsupported constructs have a separate compiler-limitation message. Manifest and
input failures identify their path. Parser failures crossing a file boundary
identify the unclosed declaration in its original file.

A bounded diagnostic context copies original source text and paths. Per-byte maps
compose through linking, configuration, generic specialization and callable
rewrites, including helper insertion. Synthesized gaps carry approximate anchors,
which are explicitly labeled; fallback context does not claim an exact location.
The context resets on each watch pass. Rendering and bounded map storage use a
private native C boundary; this is not a new public runtime API.

[Recorded observations](DIAGNOSTICS_RESULTS.json).

## Validation

- Thirteen diagnostic observations cover type/move/syntax/lex failures, unclosed
  declarations, generics, closures, unresolved imports, imported source, watch
  recovery, normal build, manifests and unchanged numeric machine output.
- Thirteen existing package checks and seven file/watch observations pass.
- Host execution: macOS ARM64. This change has not received fresh Linux or Windows
  execution validation; Windows ARM64 execution remains deferred.
- No broad corpus, adversarial campaign or language-rule changes.

Reproduce with `scripts/validate_diagnostics.py --compiler PATH`,
`scripts/validate_package_check.py --compiler PATH --out RESULTS` and
`scripts/validate_file_watch.py --compiler PATH --out RESULTS`.

Rule messages do not yet include expected/actual type descriptions or secondary
borrow-origin labels. Columns count Unicode code points with tab expansion, not
full terminal display width. This does not implement an IDE/LSP diagnostic service.
Historical numeric-output descriptions in earlier cycle reports are superseded
for user-facing commands by this report.
