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
