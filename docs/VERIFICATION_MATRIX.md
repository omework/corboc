## Configurable constants and HTTP parsing

| Mechanism / rules | Executed evidence | Scope and limits |
| --- | --- | --- |
| CC1–CC7 / N1 | Default, nested, transitive, escaped layout, alias, type and visibility checks | Bounded literal/constant-reference specialization |
| N4/N5/N6 | Reader destruction refused; per-field Result/Option summaries and four existing aggregate/borrow regressions | Covered shapes only; no independent safety claim |
| HTTP budgets / framing | Partial reads, both roles, chunked trailers, body boundaries, EOF/errors and all four budgets | Synchronous injected reader on macOS ARM64 |
| Reconstruction / documentation | Identical self-emitted C; reference inventory check | Published STD pinned; installed automatic discovery validated |

37 focused checks complete. [Evidence and limits](CONFIGURATION_HTTP_CYCLE.md).

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


## Package-root build defaults (build/CLI)

| Mechanism | Executed evidence | Limits |
| --- | --- | --- |
| Manifest selection / output paths | Defaults, configured and empty [bin], -o forms, package paths with spaces, directory creation and reuse execute. | Nine build-and-run commands on macOS ARM64 |
| Existing package resolution | Two modules, path dependencies, STD imports and both [bin]/[dependencies] orders execute. | Existing pinned STD; no language-rule change |
| Diagnostics / publication | Eight expected failures, prior binary hash preservation and temporary-workspace cleanup pass. | 18 focused checks overall; other native build drivers remain unimplemented |

[Report and reproduction](PACKAGE_BUILD_DEFAULTS_CYCLE.md).


## Canonical corbo-lang repository (organization)

The source lock now targets corbo-lang's initial snapshot. Source-lock and
runtime-resource checks, a pinned install build and the new checkout's package
smoke test pass on macOS ARM64. Emitted compiler C matches the pre-migration
build byte for byte. No language or runtime implementation changed; no new
safety claim is made. See [migration evidence](CORBO_REPOSITORY_MIGRATION_CYCLE.md).

## Pool construction and fallible allocation

- PASS: 11 focused native O1/fatal-UBSan programs and nine expected refusals.
- PASS: owned Result cleanup/dependency summaries and scalar `?` forwarding.
- PASS: byte-identical stage2/stage3 self-emission and explicit development-runtime resource freshness.
- Scope: macOS ARM64; no broad corpus or independent audit, STD/runtime pinned to `600b409a0edae3112fd0dd68e246cd0798a0a666`; clean cache and embedded-runtime freshness checked.
- Known limitation: complex owned-Result function signatures; existing iterator example fails in baseline and candidate.

See [cycle report](POOL_CONSTRUCTION_TRY_CYCLE.md).

## Bounded strings, binary encoding and time — executed integration

| Mechanism / rules | Executed evidence | Limits |
| --- | --- | --- |
| TX23 fixed inline UTF-8 | Capacity, literal/qualified identity, UTF-8 boundaries, TooLong unchanged, zero capacity, moves and pool borrows | Native padding is not a portable disk layout |
| N4 / N5 / N6 dependencies and moves | Rejected byte/text/pooled view escape, conflicting mutation, moved reuse and private construction; Result text source retained | Scoped probes, not a general proof |
| Explicit binary endianness | LE/BE integer/float reads and writes, extrema, short buffers and bool errors | 64-bit supported targets; no exhaustive bit campaign |
| Time API | Monotonic blocking/async deadline probes on macOS/Linux ARM64+x86-64 and Windows x86-64 | Wine Windows execution; Windows ARM64 compile-only; worker-per-wait |
| Core reconstruction | Byte-identical stage2/stage3 with updated STD; constant and generic regressions pass | Published STD pin updated to the committed lot; cache checked |

Nine focused host UBSan executions, ten expected refusals and two related UBSan
regressions completed. Three API and three bounded-layout probes per non-host
target completed as detailed in the report. No independent audit claimed.

[Cycle evidence](BINARY_TIME_BOUNDED_CYCLE.md).

## Async-default API organization

No new normative rule. Existing resource/borrow checks are exercised through the
new default async and explicit sync imports. Buffered File borrow refusals,
TCP split lifetime refusal and TLS privacy/refusal regressions are retained.
Targeted executions cover macOS ARM64/x86-64, Linux x86-64 (timers also ARM64),
Windows x86-64 under Wine; Windows ARM64 is compile-only. Runtime primitives
are unchanged. [Cycle report](ASYNC_DEFAULT_API_CYCLE.md).

## Package scaffolding CLI

No new language rule. Ten focused checks cover creation/build/run, no-overwrite
behavior and malformed names/arguments on macOS ARM64. The production module
also executes on macOS x86-64, Linux x86-64 and Windows x86-64; Windows ARM64 is
compile-only. Partial-directory rollback and hostile filesystem races are not
claimed. [Evidence](PACKAGE_NEW_CYCLE.md).
