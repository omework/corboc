# Pool constructors and recoverable allocation

## Scope

Core/parser integration: `Pool<T>::new(capacity)` replaces the lowercase
contextual constructor. STD/API: `pool.try(...) -> Result<A<T>, PoolError>`
adds recoverable slot exhaustion while `new` remains fail-fast. Runtime changes
only factor the existing atomic slot claim into a boolean-returning operation;
no platform allocation backend or capacity policy changes.

## Implemented

- Normal qualified generic constructor syntax, including STD import aliases.
- `try(value)`, contextual `try({ fields })`, `try({})` and `try()`.
- `PoolError.Full` is an ordinary root STD enum; enum pools exhaust per arm.
- Initializers evaluate once before claiming a slot. A supplied value moves on
  either outcome and is destroyed exactly once on failure. Successful Results
  retain allocation cleanup and source-pool/field dependency summaries.
- Owned Result payload extraction, explicit Result return construction and `?`
  preserve allocation metadata rather than treating the descriptor as a scalar.
- Both readable Corbo and reference C runtimes use the same slot-claim behavior.
- Active STD declarations, README/current examples, fixture packages, grammar,
  IDE names and current compiler validation sources use the new notation.
  Recorded top-level historical corpora, cycle reports and frozen compilers
  retain their original inputs; they are not newly validated evidence.

## Executed evidence

macOS ARM64, host C compiler, optimized O1 with fatal UBSan:

- Nine accepted programs: scalar exhaustion/reuse, nominal shorthand, custom
  destruction on failed/successful attempts, exactly-once initializer, per-arm
  enum capacity, Result/`?` forwarding, vector allocation, borrowed fields and
  default initialization.
- Nine expected refusals: old notation, missing `::new`, zero capacity,
  immutable source pool, wrong initializer type, use after move, early source
  pool destruction, early borrowed-target destruction and local-pool escape.
- STD Pool/PoolError aliases and the migrated README pool package execute:
  eleven successful UBSan programs plus nine expected refusals in total.
- A C-reference harness checks success, full without changing output, release
  and subsequent slot reuse under fatal UBSan.
- The rebuilt compiler emits itself successfully. Its next generation emits
  byte-identical C (stage2/stage3); the initial generation differs as expected
  because it used the previous runtime in the bootstrap executable.
- Generated references check 92 STD files / 1,465 documented declarations and
  members, and 32 runtime files / 777 declarations and members.
- Runtime resource freshness passes against the explicit development runtime.
- `build/pool-api/bin/corboc build build/pool-api-validation/alias -o /tmp/pool-build-alias` discovers its bundled development STD; the executable prints 42.

Reproduce the focused pool cases in the corboc checkout:

```sh
python3 validation/check_pool_api.py \
  --corboc build/pool-api/bin/corboc \
  --stdlib-dir ../corbo-lang/stdlib/src \
  --keep build/pool-api-validation
python3 scripts/runtime_sources.py --check \
  --compiler build/pool-api/bin/corboc \
  --runtime-source ../corbo-lang/runtime
```

## Limits and observed discrepancy

- Capacity remains a positive integer literal, as before; arbitrary capacity
  expressions are not added by this syntax change.
- Owned Result call-summary integration currently supports a single borrowed
  pool formal. More complex function signatures returning owned Result payloads
  can still be refused as unsupported. Direct try initializers retain the
  existing initializer/dependency support of pool.new.
- A standalone raw source using try needs a compatible PoolError declaration;
  package programs should import `std::PoolError` (aliases are supported).
- `examples/features/iter` refuses its `iter(&mut counter)` call with N1 in both
  the baseline compiler (offset 496, old syntax) and candidate (offset 501, new
  syntax). This is pre-existing and outside this pool change; no passing iterator
  regression is claimed.
- No Linux/Windows execution or independent adversarial audit was performed.
  Windows ARM64 remains deferred. This evidence is not a general safety proof.
- Publication pins STD/runtime revision `600b409a0edae3112fd0dd68e246cd0798a0a666` in
  corbo.lock. The clean dependency cache was checked with
  `python3 scripts/corbo_sources.py --check`; embedded runtime freshness passed
  with `python3 scripts/runtime_sources.py --check --compiler build/pool-api/bin/corboc`
  against the pinned cache, without a development override. The functional
  evidence above uses the development compiler in build/pool-api; build/install
  was not replaced during this commit/push step.
