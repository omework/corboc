# Definition-local methods and arrow-free returns

## Scope

Core/grammar change approved on November 24, 2026. Methods and associated
constants are declared inside structs/enums, after semicolon-terminated fields
or variants. Function, structural-contract, callable-type and explicit closure
result types follow their parameter lists without an arrow. Omitted results and
explicit `()` share the existing unit-return representation.

Typed receivers constrain existing parameters of the enclosing type. Shared,
mutable and consuming receivers retain the ordinary permissions, ownership and
lifetime rules. Nested constraints reuse the existing recursive instance unifier.
Unavailable specializations and receivers naming another owner produce N1
messages rather than a generic compiler-limitation diagnostic.

The frontend normalizes definition-local methods to the existing method-owner
AST nodes before package linking. Source maps and file boundaries are composed
through this pass. Constructor commas, array-length semicolons, comments,
strings and native C/assembly bodies keep their original meaning. Lex-only output
continues to describe the original tokens. Normalization and specialization use
the existing 1,536 Ki-token package budget consistently.

## Migration

- Migrated 102 STD files and 102 compiler source files, including return syntax
  in the generated runtime bridge and its generator. Runtime payloads are unchanged.
- Migrated 23 complete feature-example sources, English/French README snippets,
  the reference grammar and the source-documentation inventory.
- Added the bilingual `docs/DEFINITION_METHODS.md` specification in Corbo.
- Regenerated the STD reference: 104 files and 1,771 documented entries. Runtime
  reference inventory remains 41 files and 921 entries.
- Retained legacy `impl` and arrow-return parsing for older bootstrap inputs and
  generated specialization recipes. New reference syntax uses inline methods.
- Left the frozen Rust frontend and historical corpus/report sources unchanged.

An isolated legacy-syntax source view bootstrapped the transition using the
previous installed seed. Subsequent builds used the migrated Corbo sources and
migrated STD directly. Temporary bootstrap artifacts are confined to `build/`.

## Executed evidence

Host: macOS ARM64. No broad corpus, mutation campaign or platform runtime change.

`python3 scripts/validate_definition_methods.py` completed six observations:

1. Execute struct/enum methods, associated constants, typed shared/mutable/value
   receivers, tuple results, explicit unit results and arrow-free callable/closure
   signatures under fatal UBSan.
2. Execute concrete i64/bool method selection and a nested
   `Container<Inner<i64>>` receiver constraint under fatal UBSan.
3. Reject a method unavailable on the concrete specialization with N1.
4. Reject mutation through a shared receiver with N5.
5. Reject a borrowed receiver naming a different owner with N1.
6. Reject use after a consuming method call with N6 and the move location.

[Recorded results](DEFINITION_METHODS_RESULTS.json).

Adjacent STD validation completed both `validate_binary_orders.py` observations:
60 endian methods/35 assertions and target selection before import resolution,
under fatal UBSan. No rerun of unrelated API suites.

The rebuilt compiler was generated from current migrated sources using a
self-hosted compiler, then executed the focused observations. Its matching STD
and binary were installed at `build/check-file/install/`; the installed compiler
also successfully checked the inline-method package.

The diagnostic catalog audit reports 1,021 sites and 353 observed state writes.
`stdlib_docs.py --check` passes for STD and runtime inventories. These observations
are not a general proof of language-rule enforcement.

## Installation and limits

Installed compiler SHA-256:
`b94f253d85901225a011194546f2661f433dd2ac46a35f7fc4e5af66f1568d4d`.

The STD/runtime/specification pin is committed Corbo revision
`ccbeff271605a7a7c3b35d9105c41c2dd07031c2`. The installed STD matches the pinned snapshot byte for byte;
its temporary development override has been removed.
Linux/Windows execution was not repeated for this frontend-only change.
Windows ARM64 execution remains deferred as previously agreed.
