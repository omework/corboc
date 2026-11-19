## Documentation coverage follow-up

| Rules / mechanism | Executed evidence | Scope and limits |
| --- | --- | --- |
| N1/N8: structural contracts and numeric/text typing | Concrete function candidates, inferred output, forwarding, numeric bounds/exactness and descriptors executed. | Nine historical observations resolved; bounded expansion remains. |
| N4/N5/N6: returned loans, native boundary and lock lifetime | Explicit borrowed returns and relays, C operands, persistent aggregate lock results, drop release and expected invalid variants. | Targets and reservations checked through existing dependency graphs; arbitrary result shapes not claimed. |
| N7 and composition regressions | Buffered sink flush, callable cleanup/iterator composition and actual resource decoder all execute under fatal UBSan. | 26 executions, 20 expected refusals, two runtime-only accepts and five packing round trips on macOS ARM64. |
| Bootstrap and traceability | Final compiler installed; self-emitted C byte-identical; all 33 README blocks synchronized. | One reconstruction comparison, no full historical/platform campaign or independent audit. [Report](DOCUMENTATION_COVERAGE_CYCLE.md). |

# Compiler extraction verification matrix

| Property | Evidence | Status |
| --- | --- | --- |
| Compiler source preservation | 81 source/package files compared before removal of the old directory; only generated-resource metadata and one source comment differ. No language algorithm changed. | Complete |
| Shared-source identity | One exact revision for STD/runtime/spec, checked cache and regenerated resource. | Six source-lock checks passed |
| Self-hosting and installed STD discovery | Two rebuilt generations, byte-identical emitted compiler C, normal self-build and external two-module program. | Complete on macOS ARM64 |
| Compiler mechanisms | Core-extension, generic/tuple and C runtime bridge regression suites. | Three suites and historical forwarder completed on macOS ARM64 |

The full language-rule matrix and historical platform evidence remain in the
language repository at the revision named by `corbo.lock`. This table records
only extraction evidence; it is not a new safety audit.

[Detailed executed evidence and limits](REPOSITORY_SPLIT.md).

## Corbo runtime integration

| Property | Executed evidence | Scope |
| --- | --- | --- |
| Freestanding runtime boundary | Two scalar accepts, six managed/unchecked-boundary refusals; normal application suites passed. | Host macOS ARM64; no new language rule |
| Resource packing | Five independent round trips and actual Corbo decoder execution across 64 KiB history wrap under fatal UBSan. | Controlled generated resources, not an untrusted-stream API |
| Integrated runtime | Core-extension, generic/tuple/registry and C bridge suites passed; pinned Corbo implementation selected by default. | Host; platform runtime comparisons and network runs recorded in the language cycle report |

[Corbo runtime cycle](CORBO_RUNTIME_CYCLE.md).

Pinned reconstruction completed: three byte-identical generated compiler C files,
normal compiler self-build and external two-module program printing `42`.
Native compiler execution remains macOS ARM64 evidence.

## Bare type declarations

Bare `#(type: V)` parsed successfully; `#(type: V *)` was rejected. Existing
usage-site type-list syntax parsed successfully. The spaced Reader package
compiled and executed with stdout `42` at O1 under fatal UBSan. One successful
compiler build was performed; no broad suite or full self-reconstruction ran.
The matching source pin is `0e49415`. Details are recorded in the language
repository's `docs/cycles/BARE_TYPE_ANNOTATION_CYCLE.md`.

## General callable integration

| Rules / mechanism | Executed evidence | Scope |
| --- | --- | --- |
| N1/N8: concrete callable signatures and passing modes | Direct/immediate calls, owned/shared/mutable parameters, owned mutable parameters and forwarding executed; incompatible signature refused. | macOS ARM64, O1 and fatal UBSan |
| N2/N3/N6/N7: capture, move and cleanup | Automatic capture copy, explicit move, persistent mutable state and a distinct single destructor marker executed; missing move and consumed-binding reuse refused. | Six focused programs in the compiler suite |
| N4/N5: capture dependencies and reborrows | Shared/exclusive captures, local record reborrow and target access after cleanup executed; early target mutation, shared mutation and local-target escape refused. | Existing loan/constructor contracts reused |
| Iterator composition / documentation | Callback plus STD filter/map/reduce/collect executed; updated README and former rejected fixture also executed. | Eight distinct programs and seven refusals overall; no broad corpus or platform rerun |

[Detailed results, reproduction and limits](GENERAL_CALLABLES_CYCLE.md).


## Borrowed text splitting

| Rules / mechanism | Executed evidence | Limits |
| --- | --- | --- |
| TX1/TX4, N1 | UTF-8 views, byte contents, optional text results and generic Iter forwarding execute. | macOS ARM64, O1 with fatal UBSan |
| N4/N5/N6 | Piece/cursor and separator independence execute; early destruction and mutation refused. | Twelve successful programs and four refusals; existing per-field graphs reused |
| Direct regressions / build | Seven related cases, the README text package and a compiler rebuild pass; successive updated C emissions match. | No broad corpus, other-platform execution or independent safety audit claimed |

See [TEXT_SPLIT_CYCLE.md](TEXT_SPLIT_CYCLE.md).
