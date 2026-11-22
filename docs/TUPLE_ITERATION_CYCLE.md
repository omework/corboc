# Tuple projections and for patterns

Date: 2026-11-22. Scope: compiler/core and the grammar extension requested for
for-loop tuple patterns. The frozen Rust frontend and STD/runtime pin are unchanged.

## Behavior

The lexer distinguishes a decimal tuple selector from a leading-dot floating
literal. After an operand, `.0` is a dot and integer selector; in operand position
`.5` remains a float. Numeric selectors are accepted by the postfix parser.

`for (first, second) in expression { ... }` reuses ordinary tuple destructuring.
The source is evaluated once. A borrowed array/slice item produces references to
its original fields; permissions come from the source borrow, and dependency
links retain the source root and parent reference. An owned item uses existing
value moves and primitive copies. The tuple pattern must have the exact arity.
Individual bindings can use `mut`; the loop does not introduce implicit mutable
borrowing or grant permission through a shared source.

```rust
fn main() {
    let mut rows = [(1, 2), (3, 4)];

    for (left, right) in rows.mut_ref() {
        *left += *right;
    }

    for row in rows.ref() {
        print(row.0);
    }
}
```

Positional aggregate fields retain the existing storage-root representation.
Fixed arrays and slices now carry structural tuple layouts through the lowering
path, without truncating tuple type codes into container element codes. Layouts
and cleanup helpers are emitted in dependency order. Plain field assignments
retain their destination before evaluating the replacement. Fixed-array length
queries emit their known length rather than a nonexistent descriptor member.

Tuple arrays currently admit the existing structural primitive/primitive-enum
field path. This does not generalize resource-owning tuple-array extraction or
nested tuple layouts beyond the existing tuple backend. A plain field assignment
whose RHS suspends remains an explicit backend limitation until its destination
can be spilled into the async frame; it does not emit an unsaved pointer.

## Diagnostics

Malformed patterns identify the expected binding, comma or closing parenthesis.
Single-binding tuple patterns explain their minimum arity; `mut` belongs on an
individual pattern binding. Semantic arity errors identify the pattern instead
of an invented temporary name. Invalid selectors report a decimal-index or
field-range failure. Shared writes, moves and escaping references retain the
ordinary rule diagnostics and related source labels.

## Validation

The final binary passes six focused executions under fatal UBSan and seven
expected refusals. Executed examples cover the configurable WAL-shaped array,
primitive and enum field updates, borrowed doublet/triplet patterns, continue,
owned array iteration, field selectors and leading-dot floats. Refusals cover
wrong arity, missing indices, shared writes, use after move, malformed patterns
and escaping references. Ten existing iteration regressions also pass.

The compiler rebuilds from the updated compiler generation. The exact final
binary atomically replaces `build/check-file/install/bin/corboc`; a WAL-shaped
check and an arity refusal both pass through the installed binary. The static
diagnostic audit covers 1,011 sites and 351 observed checked-value writes.
`git diff --check` passes in both repositories.

Host execution: macOS ARM64. No fresh Linux or Windows execution was performed;
Windows ARM64 execution remains deferred.

[Recorded results](TUPLE_ITERATION_RESULTS.json).

```sh
python3 scripts/validate_tuple_iteration.py --compiler PATH
python3 scripts/validate_iteration.py --compiler PATH
```
No broad corpus, fuzzing or adversarial campaign is part of this change.
