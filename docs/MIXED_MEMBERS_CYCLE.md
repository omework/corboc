# Unrestricted definition members and scoped Self

Date: 2026-11-24. Core/frontend change; no ownership or borrowing rule change.

## Implementation

Struct and enum fields/variants, associated constants and methods have no required declaration order. A token-aware partition retains the existing field and method owner ASTs while preserving their relative order within each internal group. Native blocks remain opaque, including embedded operand tokens. Moved source spans retain their diagnostic offsets.

Array bounds and repetition counts resolve associated constant paths (`Type::NAME` and `Self::NAME`) before layout. Configurable constants use the effective lexical environment. The pre-existing module-symbol path remains available for unqualified module constants. Unqualified associated names have not become module globals.

Self aliases resolve against enclosing structs, enums or compatibility implementation owners, rather than requiring the internal implementation node. The outside-type diagnostic now says that Self requires an enclosing struct or enum type.

The grammar and English/French definition guides remove the field-first restriction. The source documentation inventory scans the entire body, including fields after methods/constants. No declarations were lost across 122 existing Corbo source files; the inventory also recovers Reduce.finished, previously missed after a callable field. Generated STD/runtime references pass their freshness check.

## Executed evidence

[Results](MIXED_MEMBERS_RESULTS.json): eight focused mixed-definition observations (five fatal-UBSan executables and three refusals), 14 annotation observations and six existing definition/receiver observations pass on the final candidate. The Tracker witness uses a configurable u16 associated constant before its fields, a tuple/enum array bound via Self, and lexical capacities 5 / 7 / 5. Additional cases cover interleaved enum variants and methods, qualified ordinary constants, module constants, Self constructors and signatures, unknown/runtime bounds and Self outside a type.

A temporary copy of the current SubDB WAL file also checks successfully after qualifying its two associated constant names and their uses with Self::. The user's live file was not edited. It currently uses unqualified associated names in those bounds, which remain invalid under the existing qualification semantics.

The rebuilt compiler is installed at the existing PATH with its matching pinned STD. The grammar/documentation revision is recorded in the publication note below. Runtime/STD code did not change. Execution is macOS ARM64; no new Linux/Windows execution or general safety proof is claimed.

## Publication

Corbo grammar, documentation and inventory are published at `1dad04f671b975b9018ffdc67e2cd515d1ff453f`. `corbo.lock` now pins that commit. STD/runtime code is unchanged relative to the validated pin; runtime-source consistency was checked during publication.

The published reference refresh passes HTTP/asset validation and resolves 94,259 local links across 522 HTML pages and 2,183 searchable entries. See `OFFLINE_REFERENCE_RESULTS.json`.
