# Mutable access: compiler impact inventory

Core semantic change accepted on November 21, 2026. The normative decision is
in the sibling language repository's `docs/MUTABLE_ACCESS.md` (MA1–MA6).
The inventory below records the pre-implementation source findings. The separation
is now implemented and focused validation is complete; see
[MUTABLE_ACCESS_CYCLE.md](MUTABLE_ACCESS_CYCLE.md) for the current mechanisms,
conservative limits and evidence. Historical `exclusive` field references below
refer to the prior representation; the current permission field is `writable`.

## Target behavior

`&mut T` means permission to mutate, not uniqueness. Multiple references can
coexist. Acceptance still requires N4 lifetime validity, N5 compatible accesses,
N6 path/evaluation reasoning, N7 cleanup and N8 interprocedural propagation.
Potentially concurrent overlapping accesses involving a write need established
synchronization. Completion contracts discharge only the corresponding branch's
execution dependency; results that retain references keep their dependencies.
Unresolved obligations still reject. Ownership and reference-copy/move rules do
not change. Lock contracts remain explicit exclusivity contracts.

## Source findings and required separation

| Area | Current assumption observed | Required change |
| --- | --- | --- |
| `src/model/model.crb`, `CheckedValue` | `exclusive` is carried alongside binding mutability, target and loan parent. Callers use it both for mutable-reference mode and for exclusion; lock summary marker 5019 also sets it. | Represent write permission independently from explicit lock/exclusion intervals and lifetime dependency edges. Preserve binding mutability separately. Do not rename the flag globally and assume its meanings are equivalent. |
| `src/loans/loans.crb`, `loan_conflict_from` | An overlapping live reference can reject a write, or a read when a reference is marked exclusive, based on future uses. Task reservations and explicit lock markers also reach this path. | Classify the operation: content read/write, access acquisition, move, invalidation/destruction or explicit lock acquisition. Allow reference coexistence and sequential content access, while retaining dependency checks for invalidation and synchronization checks for concurrent access. Keep `reserves`, `live_roots` and place/provenance tracking; a blanket `return 0` here is incorrect. |
| `src/signatures/signatures.crb`, `check_signature` / `argument_conflicts`; `src/places/record_arguments.crb`, `check_record_argument` / `reserve_method_receiver` | Argument pairs with the same root are rejected when either is exclusive, except established disjoint fields. | Separate preparation/evaluation effects from execution effects. Same-root mutable arguments are not intrinsically invalid; derive read/write/invalidation, concurrency and lock requirements from the callee contract and apply them to actual places. Preserve evaluation order and permission checks. |
| `src/nested_loans/nested_loans.crb`, `src/places`, `src/stored`, `src/verify` | Nested references, projected fields/cases, assignments, collection operations and reborrows reuse mutable/exclusive checks and the conflict helper. | Reborrows preserve permissions and dependencies rather than automatically suspending all parent content access. Resolve actual places, including reference binding storage versus referent storage. Keep disjointness and dependencies on structural locations; only effects that invalidate those locations should block their later use. |
| `src/loan_contracts`, `src/value_summaries`, `src/signatures` | Existing return provenance and retained-argument summaries preserve roots and mutable mode. They are not by themselves a complete access/synchronization-effect summary. | Compose operation effects, protected places, lock identity/interval and escaping dependencies through calls, aggregates, closures and returned references. Unknown effects must remain unproven rather than being justified by assumed `&mut` uniqueness. Reuse the post-AST/summaries instead of introducing concrete-library special cases. |
| `src/tasks/tasks.crb`, `check_native_worker`, `verify_task`, `task_exit`, `waits_on_entry`; `src/task_relay`, `src/task_vectors`; task helpers in `src/loans` | Captures keep target reservations; mutable captures can exclude other accesses until waiting. Completion summaries also cover deferred effects and wrapped handles/results. | Keep one outstanding lifetime dependency per relevant branch/capture and apply established completion per control-flow path. Coexisting captures are permitted when actual potentially overlapping accesses satisfy synchronization. Carry parent accesses, nested branches, pending futures and returned dependencies; completing one of several branches cannot release the others. Preserve existing LaunchFailed/success cleanup outcomes without treating any arbitrary error as proof of completion. |
| `src/lock_contracts/lock_contracts.crb`, `lock_parameter`, `retain_lock`, `validate_effect_annotations` | Lock annotations identify a formal and through-result retention. The retained lock is attached as an exclusive lifetime-summary marker (5019). Annotation validation recognizes handle completion forms; task waiting also recognizes concrete join/await operations. | Keep explicit lock reservations independent of writable references. Associate actual access places with resolved protection and active intervals, including readers. Use the declared branch completion contract across call boundaries; do not infer that an arbitrary method named join ends execution. Preserve through-result lock release at destruction, the same-object blocking reacquisition refusal and all per-outcome dependencies. |
| `src/lowering*`, native/async capture lowering | References and captures are emitted under decisions made by the checker. A targeted source search found no explicit restrict/noalias spelling in active lowering. | Confirm emitted ABI/storage accesses tolerate the accepted aliases and preserve stable storage, ordering and lock operations. Do not introduce optimizer uniqueness assumptions for `&mut`. This source observation is not a backend correctness proof. |

These are shared mechanisms, not separate rules for Vector, HashMap, File or a
particular thread count. The same representation/effect reasoning must compose
for all user-defined and STD types.

## Required facts in the representation

The post-AST should preserve or summarize separately:

- The reference's binding, scope, owner, target place and permission to write.
- Read/write versus storage-invalidating effects on resolved places and paths.
- Existing ownership/provenance and reference-storage dependency edges.
- The execution branch that may perform an access and its established completion.
- The resolved lock identity and the interval/contract protecting each access.
- Dependencies retained by results after completion and the effects of each outcome.

These are analysis requirements, not a declaration that all fields are absent
from the current representation. Reuse existing data and summaries where they
already express a fact; add explicit distinctions where `exclusive` conflates it.
No new user syntax or runtime borrow-counter primitive is proposed.

## Implemented sequence

1. Separate permission, validity dependency and explicit exclusion in the compact
   values/summaries; migrate consumers without dropping existing checks.
2. Route operation checks through those distinct facts; compose synchronous call
   effects, projections and reborrows.
3. Track synchronization requirements for overlapping execution and apply each
   branch completion, including surviving result dependencies.
4. Preserve lock-contract retention and verify backend alias assumptions. Then
   validate the affected mechanisms with focused regressions. Reference-count
   based rejections must be reclassified, not mechanically changed into accepts.

The implemented cycle is documented separately. The Rust frontend remains frozen.
The accepted specification is now committed and adopted through `corbo.lock` at
`d54cf3063861498fc721b78d9bbd11ba6ac8f667`.
