# Implicit primitive copies

Date: 2026-11-22. Approved core semantic change (V3/N3/N6); no new grammar syntax.
The Rust frontend remains frozen and retains historical behavior.

## Implementation

Primitive type codes 1–9 (i32, i64, u8/u16/u32/u64, usize, bool, f32/f64)
copy in by-value evaluation. Assignment, arguments, primitive results and
constructed primitive fields leave the source available. Named primitive inputs
are reads for loan checking, rather than resource transfers. Scalar branch and
tuple summaries no longer record these as moves or reject repeated primitive
bindings. C lowering already emits scalar value assignments; no lowering or
runtime change was required.

Structs, arrays, tuples, references and allocation handles retain their existing
move rules. An all-primitive struct is not implicitly copied. Special drop and
explicit scope-transfer directives retain their semantics. Raw usize copies
retain origin/dependency metadata, both for implicit assignment and explicit
copy(), so copying does not bypass unchecked confinement or target validity.

## Executed evidence

One integrated fatal-UBSan executable covers every supported primitive type,
initialization/reassignment, independent destination mutation, repeated by-value
calls and returns, scalar/tuple branch results, Option match and loop results,
shared borrowing, primitive constructor fields, optional explicit copy,
a primitive copy surviving source drop, async argument capture and once-only
cleanup of a moved owning struct. The output contains 20 true observations,
expected integer results and one destructor trace, recorded in JSON.

Eight focused refusals preserve array/tuple/record/reference ownership,
non-primitive copy rejection, use after explicit drop, copied-address escape
and target destruction before a copied address's use. The latter reports rule 5;
address escape reports rule 4. No raw pointer value escapes the unchecked block.

Five updated README packages execute with fatal UBSan and their independently
specified output: budget, tuples, moves, regions and map. The existing iterator
example is unchanged: both the previous and updated compiler return parse status
7 for its original source. That pre-existing issue is separate from V3 and was
not expanded into pipeline work here. Historical explicit-copy examples remain
valid spellings; this change does not require removing every existing copy().

Scope: macOS ARM64 execution, shared verifier behavior and directly affected
examples. No broad corpus, mutation campaign or fresh cross-platform execution
was performed; no safety proof is claimed.

## Reproduction

From corboc:

```sh
python3 scripts/validate_implicit_primitives.py --compiler build/implicit-primitives/install/bin/corboc
```

See IMPLICIT_PRIMITIVE_COPY_RESULTS.json for outputs and exact refusal statuses.

## Installed reconstruction

Reconstructed corboc against Corbo revision
`dd44494d08ba8ca67d01da14936a1cef1f410541`. The installed binary passed
the same focused positive/refusal suite. Normal `corboc check` and `corboc build`
resolve the installed STD and accept the documented implicit-copy example; its
executable prints `36`. This is one reconstruction, not a multi-generation
bootstrap equivalence check.
