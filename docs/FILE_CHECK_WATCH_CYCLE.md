# File checks and dependency-aware watch

Date: 2026-11-22. Scope: compiler CLI/build tooling. No grammar, normative rule,
STD API, Rust frontend or runtime implementation changes.

## Behavior

```sh
corboc check src/main.crb
corboc check src/main.crb --watch
corboc check --watch src/main.crb
corboc check path/to/package --watch
```

A `.crb` file under a package's `src/` uses the nearest enclosing manifest and
checks the complete package/module context. It is not an incremental check of
just the selected declaration. A file outside that context is loaded as a
standalone module with the installed STD; a library file need not define `main`.
The linker/verifier's internal library-check mode only removes the entry-point
requirement and still runs static verification. Check returns before C generation.
The selected file remains an explicit required input even after its deletion.

Watch retains 250 ms content polling and stable-snapshot debounce. Both package
and file modes include transitive local path-dependency trees and installed STD.
Manifests are reread each pass, so new/repointed dependencies become watched.
Canonical identities deduplicate packages and bound cycles to the existing
64-package budget. Root-salted tree hashes prevent overlapping dependency trees
from canceling identical file digests. Existing 4096-byte path and depth limits
remain. Standalone watches do not scan unrelated neighboring sources.

Pinned Git inputs are immutable: edits to their source/revision in a watched
manifest trigger resolution, but polling never fetches repositories or watches
mutable working trees as though they changed an already pinned commit. Existing
Git-checkout behavior still occurs during a check when required by resolution.

## Focused validation

Seven recorded file-check observations pass:

- Standalone STD import, and a library file without `main`.
- Semantic rejection with the existing verifier status.
- Standalone watch recovers from an initial syntax error; observes source and
  installed-STD edits, atomic replacement and deletion/recreation; ignores an
  unrelated neighboring source.
- File and module targets resolve their enclosing package and transitive imports.
- Package-backed file watch observes a transitive external dependency edit,
  refreshes its graph after a manifest changes a path, observes the new target,
  and rejects deletion of the selected file before recovering on recreation.
- Both placements of `--watch` are exercised.

The existing 13-observation package-check/watch regression script also passes,
including missing/invalid inputs, imported errors, manifest and source recovery,
generated/hidden-file exclusion, installed executable aliases and the normal
build path. Checks run without a C toolchain on PATH; the separate existing
normal-build regression is the only witness which deliberately builds a program.
No check-created build directory or temporary C artifact is observed.

Evidence: `FILE_CHECK_WATCH_RESULTS.json`. Executed on macOS ARM64. Existing
filesystem and executable-location adapters are reused; this cycle does not
claim complete Linux/Windows compiler executions. Windows ARM64 execution
remains deferred. No broad corpus, adversarial campaign or safety proof is claimed.

## Reproduce

From corboc, with an installed/rebuilt compiler:

```sh
python3 scripts/validate_file_watch.py --compiler build/check-file/install/bin/corboc
python3 scripts/validate_package_check.py --compiler build/check-file/install/bin/corboc
```

## Final pinned installation

Rebuilt and installed corboc once against Corbo revision
`37f3192ecf361d97f2818911123f2c99f84c0d10`; runtime resources still match the
unchanged readable implementation. The installed binary successfully checked a
standalone library importing the real `std::encoding::binary` API and the
package-backed README channel source, with automatic STD discovery. Compiler C
SHA-256: `ddee7bb1811ea61f1af671592475c351684fd293db1b8955485601b5b6c78178`.
No multi-generation bootstrap comparison was requested or run.
