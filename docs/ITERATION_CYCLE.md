# Universal reference spelling and for loops

Scope: compiler/core and grammar. Rust frontend, STD code, runtime and pinned
revision are unchanged. Language grammar and docs are updated in corbo-lang.

## Implementation

- Zero-argument `.ref()` / `.mut_ref()` are type-independent spellings of the
  existing borrow operators, normalized before ordinary method dispatch.
  Explicit reference levels, mutation permission and lifetime checks are retained.
- `for [mut] name in expression { ... }` has an explicit AST node (95) carrying
  source and body. Binding mutability is read from the original token prefix;
  visibility is not reused for it. `for` and `in` are keywords.
- One normalizer pass replaces one construct, composes source provenance and
  visibility offsets, and reparses before further specialization or verification.
  Borrow spelling is grouped only where postfix precedence requires it.
- Indexed sources capture their storage/view and initial length once. The cursor
  advances before the body, so `continue` cannot repeat the current item. Existing
  slice projection and bounds checks apply. Owned arrays use ordinary element
  move/copy rules; borrowed arrays and slices yield references.
- Other iterator objects use `next() -> Option<T>`, with the result retained in
  an ordinary binding before match. The source, result and payload are cleaned
  through existing scopes and ownership planning. Generated names are checked
  against source identifiers to avoid capture and shadowing.
- Fixed-array length calls are routed as expressions rather than pool creation.
  Enum borrows and mutable record-slice elements reuse existing reference/root
  tracking. Slice ranges remain in bind_slice, before element projection handling.
- Leading control/block statements terminate before a following dereference
  statement, avoiding accidental multiplication with an if expression.

These forms introduce no implicit mutable borrowing, new allocation strategy,
trait or unchecked iteration path. They do not relax existing restrictions on
moving elements/fields out of borrowed storage, or grant operations on a type
that its underlying borrow/index/next operations do not support.

## Executed validation

Host: macOS ARM64.

Five compiled and executed programs cover primitive and record borrows, indexed
mutation/shared reads, continue/break, by-value primitive arrays, identifier
hygiene, a next-based iterator factory evaluated once, mutable loop bindings,
aggregate fields, nested iteration, slices, an empty source and cleanup after an
early break. Five refusals cover mutation permission, dangling references,
reference levels, intrinsic arity and use of a moved iterator.

Sixteen focused diagnostic regressions pass, including original-source mapping,
malformed for headers, imports, generics, closures, watch recovery, normal build
errors and the raw frontend protocol. No broad corpus or safety campaign ran.
Fresh Linux/Windows execution was not performed for this platform-independent
syntax change; Windows ARM64 execution remains deferred.

[Recorded observations](ITERATION_RESULTS.json).

Reproduce with `scripts/validate_iteration.py --compiler PATH` and
`scripts/validate_diagnostics.py --compiler PATH`. The final source was rebuilt using the new compiler generation and the ten
focused observations passed again on that binary. The existing PATH installation
at `build/check-file/install/bin/corboc` was updated atomically; a mutable/shared
loop source passes its installed check. No three-generation byte-identity or
broad parity validation was requested or run.

## Publication pin

`corbo.lock` now pins Corbo `e0a6fc8b8d8c9996916cc10f45bc6c28e5bc7011`. The pinned-source
check and runtime bridge check passed. STD/runtime code is identical to the
revision used for the recorded executable validations; this commit updates the
grammar and documentation. The build record above retains its actual validation
revision rather than presenting it as a rebuild against the new pin.
