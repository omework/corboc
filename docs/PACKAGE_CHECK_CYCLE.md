# Package check and watch

Date: 2026-11-22. Scope: CLI/build tooling; no grammar or normative rule change.
The implementation lives in the corboc repository. The language checkout changes
only its English and French getting-started documentation.

## Implementation

`corboc check [PACKAGE] [--watch]` shares manifest loading, dependency/import
resolution, target selection and static verification with package compilation.
Verification mode returns before C generation and never invokes the native
compiler or creates a build directory. Existing statuses and rule/offset
diagnostics remain; file/line diagnostics and IDE integration are separate work.

Watch performs an initial check and then polls content every 250 ms. Two stable
snapshots debounce saves. SHA-256 path/content digests are combined independently
of directory enumeration order. The caller owns fixed-size digest buffers and
files are read with a 4096-byte streaming buffer. Additions, deletions, same-size
edits, atomic replacement and manifest changes are observed. Failed checks stay
in the loop; no previous failed verdict is reused after a content transition.
Hidden entries, root build/target directories and node_modules are skipped.
Symlinks are not followed. Paths are bounded to 4096 bytes and nesting to 64.
External dependencies/installed STD are resolved on each check but not watched.
The whole package is rechecked; this is not incremental analysis.

## Focused evidence

On macOS ARM64, the installed command checks a two-module package with an empty
PATH (no C toolchain), checks explicit package roots and path dependencies,
rejects syntax/semantic errors, malformed CLI options and missing packages.
Watch survives errors, observes saves/atomic replacement/addition/deletion and
manifest changes, and ignores generated/hidden files. No build directory or
temporary C output is created by check. Results are recorded in corboc's
`docs/PACKAGE_CHECK_RESULTS.json`.

The new executable-location boundary was probed independently on macOS
ARM64/x86-64, Linux x86-64 via Docker and Windows x86-64 via Wine. Those probes
are not full cross-platform compiler/CLI executions. Windows ARM64 execution
remains deferred. Existing loader/verifier/platform limits are unchanged; no
broad corpus, new rule audit or safety proof is claimed.

Reproduce from corboc:

```sh
python3 scripts/validate_package_check.py --compiler build/check/install/bin/corboc
```

## Final installed validation

The compiler was reconstructed and installed against Corbo revision
`c897502f8eabdbdbb65b48da49cf037ef80e0e5c`. The final focused CLI run
passed 13 recorded observations, including installed-executable symlink
resolution, owner destruction with a live guard being refused, and a normal
package build whose executable prints `42`. Watch transitions are recorded
as one integration observation rather than counted as separate rule proofs.
No full corpus or multi-generation bootstrap-equivalence run was performed.
