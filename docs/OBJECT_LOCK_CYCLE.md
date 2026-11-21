# Object-level lock contracts

Core/grammar change explicitly approved by the user. A bare `#(lock)` on a struct
makes its public instance methods inherit `#(lock: on=self)`. Private helpers and
associated functions without a receiver do not acquire automatically. A method
can explicitly extend the same contract through its result. The compiler does
not synthesize locks; the implementation remains developer-owned. Mutex and
AsyncMutex also lose their former name-specific lexer/declaration treatment;
[the preceding report](ORDINARY_LOCK_NAMES_CYCLE.md) records that cleanup.

## Representation and analysis

The AST retains the object annotation and method public visibility. The static
field/signature view omits metadata while raw AST ownership preserves it.
Effective lock parameters are derived from the nominal owner, without special
receiver-type names. Generic rendering retains lock contracts while removing
specialization recipes. The existing access/protection analysis consumes those
effective contracts, including shared-thread content accesses and retained guards.

The re-entry pass follows checked call paths with symbolic parameter-to-actual
mapping. It rejects same-object direct calls, recursion, private/free-function
routes and aliases. Different parameter names do not establish different objects.
Fresh locally constructed independent objects may be called. Unknown required
identity proofs remain refusals; this is deliberately conservative.

During validation, a borrowed nominal parameter initially escaped call resolution:
the reference annotation wrapped the actual type. Resolving its referent before
nominal lookup fixes the possible-alias rejection. This uses the common receiver
resolver rather than a special case for a lock type.

## Executed evidence

`python3 scripts/validate_object_lock.py` uses the development compiler
`build/object-lock/corboc`, built with the preceding compiler and pinned STD.

- Six accepted packages execute at O1 with fatal UBSan: private helpers/fresh
  instances, unmarked types, generic specialization, module import, explicit
  through-result guards and real native three-thread synchronization.
- Ten invalid packages reject: direct/indirect/recursive acquisitions, local and
  possible parameter aliases, free-function helper and generic re-entry, bare
  marker on a method, duplicate marker and enum placement.
- Existing `lock_drop_release` executes with fatal UBSan (42);
  `reject_double_reserve` and `reject_lock_after_use` reject with rule 5.
- The actual atomic-lock three-thread package executes on macOS ARM64 and x86-64,
  Linux x86-64 (container) and Windows x86-64 (Wine). Windows ARM64 cross-compiles;
  execution is deferred as agreed. Platform emitters use the existing temporary
  target-selection harness; no production target predicates are changed.
- Self-emission succeeds in 26.97 seconds, 14,401,024 bytes, byte-identical to the
  seed-built C output. This is a host self-emission check, not a cross-host bootstrap.

Results: `validation/object-lock-results.json`, `object-lock-regressions.json`
and `object-lock-platforms.json`. Ordinary-name results are retained separately.

## Limits

No independent audit, mutation campaign or general safety proof is claimed.
Symbolic identity analysis is conservative across parameters, aggregate aliases
and opaque callbacks. Helper traversal is bounded to 128 frames and root tracing
to 64 steps; exhausted required proofs reject. Runtime/foreign locking behavior
inside `@unchecked` is trusted. Object markers currently apply to structs, not
enums; explicit method contracts remain available. The frozen Rust frontend and
installed release binary are unchanged. The development compiler contains this
implementation. Windows ARM64 execution remains unvalidated.

## Published inputs

The compiler pins Corbo revision `c8bbadf15094f0d297c68fffcab4693cffbc8102` in `corbo.lock`.
The source-lock and generated-runtime checks are performed against that revision.
