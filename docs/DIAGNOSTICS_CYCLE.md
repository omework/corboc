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

- Sixteen diagnostic observations cover type/move/syntax/lex failures, unclosed
  declarations, generics, closures, unresolved imports, imported source, watch
  recovery, normal build, manifests and unchanged numeric machine output.
- Thirteen existing package checks and seven file/watch observations pass.
- Host execution: macOS ARM64. This change has not received fresh Linux or Windows
  execution validation; Windows ARM64 execution remains deferred.
- No broad corpus, adversarial campaign or language-rule changes.

Reproduce with `scripts/validate_diagnostics.py --compiler PATH`,
`scripts/validate_package_check.py --compiler PATH --out RESULTS` and
`scripts/validate_file_watch.py --compiler PATH --out RESULTS`.

Expected/actual type descriptions and secondary move/borrow labels were added
in the subsequent [semantic diagnostic cycle](SEMANTIC_DIAGNOSTICS_CYCLE.md).
Columns count Unicode code points with tab expansion, not
full terminal display width. This does not implement an IDE/LSP diagnostic service.
Historical numeric-output descriptions in earlier cycle reports are superseded
for user-facing commands by this report.

## Parser context follow-up

The parser now records an expected-syntax reason alongside its farthest failure.
Common block/binding failures explain the required token or binding, rather than
only reporting invalid syntax. An expression-statement failure originating at
`for` explains that `for ... in` is absent from the current grammar and suggests
`while`/explicit `next()`. This is diagnostic classification after parsing fails:
no keyword is reserved and no grammar or accepted program is changed.

Sixteen focused diagnostic observations pass on macOS ARM64, including the new
loop, initializer and separator explanations. Checking the actual SubDB source
now identifies line 49 column 9 (`for`), rather than column 13 (`slot`). A valid
function named `for` still checks successfully. No SubDB source was modified.

## Iteration follow-up

The later for-loop implementation supersedes the unsupported-loop diagnostic
above. Valid for headers are now parsed; a malformed header reports the missing
`in` token. Reference-method arity failures identify the method name and explain
that the intrinsic takes no arguments.
