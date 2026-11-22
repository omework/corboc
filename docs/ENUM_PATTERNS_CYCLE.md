# Enum patterns, equality and implicit copies

Date: 2026-11-22. Approved core/compiler change: EN1 and V3; interactions with
N1 (typing), N3 (value semantics), N4/N5 (dependencies), N6 (availability) and
N7 (destruction). The Rust frontend remains frozen.

## Implementation

- `if let` parses any existing enum pattern using match nodes and scoped pattern
  bindings. Its subject is evaluated once before either arm. A synthetic wildcard
  represents else, or an empty no-op branch when else is absent. Both kinds of
  else-if chain normalize to ordinary scopes and reuse existing branch joins.
- Copy eligibility examines every variant. Only empty variants and direct
  primitive payload fields qualify; the current active variant does not change
  the decision. Eligible Option and Result instantiations follow that rule too.
  Bindings, reassignment, calls, returns, tuple/record fields, explicit copy and
  closure capture reuse the same value semantics. Other owners and references
  retain their existing behavior; copying a struct is not enabled.
- Equality evaluates both operands once, then compares their tags and active
  primitive fields. It never compares padding or inactive fields. Nominal enum
  identities must match; ordering and recursive aggregate equality are excluded.
- A selected owned payload moves into its binder. Ignored and unmatched fields
  are destroyed before the branch body; moved fields are cleared in the temporary
  to prevent duplicate destruction. Bound owners use ordinary scope/return
  cleanup. Explicitly borrowed matches retain their dependency on the target.
- Positional variant fields now receive distinct C aliases, including variants
  with several fields. The STD and runtime implementations are unchanged.

## Executed validation

Four focused programs compile and execute with fatal UBSan: the combined enum
features, equality across all primitive field types, ownership/borrow/destructor
behavior, and the updated README package. They cover named and positional fields,
else-if/value expressions, source availability after copies, copies through
functions/fields/tuples/closures, one evaluation of an effectful subject,
Option/Result, differing variants, payload differences and floating signed zero.
The destructor trace covers matched/unmatched ownership, shared/mutable borrows
and both early-return paths, with once-only destruction.

Ten refusals cover a wrong enum pattern, wrong arity, out-of-scope binder,
cross-enum binding/equality, aggregate-payload equality, a move-only enum whose
active arm is empty, use after drop, a missing else result, and destruction of
a target still used by a borrowed pattern.

The existing primitive-copy executable and its eight refusals also pass. They
retain coverage of non-enum owner moves, references and raw-address confinement.

The rebuilt compiler emits byte-identical compiler C to its seed's output for
the same current source. The package-level `check` command accepts the README
example with automatic installed-STD discovery.

## Limits

Execution was on macOS ARM64. No native backend or runtime code changed, and
Linux/Windows execution was not repeated. Windows ARM64 execution stays deferred.
This is bounded implementation evidence, not a new corpus campaign, independent
audit or proof of general safety. The language commit changes no STD/runtime
bytes; the compiler lock is advanced to that committed specification.

Committed STD/specification pin: `822dcf7198a5bf33ebd09eec17dcd8e7d8c97e1f`. STD/runtime source bytes are unchanged.
