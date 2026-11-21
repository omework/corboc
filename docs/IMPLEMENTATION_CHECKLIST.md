## Positioned File API integration

- [x] Advance STD pin to the committed read_at/write_at implementation.
- [x] Existing corboc accepts sync/async API and refuses owner destruction with a pending read.
- [x] Record platform witnesses and Windows resource cleanup; ARM64 execution deferred.
- [x] Extend test-only target-emitter tooling with the ARM64 selector.

[Evidence](FILE_POSITIONED_CYCLE.md). No compiler/core implementation changes.

## Package check/watch CLI

- [x] Share package resolution and verifier-only mode; no code generation.
- [x] Watch source/manifest content with debounce and recovery after errors.
- [x] Execute focused package, dependency, error and watch tests on macOS ARM64.
- [x] Probe the native executable-location boundary on macOS/Linux/Windows x86-64.

[Evidence](PACKAGE_CHECK_CYCLE.md). Full cross-platform CLI runs were not repeated.

## Mutex API namespaces

- [x] Move Mutex/MutexGuard to `std::sync` and `std::sync::asyn`.
- [x] Update private compiler bindings, docs and examples.
- [x] Run three fatal-UBSan programs and ten existing refusal checks.

[Evidence](MUTEX_NAMESPACE_CYCLE.md). Runtime unchanged; platform results retained.

## Synchronous defaults and mutexes (current API convention)

- [x] Restore synchronous default packages and explicit asyn counterparts.
- [x] Add shared-reference sync/async mutex acquisition and scope-owned guards.
- [x] Preserve private generic layouts, result dependencies and transfer contracts.
- [x] Fix terminal assignment cleanup and validate native/async contention.
- [x] Run focused positive/refusal, buffered I/O and memory-ABI regressions.
- [x] Execute macOS ARM64/x86-64, Linux x86-64 and Windows x86-64 witnesses.
- [x] Compile Windows ARM64; execution remains explicitly deferred.
- [x] Update EN/FR guides, examples and generated references.

This supersedes the historical async-default API convention below.
[Evidence](SYNC_DEFAULT_MUTEX_CYCLE.md).

## Package scaffolding (CLI/build tooling)

- [x] Add corboc new with a minimal runnable package and no implicit Git initialization.
- [x] Validate names and refuse all existing destinations before file writes.
- [x] Execute ten focused CLI checks, including generated-package build/run.
- [x] Check native module boundaries on macOS/Linux/Windows; Windows ARM64 compile-only.
- [x] Update EN/FR language quick starts and compiler documentation.
- [x] Install the compiler with its pinned STD and run the same focused CLI checks.

[Evidence and limits](PACKAGE_NEW_CYCLE.md). No core/grammar change.

## Async-default APIs (API/STD organization)

- [x] Move async I/O/waits to default packages and blocking APIs under sync.
- [x] Keep shared options, metadata, addresses and time values common.
- [x] Migrate corboc imports/namespace metadata and compile the active compiler.
- [x] Update EN/FR READMEs, runnable examples, API guides and generated reference.
- [x] Execute affected File/buffered/network/timer regressions and TLS interop.
- [x] Complete targeted platform probes; Windows ARM64 remains compile-only.
- [x] Pin the committed async-default STD revision in corbo.lock.

No open language decision; no async TLS transport introduced. [Evidence](ASYNC_DEFAULT_API_CYCLE.md).

## Bounded strings, binary encoding and time (core + STD API)

- [x] Parse literal type arguments and specialize `String<N>` to fixed inline storage.
- [x] Preserve generic private layouts, returned text dependencies and nominal allocation borrows.
- [x] Implement explicit little/big-endian primitive conversion with caller buffers.
- [x] Implement monotonic Duration/Instant, blocking Timer and worker-backed async waits.
- [x] Execute nine functional programs under fatal UBSan and ten expected refusals.
- [x] Execute two directly related constant/generic regressions under fatal UBSan.
- [x] Execute binary/time and bounded-layout probes on supported host/target combinations.
- [x] Complete byte-identical stage2/stage3 compiler self-emission with the development STD.
- [x] Regenerate API references and document platform and publication limits.

