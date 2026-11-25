# Primitive Option fields in struct constructors

Scope: compiler/checker and C declaration ordering. No grammar or normative-rule
change. `new` remains an ordinary associated method and `Self` remains the
existing enclosing-type alias.

## Failure

The corrected Dispatcher initializer was valid. The checker routed
`limit: Option<usize>` through its generic allocation-field fallback and returned
an unsupported-operand status for `limit: None`. Constructor calls also failed
because value-only aggregate classification excluded the Option field.
The diagnostic's struct-level anchor obscured that underlying limitation.

## Fix

- Supply the declared primitive Option field type to normal expression checking
  for None, Some and existing Option variables.
- Recognize primitive Option fields when classifying value-only aggregates for
  function return and argument contracts.
- Decode field projections through the normal place, mutation-permission and
  live-loan checks. Primitive Option copy eligibility remains unchanged.
- Emit required primitive Option layouts before their enclosing C struct and
  suppress repeated declarations in later Option/Result emission.

The shared classification admits only Options with primitive payloads. It does
not grant implicit copying to arbitrary nested/resource-bearing envelopes or
introduce additional borrowing forms.

## Validation

Results are recorded in [OPTION_FIELDS_RESULTS.json](OPTION_FIELDS_RESULTS.json).
The focused program covers the exact Dispatcher constructor and its scoped
capacity override, followed by Some construction, parameter reuse, field reads,
field mutation and bool payloads. Two refusals retain payload type checking and
array length checking.

Executed on macOS-26.6.2-arm64-arm-64bit-Mach-O: both programs compiled and ran under fatal
UBSan with outputs `16 / 0 / 3` and `42 / 1 / true`. Both invalid programs were
rejected. The eight adjacent member/Self/array-bound regressions also passed
(five executable programs under fatal UBSan and three refusals).
[Adjacent results](OPTION_FIELDS_MEMBER_RESULTS.json).

Reconstructed corboc with the modified compiler generation and atomically
installed it at `/Users/jabarkarim/sources/corboc/build/check-file/install/bin/corboc`.
Binary SHA-256: `4933485dbcd46f9fc17465fb2b6e614348283421a34a42e099f51f9cd9c9c69a`.
STD/runtime pin remains unchanged. No commit or push was performed.
No Linux/Windows execution or broad corpus campaign was run in this focused
compiler cycle.
