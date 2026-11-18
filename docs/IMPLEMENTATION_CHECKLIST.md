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