No open language decision. Windows ARM64 execution remains deferred. The
STD pin now references the published lot; the matching development
bundle is retained. See [evidence and limits](BINARY_TIME_BOUNDED_CYCLE.md).

## Pool construction and recoverable allocation (core + STD API)

- [x] Parse `Pool<T>::new(capacity)`; reject the former constructor.
- [x] Implement `try` with `PoolError.Full`, exactly-once initialization and cleanup.
- [x] Preserve source-pool/field dependencies in stored/extracted owned Results.
- [x] Migrate active source examples, grammar, STD exports and API documentation.
- [x] Run 20 focused checks: 11 UBSan programs and nine expected refusals.
- [x] Check C-reference slot reuse and byte-identical self-reconstruction.
- [x] Record existing limits, the baseline iterator failure and platform scope.
- [x] Pin the committed STD/runtime revision and verify the clean cache and runtime resource freshness.

No open language decision. See [evidence and limits](POOL_CONSTRUCTION_TRY_CYCLE.md).

## Configurable constants and HTTP parsing (core + STD API)

- [x] Parse configurable constants and lexical override blocks.
- [x] Resolve/import aliases, visibility, types and duplicate targets.
- [x] Specialize helper calls and nominal layouts; preserve escaped configurations.
- [x] Implement bounded HTTP request/response heads and optional streaming bodies.
- [x] Preserve nested result and reader dependencies with existing value summaries.
- [x] Complete 37 focused checks: 25 UBSan executions and 12 expected refusals.
- [x] Reconstruct the optimized compiler with identical emitted C.
- [x] Regenerate/check API documentation and record scope/limits.
- [x] Pin the published STD, rebuild/install corboc and validate automatic STD discovery.

No open design decision. The published STD pin and untested platforms are
explicit in the [cycle report](CONFIGURATION_HTTP_CYCLE.md).

## Canonical corbo-lang repository (organization)

- [x] Point the language link and local checkout instructions to corbo-lang.
- [x] Pin its parentless initial snapshot in corbo.lock and update the clean dependency cache.
- [x] Verify the source lock and runtime resource freshness.
- [x] Complete the pinned install build with unchanged emitted C.
- [x] Build and run a package from the new checkout.
- [x] Record the [migration evidence and limits](CORBO_REPOSITORY_MIGRATION_CYCLE.md).

## Package-root build defaults (build/CLI)

- [x] Accept package-root build and optional explicit package paths.
- [x] Read optional [bin].name with a package-name fallback.
- [x] Create the default package-relative build directory and retain -o precedence.
- [x] Preserve module/dependency parsing and failed-build publication behavior.
- [x] Complete the compiler development build and 18 focused checks.
- [x] Pin the published specification, complete the final install build and execute the actual README command.
- [x] Update both READMEs and the [cycle report](PACKAGE_BUILD_DEFAULTS_CYCLE.md).

No open design decision. Native build driver support remains macOS ARM64 only.

## Borrowed text splitting (STD API / compiler integration)

- [x] Keep the splitter algorithm in the STD and route native convenience calls to it.
- [x] Retain UTF-8 text-field, constructor and optional-result storage dependencies.
- [x] Lower checked text slices and evaluated descriptor operations.
- [x] Forward text results through the existing generic Iter wrapper.
- [x] Reject premature source/ separator destruction and source mutation.
- [x] Execute twelve successful programs, four refusals, seven related regressions and the README text package.
- [x] Build the compiler from its updated C emission and compare the next emission byte for byte.
- [x] Pin the published STD, complete the install build and run the example with automatic STD resolution.
- [x] Record [evidence and limits](TEXT_SPLIT_CYCLE.md).

No language arbitration remains. `corbo.lock` pins the published STD revision
`d15cd7b6d6a567c4b7e98211b7fb0c7e2e5a7a90`.

## Documentation coverage gaps (compiler/core)

