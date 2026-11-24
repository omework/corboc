# Compound await propagation: explicit slice argument diagnostics

Scope: compiler/core diagnostics, with no grammar, language-rule or STD API change.

## Diagnosis

The reported `cursor += self.file.write_at(buf[..], cursor).await?` was not an
unsupported compound assignment or suspension. The explicit-borrow form
`cursor += self.file.write_at(&buf[..], cursor).await?` already compiles and runs.
`check_slice_argument` returned an unsupported-feature sentinel for the bare range
expression, which the outer statement reported as E0009. Binding the same call
to a local produced the same false compiler-limitation category.

## Change

Bare range expressions, including parenthesized ranges, now produce N1 failures
1018/1019 for shared/mutable slice parameters. Their messages name the required
explicit borrow, show the expected signature and unborrowed actual expression,
and suggest the source spelling with `&` or `&mut`. The source location is the
argument, with the relevant parameter location retained. No implicit borrow is
inserted; no expression is evaluated to manufacture a diagnostic. Other
unsupported operand forms retain their existing classification.

## Focused validation

`scripts/validate_compound_await.py` contains four observations:

- A real async File `write_at` compound assignment while a sibling tracker guard
  stays live, writing two bytes.
- An indexed assignment with an effectful index and an RHS that yields. Success
  changes 40 to 42; error propagation leaves 40 unchanged. Each index is
  evaluated exactly once. Both paths return their expected Result.
- The File call with an unborrowed range, requiring a shared-borrow diagnostic.
- `binary::write_u16_be` with an unborrowed range, requiring a mutable-borrow diagnostic.

The two positive programs pass on the existing compiler with fatal UBSan,
confirming the lowering already supports this syntax. All four observations pass on the final rebuilt compiler. The two source errors
produce N1, their exact expected slice types, the correct argument locations,
and complete `&data[..]` / `&mut buffer[..]` suggestions. Suggestions preserve
punctuation while mapping identifier tokens to their original source names.

The existing semantic-diagnostic suite also passes: eleven rejection observations,
an accepted observation, raw-protocol checks and the diagnostic-site audit
(1,019 sites, 353 observed state writes). No unrelated test campaign was run.

The installed binary is `build/check-file/install/bin/corboc`, unchanged from the
shell PATH setting. SHA-256:
`b413347a2d692cf9182522a92b4361fb3dd300ba5c85578edde47ae51702c43f`.
The actual unchanged WAL now reports N1 at line 117, column 38, with
`expected: &[u8]` and `help: pass an explicit shared borrow: &buf[..]`.
Results are retained under `build/compound-await/results.json` and
`build/slice-argument-install/semantic-results.json`.

Validation is limited to macOS ARM64 and these affected paths. No platform code
changed. No broad rule-breaking campaign or frozen Rust frontend change was
performed. Windows ARM64 execution remains deferred.

SubDB source is unchanged. Fixing its missing borrow can expose further source
errors; this diagnostic change does not claim the whole WAL compiles.
