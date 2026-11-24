# Definition-member annotations

Date: 2026-11-24. Scope: compiler/core parsing and specialization, grammar and documentation; no changes to ownership, borrowing or annotation-effect semantics. The Rust frontend remains frozen.

## Implementation

- Parse `#(configurable)` on associated constants in both struct and enum definitions, retaining the marker in the declaration's source span.
- Register package and associated configuration identities uniformly. Associated overrides specialize the enclosing nominal type and its implementations; member names stay stable and initializer values follow the lexical environment. Nested overrides inherit and restore their enclosing values.
- Lift independently generic associated functions without inventing a self parameter. Instance method promotion preserves the self spelling used by lock contracts.
- Infer the nominal identity of enum constructors in both qualified and normalized member/payload forms when selecting generic methods.
- Resolve synchronous and asynchronous generic recipes without broadening the verifier's ordinary synchronous-call resolver.
- Preserve branch and lock metadata while removing type-specialization recipes.
- Update member grammar, configuration and definition guides, editor annotation names, and the compiler reference. Generated signatures now display source annotations.

Annotations retain their existing targets: type/branch/lock on applicable methods and associated functions, configurable on constants, target selection around members, and block annotations on blocks. Invalid targets remain errors. This change does not introduce field annotations or redefine object-level annotation semantics or member visibility.

## Executed evidence

[Focused results](MEMBER_ANNOTATIONS_RESULTS.json): seven executables with fatal UBSan and seven expected refusals. Executed cases cover associated defaults, nested override inheritance/restoration, static and instance generic members on structs/enums, stacked lock contracts, generic async members, branch contracts, conditional members and an imported owner in a two-module package. Refusals cover incompatible annotation targets, unknown annotations, unmarked overrides and overflowing replacement literals.

[Existing definition-method regressions](MEMBER_ANNOTATIONS_DEFINITION_RESULTS.json): six observations pass (two executable cases and four refusals).

The offline reference graph resolves all 94,150 local links across 521 pages and 2,181 search entries. Rendered Mutex signatures contain their lock annotation. Python source syntax, VS Code JSON and Git whitespace checks pass.

Validation executed on macOS ARM64. No platform-specific runtime behavior changed. Linux/Windows execution was not repeated; Windows ARM64 execution remains deferred. These focused results are not a general language-safety proof.

The compiler was rebuilt with its existing self-hosted seed and installed at the existing PATH, together with its matching pinned STD and offline reference. The STD lock stays ccbeff271605a7a7c3b35d9105c41c2dd07031c2; publishing the language documentation and updating the pin are separate Git operations. No commit or push was requested.

## Publication

Corbo documentation and grammar are committed at `6007d05366476a31f9c4ba99c8d6ab55becaf77c`. The compiler lock now pins that revision. STD and runtime source code are unchanged by this documentation/grammar revision; the executable observations above remain those actually recorded before publication.
