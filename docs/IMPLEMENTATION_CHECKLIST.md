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
