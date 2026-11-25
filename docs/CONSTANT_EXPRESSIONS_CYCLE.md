# Literal-based constant expressions

Scope: compiler/core grammar and pre-verification configuration reduction.
The frozen Rust frontend and runtime are unchanged.

## Implementation

- `parse_constant` retains an ordinary expression AST rather than requiring an
  immediate numeric/bool literal.
- `configuration/evaluation.crb` reduces primitive/text literals, constant reuse,
  parentheses, unary minus, numeric `+ - * / %`, min and max. It rejects other
  calls, owned/aggregate values, mismatched constant types and dependency cycles.
- Integer sign/magnitude evaluation handles full u64 and signed minimum bounds
  without overflowing the compiler. Floating conversion/formatting uses a small
  native numeric boundary; f32 operations retain f32 precision.
- Empty environment entries mean “evaluate the original default here”. Explicit
  overrides materialize values in their parent environment and are inherited
  without re-evaluating their RHS. Derived defaults follow dependency overrides.
- Numeric declarations retain their type and receive canonical literals. Text
  constants reduce to the existing static UTF-8 literal representation at uses.
- A token-indexed map locates constant declarations/text uses; named array bounds
  and repetition lengths use the same evaluator. Existing reserved-name and
  declaration-collision checks run before text declarations are removed.

## Executed validation

`scripts/validate_constant_expressions.py` passed three programs with fatal UBSan:

1. Associated derived bounds, type layout and nested override precedence.
2. Primitive/text reuse, integer extrema, signed minimum remainder, min/max,
   parentheses, exact primitive width and f32/f64 arithmetic.
3. Module/helper specialization, unmarked derived constants, text overrides and
   simultaneous assignment evaluation in the parent environment.

Twelve refusals cover overflow, zero divisor, signed division overflow, cycles,
reference type mismatch, user calls, aggregates, min arity, text arithmetic,
invalid text initializer, unsupported unary operator and override overflow.

The adjacent mixed-member suite passed five executable programs under fatal
UBSan and three refusals: interleaved struct/enum definitions, Self aliases,
associated array bounds, scoped configuration and imported methods.

## Rebuild and installation

Reconstructed the modified compiler with the new compiler generation using
`scripts/build.py`, then atomically replaced:

`/Users/jabarkarim/sources/corboc/build/check-file/install/bin/corboc`

Binary SHA-256: `fae89ebeb166dd22c5e15376521ef551780146751516be298725d7f87f04aaed`.
The unchanged STD/runtime remains pinned to `1dad04f671b975b9018ffdc67e2cd515d1ff453f`.
No commit or pin update is part of this working-tree change.

Installed-command smoke output for `GROUP_SIZE = 4096 * Self::FRAME_SIZE`:
`4194304`, then `8388608` under the override, then `4194304` outside it.

## Limits

Executed on macOS-26.6.2-arm64-arm-64bit-Mach-O. No Linux/Windows execution or full
three-generation fixed-point campaign was performed in this focused cycle.
The existing 256 marked-constant / 256 environment limits remain; expression
and dependency nesting is bounded at 128. Arbitrary compile-time function
execution, structs and owned collections remain outside the agreed scope.

[Focused results](CONSTANT_EXPRESSIONS_RESULTS.json) and
[adjacent regressions](CONSTANT_EXPRESSIONS_MEMBER_RESULTS.json).
