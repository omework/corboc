# Instance methods on user-defined types

Scope: corboc checking and code generation. No grammar, ownership rule, STD,
runtime ABI or frozen Rust frontend change.

## Implementation

Instance-method lookup and lowering now accept both nominal declaration kinds:
structs and enums, including their existing generic specializations. An enum
receiver no longer hits a struct-only guard before its body is checked.

`&self` and `&mut self` use the existing receiver reservation, lifetime and
mutation-permission checks. `match self` on an existing enum reference inspects
borrowed storage; it does not consume the enum. Explicit `match &mut *self`
retains the existing mutable payload binding behavior. Nominal identity can be
recovered from an implementation receiver, including when assigning a primitive
enum through `*self`.

`self: Type` is an ordinary by-value argument. Receiver identity must match the
implementation owner; field/dependency admissibility is checked through the
normal function signature path instead of a second struct-layout restriction.
Primitive-only enums retain implicit copying. Other enums move and cannot be
used again. Enum parameters containing destructible owned data use the existing
owned-data predicate, not the replication/trivial-destruction predicate.
Cleanup follows the existing function and enum ownership lowering.

User-defined types currently have struct and enum declarations. This change
covers those nominal families; it does not introduce extensions to primitive
or builtin types, traits, or additional declaration forms. Enum variants retain
the existing `Enum.Variant` spelling, including inside match patterns.

## Validation

Focused evidence is recorded by `scripts/validate_enum_methods.py` in
`build/enum-methods/evidence/results.json`. The fixture covers borrowed and
mutable receivers, enum-valued returns, calls through a borrowed argument,
primitive-enum copies, a consuming receiver with owned resource cleanup, generic
enums, generic structs and a consuming struct containing a borrowed field. Refusals cover mutation without permission, mutation
through a shared reference, use after move, and destroying a still-borrowed
receiver. Executable output is checked under fatal UBSan.

The existing enum integration suite covers values, equality, copies, ownership,
pattern binding and ten refusals. Validation status and installation are tracked
in the implementation checklist. Platform-specific runtime code is unchanged;
execution is on macOS ARM64, not a replay of all platform suites. Windows ARM64
execution remains deferred.

### Completed execution

The focused fixture and all four refusals pass. All four existing enum execution
fixtures and ten refusal cases also pass against the final compiler. Executables
were compiled with `-fsanitize=undefined -fno-sanitize-recover=all` and their output
was checked. Results are in `build/enum-methods/evidence/results.json` and
`build/enum-methods/regressions-final/results.json`.

The compiler rebuilt itself from current sources using the pinned STD/runtime,
without a source override. The resulting binary was installed atomically at
`/Users/jabarkarim/sources/corboc/build/check-file/install/bin/corboc`.
Shell PATH resolution returns that exact path, and the installed compiler checks
the complete method fixture successfully. Restart existing watch processes to
use the new binary. No SubDB source was changed; no commit or push was performed.
