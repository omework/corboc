# Synchronous defaults and shared-reference mutexes

Date: 2026-11-21. Scope: STD/API organization, runtime integration and the
specific general compiler mechanisms exposed by these APIs. Rust frontend frozen.

## Delivered

- Restore synchronous `std::io`, `std::net::{tcp, udp, tls}` and `std::time`.
  Async variants live under the corresponding `asyn` namespaces. Shared options,
  addresses and monotonic values retain their common packages. No legacy
  `::sync` aliases and no new async TLS transport.
- Add ordinary generic `std::Mutex<T>` and `std::asyn::Mutex<T>`, both acquired
  through `lock(&self)`. Guards expose `get()` / `get_mut()` and unlock on drop.
  Sync guards carry the normal `#(thread: transfer=false)` annotation.
- Implement trusted interior mutation inside `@unchecked`; the mutable borrow
  retains its target, provenance and lifetime graph. Native locking remains
  implementation-owned, and the checked spelling is still refused.
- Implement stable OS-backed lock metadata, native-thread sync ownership and
  FIFO async task ownership, parking, root wakeup, handoff and waiter cleanup
  in the Corbo runtime, with a matching retained C reference implementation.
  Async acquisition does not spin or occupy a blocking worker.
- Keep raw mutex create/wait/release bindings private to the STD; checked
  callers cannot import the resource-identity bridge.
- Preserve opaque layouts across generic specialization using an original
  package-file identity. `LayoutVisibility.origin` and `StaticNode.private_origin`
  describe lexical visibility, not value provenance or ownership. A sparse
  specialization-origin map records which file authored each generated impl;
  implementing a public STD type does not confer private-field access. Private
  declaration ranges exclude foreign implementations. Sibling STD
  implementations can construct their guards without exposing fields to users.
- Reuse general per-field result/capture summaries for async record results,
  shared record parameters and stored-reference forwarding. Accept record
  literals as ordinary owned constructor arguments. No Mutex-name checking rule.
- Fix final compound/indexed assignments skipping automatic scope cleanup.
  The three-thread witness initially stalled because the first guard was not
  destroyed; the corrected exits release it before stack reclamation.
- Align the linker's edit workspace with its existing 4 MiB input budget.
- Update compiler loading/scaffolding imports, EN/FR README examples, active
  guides and generated STD/runtime references. Keep historical cycle reports.

## Executed evidence

- Three public programs under fatal UBSan on macOS ARM64: scalar guards and a
  same-thread guard move (`42, 42`); three native threads and three contending
  async writers (`3, 4`), including both fixed cleanup exits; aggregate payload
  mutation and once-only destruction (`41, 99, 99, 41`). Async guards survive yield.
- The same three generated programs execute with matching output on Linux
  x86-64 (Docker), macOS x86-64 and Windows x86-64 (Wine). Windows ARM64 builds;
  execution remains deferred by the existing user decision.
- Ten refusal programs cover same-object re-entry, owner/guard destruction
  with live dependents, native guard transfer, native guard retained across
  suspension, concurrent mutable sharing of a guard, private guard construction, external-implementation field access, private
  raw-helper import, and attempted checked interior mutation. The last is conservatively unsupported;
  the others are rejected with rule, contract or import-visibility diagnostics.
- One independent C witness runs against both runtime implementations: 3,000
  contended native writes, FIFO queueing, removal of an interior waiter, dropped
  handoff forwarding, re-acquisition and async unlock by another native thread.
  Both execute on macOS ARM64 with fatal UBSan, macOS x86-64 with fatal UBSan,
  Linux x86-64 and Windows x86-64. Both compile for Windows ARM64.
- The cross-target witness uses always-evaluated CHECK operations: standard
  assert expressions were disabled by that toolchain, skipping operations in
  the original harness. Corrected the harness and reran all targets.
- Six changed README packages execute under fatal UBSan: file, async_file,
  buffered, network, time and async_time.
- Async buffered File round trips pass at O0/O2, with five retained refusal
  checks and three sequential-write acceptances under current N5. These three
  former uniqueness expectations were updated; conservative refusals are not
  presented as normative bans. Async buffered TCP passes against an independent
  loopback peer at O0/O2.
- Existing runtime metrics regression passes: Corbo API, retained C memory ABI
  and Corbo memory ABI, each under fatal UBSan. Generated runtime bridge matches
  readable sources. STD/runtime documentation inventory checks pass.
- Rebuilt and installed corboc from the modified sources against STD revision
  `57313769e0f0cdc76804f903d75de64f314ceed7`. The installed compiler
  resolves its bundled STD automatically, builds the mutex example through
  normal `corboc build`, and the executable prints `42, 42`. This was one
  reconstruction, not a multi-generation bootstrap equivalence check.

## Reproduction

From the language checkout:

```sh
python3 scripts/validate_mutex_runtime.py --compiler ../corboc/build/asyn-mutex/corboc
python3 validation/check_rust_buffered_io.py --async --corboc ../corboc/build/asyn-mutex/corboc
python3 validation/check_rust_buffered_io.py --tcp --async --corboc ../corboc/build/asyn-mutex/corboc
python3 scripts/validate_runtime_metrics.py --compiler ../corboc/build/asyn-mutex/corboc
python3 scripts/stdlib_docs.py --check
```

From the compiler checkout:

```sh
python3 scripts/validate_mutex.py --compiler build/asyn-mutex/corboc
python3 scripts/runtime_sources.py --compiler build/asyn-mutex/corboc --check
```

For cross-target queue checks, compile the validator's `corbo.c` and
`c-reference.c` with `zig cc -target x86_64-linux-gnu -pthread -O1` or
`-target x86_64-windows-gnu`, then execute using Docker/Wine. Use
`-target aarch64-windows-gnu` for the deferred-execution build. For public APIs,
use the three C artifacts emitted by `validate_mutex.py` with the same commands.

## Limits

These focused checks establish the reported executions and rejections, not a
proof of memory safety. No full compiler corpus or new adversarial campaign was
run. Linux uses Docker and Windows x86-64 uses Wine, not physical Windows.
Windows ARM64 execution remains deferred. Raw native calls and trusted interior
mutation rely on implementation correctness; annotation checking does not
verify OS synchronization. Existing conservative verifier limits remain.
