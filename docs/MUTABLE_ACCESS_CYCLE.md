# Mutation permission, synchronization and lifetime separation

Core/compiler implementation of MA1–MA6 (November 21, 2026). No new grammar,
primitive, runtime lock implementation or STD API. The Rust frontend remains
frozen. The existing runtime and declared lock contracts are reused.

## Implemented mechanisms

`CheckedValue.writable` is permission to write through a reference. It is no
longer called `exclusive`. Explicit retained locks use their existing dedicated
summary marker (5019); that marker grants no reference write permission.

After lexical resolution, `prepare_accesses` records independent static facts:
`StaticNode.access_mode` establishes storage-preserving content effects, and
`StaticNode.protection` identifies a proven protecting lock. Formal effects are
composed through concrete calls; lock parameters are substituted with actual
identities. Native captures retain their own effect/protection facts. Binding
mutability, target identity, loan-parent links and ownership state remain separate.

Content reads/writes and pure borrow creation may coexist through multiple
references. Destructive, moving or unresolved effects retain the conservative
validity/dependency checks. Aliased call arguments are allowed when the callee's
effects preserve storage and argument preparation has no hidden invalidating
call. Scalar/primitive-array writes and content-only record methods use this
path. This does not make mutable references Copy or permit writing through `&T`.

Potentially concurrent conflicting accesses are compared against outstanding
branch captures. Every matching capture must establish the same exact lock
identity as the access being admitted. Native captures compare against siblings
visible at launch, not only the worker's isolated lexical environment. Lock
contexts do not automatically extend from a parent call into a deferred worker.

Inactive Futures retain dependencies without executing content effects. Creating
two such Futures is permitted; launch and direct await check their captures at
the actual execution boundary. Completing one handle removes only its existing
branch dependency. Other branches, borrowed results, early exits and existing
per-outcome cleanup remain subject to the pre-existing lifetime machinery.
Through-result locks still last until their declared destruction/release point;
two blocking acquisitions before release remain refused.

## Focused validation

`scripts/validate_mutable_access.py` retains nineteen checks:

- Nine O1/fatal-UBSan executions: scalar aliases and a returned reborrow; aliased
  function arguments; content-only record methods; sequential awaits of inactive
  Futures; three native threads sharing one scalar under one real atomic lock;
  aliased buffer arguments; explicit guard release; lexical propagation cleanup;
  and independent returned fixed fields.
- Ten refusals: different locks, an unlocked competing writer, a parent read before
  every join, overlapping unlocked Futures, a target ending too early, owner drop
  while references are needed, early exit with outstanding branches, two retained
  lock reacquisition forms and reuse after moving a record into an array.

The former `reject_aliased_buffers` fixture is now `aliased_buffers`: its sequential
same-place writes are valid under MA1–MA6. Historical results describe the previous
rule; the focused SubDB regression runner uses the revised expectation.

The three-thread atomic-lock program also executes on macOS x86-64 (fatal UBSan),
Linux x86-64 in a linux/amd64 container, and Windows x86-64 under Wine. macOS ARM64
host execution is covered by the focused runner. Windows ARM64 compiles only;
execution remains deferred. Target executables were emitted using temporary host
emitters selecting the existing target predicates, then compiled with cc/Zig.
No Windows hardware run, native compiler bootstrap on those targets or ThreadSanitizer
claim is made. Results are retained in `validation/mutable-access-results.json`
and `validation/mutable-access-platform-results.json`.

## Conservative limits

Effect/protection summaries are bounded. Recursive or opaque effects and lock
identities that cannot be instantiated remain unproven and are rejected for
conflicting sharing. In particular, an overlapping storage root is not proof that
two projected lock objects are identical: currently unresolved projected lock
identities return no proof. Reassigned aliases likewise cannot establish a stable
lock identity from their initializer alone. Complex wrapped-capture summaries do
not become synchronized merely because their roots overlap.

This is not an exhaustive alias/concurrency audit or a general safety proof.
Lock annotations remain trusted implementation contracts: the compiler does not
prove native lock acquisition/release code. Existing unchecked boundaries retain
their developer responsibilities. No mutation campaign or broad legacy suite was run.

## Build status

The seed-built compiler is `build/mutable-access/corboc`, using the sibling working
STD explicitly. The source lock now pins committed Corbo revision `d54cf3063861498fc721b78d9bbd11ba6ac8f667`.
The release installation is unchanged; no uncommitted source tree is pinned. The separate self-emission snapshot records the compiler's
reconstruction result and whether emitted compiler C matches the seed emission.

Final self-reconstruction check: the updated compiler emitted its own package
successfully in 26.55 seconds, producing 14,338,180 bytes of C, byte-identical to
the seed emission. The snapshot is `validation/mutable-access-self-emission.json`.
This is one self-emission comparison, not an additional broad test campaign.

## Documentation alignment

The English/French READMEs, N5/B1/B2 and affected return/projection/array clauses,
async capture/branch clauses, memory representation and implementation checklists
now use permission rather than implicit uniqueness. Dated exclusion examples and
verdicts in earlier design/validation documents are explicitly marked historical.
Iter and File API comments were aligned and the STD reference regenerated. The
source/reference coverage check passes for 97 STD files (1,596 documented entries)
and 32 runtime files (777 entries). No grammar production changed and no compiler
execution was repeated for these documentation/comment-only updates.

## Publication

`corbo.lock` pins the committed language/STD/runtime revision
`d54cf3063861498fc721b78d9bbd11ba6ac8f667`. The clean dependency cache passes source-lock verification.
Runtime resources were regenerated through `scripts/runtime_sources.py` and are
byte-identical to the previous resources because the readable runtime did not
change; the freshness check passes against the committed revision.
