# Recursive projected writes

## Failure and repair

The reported `self.buffer[index] = tuple` rejection started in declaration
validation: it required an indexed assignment to start with a bare binding,
before symbolic receiver state existed. The assignment checker repeated that
restriction, and aggregate replacement only dispatched on an array binding.
The diagnostic formatter then mistook missing symbolic state for an
uninitialized source-level `self`.

Declaration validation no longer guesses place validity from a binding's AST
shape. Assignment checking resolves fields, indices, grouping and dereferences
recursively, preserving the root, shape, availability and mutation permission.
Plain tuple/record replacement uses the same place-access checks as scalar
projection clients, validates the replacement against the destination shape,
and checks the root again after evaluating the RHS. Stable plain-value writes
use the existing content-access conflict path, preserving explicit lock and
outstanding-branch checks. Resource/dependency-bearing replacement analysis is
not bypassed or newly generalized by this cycle.

Tuple positional typing accepts declared annotations and inferred value shapes.
Array length queries also resolve projected receivers in checking and lowering;
the read-only condition classifier follows pure receiver projections instead of
requiring a bare name. Diagnostics report uninitialized use only when the
failure site establishes initialization as the issue.

## Existing move semantics still apply

`for slot in self.buffer` requests a by-value source. It would move the field
out of its containing value and is rejected with N3 and a specific explanation.
The compaction loop borrows its source with `self.buffer.ref()` instead. An
index compared with `.len()` should be explicitly `usize` under existing numeric
rules. This cycle changes neither implicit-copy rules nor partial-move rules.

## Focused evidence

`validation/check_projected_writes.py` executes eleven accepted programs under
fatal UBSan: field indexing, explicit dereference, tuple components, compound
component updates, slice aliases, borrowed iteration, compaction, inferred tuple
arrays, nested fields, record elements and a suspended async receiver.
A twelfth executable traps on a dynamic out-of-bounds index before access.
Five invalid programs reject: field move (N3), read-only mutation (N5), wrong
component type, tuple arity and constant index bounds (N1). No rejection falsely
claims that self is uninitialized.

The directly related existing tuple-iteration suite also passes six executions
and seven refusals. Diagnostic catalog integrity passes: 1012 stable identities,
with six superseded syntactic-guard sites explicitly retired rather than
renumbered. Rebuild succeeds; the installed compiler accepts the compaction
package and emits the new N3 diagnostic for the by-value source.

These are focused macOS ARM64 observations, not a general language-safety proof.
No target ABI, runtime, STD or assembly implementation changes were introduced;
platform suites were not replayed. The Rust frontend remains frozen and Windows
ARM64 execution remains deferred. SubDB source files were not modified.

Installed binary: `build/check-file/install/bin/corboc`.
