# Runtime metrics integration

The new public API is supplied by `stdlib/src/runtime/metrics/metrics.crb` in the
language checkout: `runtime::metrics::memory_stats() -> MemoryStats`, with reserved,
committed and occupied byte accessors. It is an ordinary package/type, not a new
parser primitive. Namespace discovery mounts the STD's runtime subtree under
`runtime::`; existing module/type/contract resolution handles its declarations.

Fixed datastacks are thread-local execution contexts, while region bands can be
shared. Five atomic counters aggregate reserved mappings, committed pages, fixed
cursor spans, live region payloads and unused pool slots. Snapshot reads never
inspect another thread's mutable descriptors. Fields are independent samples;
there is no global sampling lock or implied lifetime/synchronization effect.

Generated cursor rewinds call the runtime accounting entry point after cleanup.
Its pool chain retires unused-slot facts before their fixed storage is reused.
Suspended contexts preserve their chain without charging restored storage twice.
Runtime policy is implemented in Corbo and mirrored by the C reference; atomics
remain typed native primitives. The added pool/context fields require matching
C header/runtime version 2. Runtime resources are generated through the supported
script, never edited as byte arrays.

## Focused evidence

The development compiler is `build/memory-metrics/corboc`. The language checkout's
`scripts/validate_runtime_metrics.py` executes:

- Eight Corbo observations: qualified/grouped API imports, fixed reservations,
  pool claim/drop and scope rewind, vector growth/pop and async suspension.
- One exact-accounting C ABI witness against each runtime implementation, with
  fatal UBSan. It checks reclamation, slot deltas and final zero counters, and
  samples concurrently while three workers perform 30,000 total claim/drop cycles.
  C-owned global initialization/shutdown configuration is serialized; allocation
  loops and snapshot reads run concurrently.

The API observations additionally execute on macOS x86-64, Linux x86-64 (container)
and Windows x86-64 (Wine); Windows ARM64 compiles only. Host is macOS ARM64.
Results live in `corbo-lang/validation/runtime_metrics/`. The source documentation
checker passes for STD/runtime declarations. No broad legacy suite, mutation
campaign, TSan run, performance benchmark or general concurrency proof is claimed.

## Scope and development sources

Counters exclude OS thread stacks, registers/native locals, foreign allocations
and separately mapped scheduler/reactor metadata. Occupancy includes fixed cursor
alignment/bookkeeping but subtracts unused pool payload slots. Committed bytes are
not process RSS. Quiescent comparisons are exact within this accounting model;
concurrent cross-field comparisons are not guaranteed.

The installed release binary and frozen Rust frontend are unchanged. During
implementation the runtime-source override selected working-tree sources. The
published `corbo.lock` now pins Corbo revision `13aa9b6306ddb4e878976d7e86be243a10285894`;
source-lock and runtime regeneration checks use that exact committed revision.
