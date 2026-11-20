# Package scaffolding command

Scope: compiler CLI/build tooling. No grammar, accepted language rule, STD or
runtime implementation changed. Rust remains frozen. The implementation lives
in src/package_new; main dispatches `corboc new <package_name>` to that module.

The command creates one new child directory containing package.toml, an empty
src/main.crb, .gitignore and README.md. Package identifiers use ASCII letters,
digits and underscores, start with a letter or underscore and contain at most
255 bytes. std/runtime are reserved. Native filesystem restrictions also apply.
Paths and hyphenated package names are rejected rather than silently rewritten.
No Git repository is initialized.

Exclusive native mkdir/CreateDirectory refuses existing destinations before any
file writes, including empty directories and ordinary files. File output uses
the explicit blocking STD File API and retries partial writes. File handles
close at scope exit. A failure after directory creation reports an error and
retains the partial directory; transactional rollback is not claimed. Filesystem
races against a malicious concurrent process are not audited by these checks.

## Executed evidence

On macOS ARM64 the rebuilt full compiler passes ten focused CLI checks:
creation, exact scaffold shape, preserving an existing package, ordinary file
and empty directory, building/running the generated executable, missing/extra
arguments and a table of invalid names with no filesystem effects. The same
checks pass through build/install/bin/corboc with its matching pinned STD.
This is one ten-check set exercised at two installation paths, not twenty
independent semantic cases.

The production package_new module was copied unchanged into a temporary small
CLI harness for platform checks. macOS x86-64 (Rosetta), Linux x86-64 (Docker)
and Windows x86-64 (Wine) pass creation/content, existing-path refusal, invalid
name and usage diagnostics. macOS/Linux harness executions use O1/fatal UBSan;
Windows uses Zig O1 without UBSan. Windows ARM64 compiles to an object only;
execution remains deferred. These are module/native-boundary checks, not full
native compiler rebuilds on each platform. Existing Linux ARM64 File/CLI limits
are not extended. Temporary host emitters select each target's existing backend.

The full compiler was built once for this change; no broad compiler corpus,
self-reconstruction campaign, disk-failure injection or independent audit ran.
The implementation uses explicit byte-view bindings and slice bounds supported
by existing call lowering rather than adding compiler mechanisms for this CLI.
STD/runtime pin and embedded runtime code are unchanged.

[Machine-readable results](PACKAGE_NEW_RESULTS.json).

```sh
python3 validation/check_package_new.py --corboc build/install/bin/corboc
```

The test retains report.json under build/package-new-validation. README quick
starts describe package creation in both language documentation languages and
the compiler README. The installed binary is build/install/bin/corboc.
