# General reference methods and wrapper dereferencing

## Scope and implementation

This is an approved API change plus a core resolution change. Both STD
MutexGuard variants replace `get`/`get_mut` with `ref`/`mut_ref`. A<T>'s helpers
borrow its stored T; explicit `&allocation` still borrows the handle.

The compiler looks up actual instance declarations before applying universal
reference shorthand. Nominal dereferencing is normalized into an ordinary
method call followed by native dereferencing: reads use ref, mutable place
consumers use mut_ref. The method pair exposes one target type, takes no extra
arguments and returns the corresponding reference mode. Assignments, compound
assignments, explicit mutable borrows and mutable method receivers select the
mutable mode. Native references and A<T> retain their native dereference path.
There is no MutexGuard name check, new lock primitive or alternate dependency
graph. Ordinary call, receiver permission, borrowed-place and lifetime checks
remain responsible for validation and lowering. The source map follows each rewrite. Expression-local bindings materialize the
method result once, preserving argument order and short-circuit boundaries.
The existing lexer is now shared by frontend parsing and expression-block
verification; its tokenization logic is unchanged. Both invoke the same scope
checker. Local reference aliases are reduced at scope handoffs while the actual
referent and surviving parent reservations remain tracked.

Method lookup/inference also retains the nominal output of an awaited async
function instead of treating its generic argument as the output. Allocation
reference lookup uses the existing A/Pool primitive syntax and annotations.
The generic helpers alone do not grant dereferenceability to a nominal object.

## Validation plan and boundaries

Run focused custom-wrapper, generic-wrapper, native-reference, A<T> and
sync/async guard programs under fatal UBSan. Check mutation permission,
malformed method signatures, missing declared methods, lifetime escape and
moving an owned payload out of borrowed storage. Reuse the existing public
mutex API/threads/aggregate tests and directly related refusals, after migrating
their method spelling. Audit diagnostic-site coverage and regenerate the STD
reference. Rebuild and install corboc at the existing shell PATH.

This change does not alter OS synchronization or runtime source. Execution
coverage is host macOS ARM64; it does not claim a replay of all platforms.
Windows ARM64 execution remains deferred. Focused passing checks are not a
proof of general memory safety.

## Executed evidence

`scripts/validate_reference_methods.py` passes 14 focused cases: six executable
programs under fatal UBSan and eight refusals. Executions cover a custom wrapper
with field writes, compound writes, a mutable method receiver and escaping
reborrows; two generic specializations; scalar/struct A<T> payload references;
native references/arrays; both guard variants; and a single witness for operand
evaluation count, left-to-right arguments, short-circuiting and temporary cleanup.
An enum with an incompatible declared ref method is rejected by the same
signature-resolution mechanism. The suite does not count unsupported borrowed
moves as demonstrated normative diagnostics.

The existing mutex suite passes three executable programs under fatal UBSan and
ten refusal fixtures, including captured guard aliases. The diagnostic-site
history audit passes; semantic diagnostic regressions pass 13 observations and
category/parser regressions pass nine observations with raw-protocol comparisons.
The generated STD documentation check passes for 103 STD files / 1,689 declarations
and 41 runtime files / 921 declarations. Runtime source is unchanged.

Evidence is recorded in `docs/REFERENCE_METHODS_RESULTS.json`; reproducible runs:

```sh
python3 scripts/validate_reference_methods.py --compiler /path/to/corboc --stdlib /path/to/corbo-lang/stdlib/src
python3 scripts/validate_mutex.py --compiler /path/to/corboc --stdlib /path/to/corbo-lang/stdlib/src
```

## Existing limits observed while scoping the witnesses

Nominal allocation-handle borrows such as `&A<Point>` parameters and some methods
returning borrowed enum payloads through match are still rejected by existing
compiler paths. They are distinct from borrowing the stored Point with ref or
mut_ref, which is executed here. No claim of positive enum-payload-return or
all ownership compositions is made. These observations were not turned into a
separate language-arbitration or adversarial campaign.

## Installation

The compiler rebuilds itself with the committed STD pin and no development
override. All 14 focused observations pass again on that final rebuilt binary.
The lexer extraction was checked to have identical function bodies. The final
binary and updated STD are installed at the existing location. The shell
PATH remains `/Users/jabarkarim/sources/corboc/build/check-file/install/bin`.
Existing watch processes must be restarted after replacement.
