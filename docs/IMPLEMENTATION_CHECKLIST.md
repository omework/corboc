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