- [x] Replay the nine historical failures without changing their sources or accepted rules.
- [x] Integrate function structural contracts and explicit returned-borrow arguments.
- [x] Integrate branch/lock signature metadata, temporary joins and aggregate lock-result dependencies.
- [x] Integrate and validate batched exact numeric try_from, typed text length, named slice comparison and C address operands.
- [x] Accept usize-bearing records in custom buffered adapters.
- [x] Execute 18 focused programs, seven refusals and the six/seven callable regressions.
- [x] Validate the compact resource representation, history wrap and runtime-only boundary.
- [x] Install the compiler; compare its own emitted C byte for byte.
- [x] Update historical observations, documentation replay and the [cycle report](DOCUMENTATION_COVERAGE_CYCLE.md).

No new language decision remains for these nine forms. Platform limits and
unexercised compositions are listed in the report.

# General callable support (compiler/core)

- [x] Reuse the existing closure and `fn` / `&fn` / `&mut fn` syntax.
- [x] Materialize concrete capture records and specialize callable parameters.
- [x] Preserve explicit moves, Copy captures, field dependencies and module visibility.
- [x] Reuse a bounded expansion workspace before ordinary verification and placement.
- [x] Complete the bootstrap build and six executions/seven rejection checks.
- [x] Execute the former rejected package, the README example and iterator composition.
- [x] Finalize the [cycle report](GENERAL_CALLABLES_CYCLE.md), verification matrix and installed compiler.

# Bare type parameter declaration

- [x] Accept the bare form and reject the former star spelling in parse_annotation.
- [x] Preserve the existing unconstrained-parameter AST role and usage-site constraints.
- [x] Migrate active fixtures, pin the compatible STD and regenerate runtime resources.
- [x] Build the compiler once and install it with the matching STD.
- [x] Complete three parser checks and execute the Reader example.
- [x] Record the focused validation; broad tests and self-reconstruction were not run.

# Corbo runtime integration (compiler/runtime)

- [x] Add checked, scalar-only `--emit-runtime-c` emission without managed allocation.
- [x] Keep ordinary application checking and the explicit unchecked ABI boundary.
- [x] Compile the language repository's Corbo runtime into namespaced resources.
- [x] Pin the implemented source revision and select `runtime_implementation="corbo"`.
- [x] Add bounded packed resources and execute decoder/history-wrap regressions.
- [x] Complete the pinned compiler self-rebuild and normal package-build smoke test.
- [x] Complete integrated regression and real platform reactor checks.
- [x] Record the [cycle report](CORBO_RUNTIME_CYCLE.md) and verification evidence.

The C reference remains selectable. Windows ARM64 execution is deferred.
No normative language rule changed.

# Compiler repository extraction

Scope: repository/build organization, not a language-rule or backend-algorithm change.

- [x] Move the compiler package to the root of `omework/corboc`.
- [x] Move focused compiler regression scripts and fixtures with it.
- [x] Pin the STD, runtime and normative sources in `corbo.lock`.
- [x] Prepare an isolated source cache and reject mismatched/modified inputs.
- [x] Generate embedded runtime resources from the pinned checkout.
- [x] Add a build/install script retaining automatic installed-STD discovery.
- [x] Update language-repository tools with external compiler discovery/forwarders.
- [x] Complete self-reconstruction, normal package self-build and module smoke test.
- [x] Execute focused regression suites and six source-lock checks.
- [x] Finalize the [report](REPOSITORY_SPLIT.md) and verification matrix.

No language decision is open. Native compiler self-hosting is exercised on the
macOS ARM64 host; this extraction does not broaden platform validation claims.
Windows ARM64 remains deferred.

## Subdb propagation cleanup

- [x] Stop partial-expression cleanup at lexical blocks.
- [x] Rebuild the compiler and execute the focused cleanup regression under fatal UBSan.
- [x] Compile and execute the affected Subdb persistence examples.
- [x] Record the evidence and retain the existing published STD pin.

## SubDB facade compiler integration

- [x] Promote independently contracted instance methods with explicit receiver modes.
- [x] Infer receiver payload types after `?`.
- [x] Reuse structural fixed-value summaries for returns and native worker captures.
- [x] Keep owned fixed-array fields inline across record returns/moves.
- [x] Accept disjoint field arguments; MA1–MA6 also allows proven content-only aliasing.
- [x] Move named fixed-record values into arrays while rejecting later reuse.
- [x] Execute four focused regressions under fatal UBSan and reject three invalid forms.
- [x] Run the SubDB facade and retain focused evidence, without changing the STD lock.

