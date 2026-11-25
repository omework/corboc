# Standalone Vector ownership and dependencies

## Scope

Compiler/core integration and its ordinary STD implementation. No grammar,
copy-eligibility, lifetime, synchronization or branch rule was relaxed. The
plain-data-only specialization gate was removed. Existing pooled vectors remain
available; a standalone descriptor does not require a user-facing pool.

## Mechanism

- Insertion snapshots the element's existing checked-value graph into immutable
  member entries. The vector retains references, source-pool dependencies and
  deferred task state through the same owned-summary traversal as aggregates.
- Field mappings locate a descriptor inside its containing record. Extraction
  preserves named field mappings and any additional candidate dependencies.
- Known straight-line pop removes one proven insertion. A loop insertion can
  represent multiple actual elements, so its summary is retained conservatively.
  Conditional/repeated extraction and clear can retain dependencies longer than
  runtime membership; this may reject valid programs rather than erase an
  unproven loan or task dependency.
- Ordinary helper calls instantiate their own argument environments, recursively
  propagating insertions into borrowed vectors and vectors returned by factories.
  Async record-return construction retains the same instantiated graph.
- Nominal allocation parameters and records containing owned allocations use
  ordinary type and ownership checks instead of scalar-only signature fallbacks.
- The STD transfers input into a local Option before the unchecked storage copy,
  then clears its runtime discriminant to prevent double destruction. Pop returns
  ownership through Option. Clear and drop destroy remaining elements before
  reclaiming regional payload and registration storage.
- Matching an empty Option<Handle> now creates an empty typed payload summary;
  it no longer copies slot zero, which is the summary allocator's workspace.

Implementation: src/vector_values/vector_values.crb,
src/signatures/signatures.crb, src/value_summaries/value_summaries.crb,
src/value_dependencies/value_dependencies.crb, src/loans/loans.crb and the STD
collections/vector_value.crb. Fixed descriptor placement and regional runtime
allocation policy remain unchanged. Runtime source/ABI was not modified.

## Validation

Focused executable results are recorded in VECTOR_OWNERSHIP_RESULTS.json.
The script is scripts/validate_vector_ownership.py; it checks ordinary functional
behavior and directly related ownership/dependency refusals under fatal UBSan.
No full historical corpus, mutation campaign or independent safety audit was run.

Platform scope: host macOS ARM64. Windows/Windows ARM64 execution is not claimed.
The Rust frontend remains frozen. The compiler build uses an explicit development
STD override; corbo.lock is not silently repinned to an uncommitted tree.

## Implementation bounds

The new path provides new/len/is_empty/push/pop/clear. The older indexed/sliced
native-vector API is unchanged. Ordinary compiler type/operand limitations can
still reject a composition outside its existing supported forms. Conservative
membership summaries are not a claim of exact runtime length or full rule parity.

## Executed outcome

All 16 focused observations passed on macOS ARM64: ten executable programs under
fatal UBSan and six expected rule refusals. Executables cover shared/mutable
references, borrowed records, text/byte slices, custom destruction, nested vectors,
A<Resource>, records owning A<Resource> with pool-slot reuse, native handles and
nested helper/factory dependencies. Refusals cover moved values, borrow conflicts,
dangling targets, premature pool destruction and repeated-insertion dependencies.

The compiler reconstructed its current source successfully using the preceding
self-hosted generation. This is not a full three-generation fixed-point claim.
Installed binary SHA-256: `58df9a417efc729abc8f55c0206cca7db70ee9eb6fc103210be3342ccebb40c9`.
Installed path: `/Users/jabarkarim/sources/corboc/build/check-file/install/bin/corboc`.
The matching working-tree STD is installed alongside it. No commit or push.

Post-install checks passed: the actual SubDB dispatcher checks successfully with
the PATH binary; the README budget example builds and prints `1000`. Generated
installed HTML docs and checked STD/runtime Markdown reference freshness.
`command -v corboc` resolves to the installed path recorded above.

## Committed dependency alignment

Corbo is committed and pushed as `4e841e8cc7f0509e343afc6ba95a7640772a35f1`.
`corbo.lock` now pins that revision. The clean dependency cache was advanced to
the same commit; source-pin verification and runtime-bridge freshness both pass.
The prior development-override execution evidence above is retained as history.
Before committing corboc, the installed STD was compared byte-for-byte with the
pinned STD and the installation metadata was aligned with the committed pin.
