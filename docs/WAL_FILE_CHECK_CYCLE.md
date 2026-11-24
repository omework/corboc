# WAL file check: guard iteration and source alignment

Scope: compiler/core fixes and SubDB source corrections. No grammar, language-rule
or STD/runtime API change. The frozen Rust frontend is unchanged.

## Compiler corrections

1. Iteration inference previously returned the same classification for an unknown
   generic-dependent source and a known next()-based iterator. Early normalization
   therefore rewrote a guard's tuple array into a next() call before its type was
   specialized. Unknown sources now defer classification.
2. Overloaded dereference in a borrowed loop header is materialized after the
   header's normal array-to-slice view transformation. This avoids manufacturing
   an unsupported reference-to-whole-array temporary. Evaluation remains at the
   original source position.
3. Moving a slice out of a generated block previously used the aggregate fallback
   and lost its mutable permission and parent-loan summary. Slices and UTF-8 views
   now use the existing dependency-preserving transfer path, including alias
   reduction and lifetime validation. No permission is granted to a shared view.

## SubDB source corrections

The user authorized updating `/Users/jabarkarim/sources/subdb/src/wal/file.crb`
until its exact file check succeeded. The source changes are:

- Await the async offset provider.
- Iterate slots through an explicit mutable borrow.
- Correct `Avaible` to `Available` and return `Some(offset)` as declared.
- Remove the redundant WAL destructor; ordinary owned-field cleanup closes File.

File checking retains required module companions and transitive imports. The WAL
companion imports root definitions, which pull in `main.crb` and `catalog.crb`.
Those still passed legacy byte paths to File. They now pass UTF-8 views; catalog
conversion excludes the path helper's trailing NUL and explicitly reborrows the
view for open before the create fallback. Other application policies are unchanged.

## Evidence

- `scripts/validate_wal_guard_loop.py`: two executions pass with fatal UBSan, using
  overloaded dereference and an explicit guard reference respectively. Each
  reserves offsets 3 and 7, returns None when exhausted and completes normally.
  Early returns release the guard, allowing the next call to acquire it.
- `scripts/validate_iteration.py`: five positive executions and five expected
  refusals pass, including ordinary next() iteration and cleanup.
- Diagnostic-site audit: 1,019 catalog entries and 353 observed state writes pass.
- Rebuilt compiler installed at `build/check-file/install/bin/corboc`; SHA-256
  `f3d2c267c1bb231e4d13c027886cd5cda6e3b114b1071d738b0ffd2b992d7276`.
- Installed binary: `corboc check /Users/jabarkarim/sources/subdb/src/wal/file.crb`
  exits 0 and prints `corboc: check passed`. Output is retained in
  `build/wal-slice-summary/file-check.stderr`.

Execution is limited to macOS ARM64; no platform code changed and Windows ARM64
execution remains deferred. This is evidence for the affected paths and a
successful static file check, not a runtime validation of all WAL business logic.
Temporary compiler instrumentation used during diagnosis exists only under /tmp
and is absent from the source and installed binary.