See [the cycle report](SUBDB_FACADE_CYCLE.md) and the sibling SubDB validation report
for application/platform evidence and limits. Release installation is unchanged.

## Mutable references as mutation permission (core semantic change)

- [x] Record the user-approved MA1–MA6 decision in the language specification.
- [x] Inspect permission/exclusivity coupling and identify affected compiler mechanisms.
- [x] Record [the source-impact inventory](MUTABLE_ACCESS_PLAN.md).
- [x] Separate mutation permission, validity dependencies and explicit lock exclusion.
- [x] Apply effect-based compatibility through calls, projections and reborrows.
- [x] Preserve per-branch completion and synchronization proofs across captures/results.
- [x] Complete 9 fatal-UBSan executions, 10 refusals and supported-target native capture checks.

Implementation and focused validation are complete. See
[the cycle report](MUTABLE_ACCESS_CYCLE.md) for bounded-summary limitations and
platform evidence. Unknown required proofs remain refusals. The STD/runtime pin
now references committed Corbo revision `d54cf3063861498fc721b78d9bbd11ba6ac8f667`; the source-lock and
regenerated-runtime checks pass. The release installation is unchanged.

## Ordinary lock type names

- [x] Remove Mutex/AsyncMutex lexer, builtin arity and special rejection handling.
- [x] Preserve generic named types, associated calls and explicit lock contracts.
- [x] Execute a declared-name fixture under fatal UBSan; reject three undeclared names uniformly.
- [x] Align English/French MT9 and retain the [focused report](ORDINARY_LOCK_NAMES_CYCLE.md).

Object-level inheritance is implemented separately below; it never follows from
naming a type Mutex.

## Object-level lock contracts (MT11)

- [x] Parse bare `#(lock)` on structs and retain public instance-method visibility.
- [x] Derive receiver contracts; exclude private helpers and receiver-less constructors.
- [x] Preserve object/method contracts through generic specialization and module loading.
- [x] Reject checked same-object acquisition through direct calls, helpers and aliases.
- [x] Preserve explicit through-result contracts and existing guard-release checks.
- [x] Execute six accepted fixtures under fatal UBSan and reject ten invalid forms.
- [x] Execute the real-lock three-thread fixture on supported targets; Windows ARM64 compile-only.
- [x] Check identical self-emission and record the [cycle report](OBJECT_LOCK_CYCLE.md).

## Thread transfer eligibility (TR1)

- [x] Parse `#(thread: transfer=false)` on structs and enums; reject invalid placement/duplicates.
- [x] Preserve metadata through generic specialization and ordinary layout/signature views.
- [x] Derive owned-field, binding, capture-record and suspended-state restriction summaries.
- [x] Check native/async/declared-branch boundaries, including worker results.
- [x] Preserve ordinary moves, fresh worker-local values and cleanup before suspension.
- [x] Execute five focused packages with fatal UBSan and reject fourteen invalid forms.
- [x] Retain passing object-lock regressions: six executions and ten refusals.
- [x] Document target-independent analysis and conservative summary limits.

See [the cycle report](THREAD_TRANSFER_CYCLE.md). The Rust frontend and installed
release remain unchanged; the development compiler is `build/thread-transfer/corboc`.

## Runtime memory metrics API

- [x] Load the STD-supplied `runtime::metrics` namespace with ordinary module resolution.
- [x] Preserve bookkeeping when emitted code rewinds fixed datastack cursors.
- [x] Regenerate the Corbo runtime bridge from readable source, including ABI version 2.
- [x] Execute eight API observations and C/Corbo concurrent ABI witnesses with fatal UBSan.
- [x] Execute the API on macOS ARM64/x86-64, Linux x86-64 and Windows x86-64; Windows ARM64 compile-only.
- [x] Regenerate source documentation and record the sampling/managed-storage boundaries.

Development compiler: `build/memory-metrics/corboc`. The installed release
remains unchanged. The STD/runtime source lock now pins the
committed metrics implementation. [Integration report](MEMORY_METRICS_CYCLE.md).
