# Ordinary lock type names

Core name-resolution cleanup requested by the user. `Mutex` and `AsyncMutex`
have no intrinsic static meaning. Synchronization facts continue to come from
explicit method contracts and result dependencies, not the spelling of a type.

Removed from the active compiler:

- Lexer builtin/placeholder recognition for both names.
- Builtin type-name and fixed generic-arity recognition.
- Special unsupported-reference-type and qualified-constructor treatment.

Both names now use ordinary nominal declaration, type argument and associated
function resolution. Runtime mutex implementations remain unchanged: native
locking operations are mechanisms, not language-name privileges. The frozen
historical Rust frontend was not changed.

The English/French MT9 clauses and mutable-access specification now state this
explicitly. No grammar production needed changing because named types and
qualified calls already have generic productions.

## Focused validation

The development compiler is `build/ordinary-lock-types/corboc`, built with the
preceding validated compiler and the pinned STD. The `declared` fixture defines
ordinary nongeneric `Mutex` and `AsyncMutex` objects, their own constructors and
methods. One method explicitly carries a lock contract, while the other does not.
The program executes under O1/fatal UBSan and prints two true observations.

Three negative fixtures use undeclared `Mutex<i64>`, `AsyncMutex<i64>` and an
ordinary `OtherName<i64>`. All three reject with the same unknown-type rule (1),
without a builtin unsupported-type fallback. Fixtures are in
`validation/fixtures/ordinary_lock_names`; results are retained in
`validation/ordinary-lock-names-results.json`.

These checks concern parsing/resolution on the macOS ARM64 host. No runtime/ABI
or platform backend changed, and no broader/platform suite was rerun for this
name-resolution cleanup. Source inspection finds neither name nor its encoded
name-specific checks in the active lexer/declaration modules.

## Follow-up object-level contract

This name-resolution cleanup itself introduces no object shorthand. The subsequent
user-approved implementation adds `#(lock)` independently of concrete type names;
see [the object-lock cycle](OBJECT_LOCK_CYCLE.md). Native locking remains developer-owned.
