## Definition-local method syntax

The current cycle covers inline method ownership, arrow-free result syntax and
concrete receiver selection. Existing move/borrow rules remain authoritative.
See [the cycle report](DEFINITION_METHODS_CYCLE.md) for executed observations and
bootstrap details. The frozen Rust frontend is not migrated.

## Tuple projections and for patterns

- [x] Distinguish tuple indices from leading-dot floats and accept numeric field suffixes.
- [x] Parse tuple loop patterns and normalize through ordinary tuple destructuring.
- [x] Connect tuple aggregate layouts, field dependencies and borrowed patterns end to end.
- [x] Execute six tuple examples under UBSan, check seven refusals and pass ten iteration regressions.
- [x] Self-rebuild and atomically update the local installation; two installed smoke checks pass.

[Evidence](TUPLE_ITERATION_CYCLE.md).

## Semantic diagnostic context

- [x] Attach failure-site descriptions and explicit expected/actual type metadata.
- [x] Observe checked-value writes without replacing verification assignments.
- [x] Add scoped diagnostic views, source labels and lifetime/move/borrow history.
- [x] Build and validate thirteen focused semantic observations, sixteen source-diagnostic regressions and ten iteration regressions.
- [x] Rebuild with the new compiler generation and atomically update the PATH installation; two installed smoke checks pass.

[Evidence](SEMANTIC_DIAGNOSTICS_CYCLE.md).

## Universal reference spelling and for loops

- [x] Specify exact ref/mut_ref equivalence and loop ownership semantics.
- [x] Add loop parsing and normalization through existing operations.
- [x] Validate indexed and next-based iteration, borrowing and cleanup (ten focused observations, plus sixteen diagnostic regressions).
- [x] Rebuild final source with the new compiler generation and update the local installation.

[Evidence](ITERATION_CYCLE.md).

## Interactive watch refresh

- [x] Clear the visible terminal before initial and repeated watch checks.
- [x] Preserve redirected logs, Unix `TERM=dumb` output and terminal scrollback.
- [x] Validate terminal refresh and redirected output on macOS ARM64; rebuild local installation.

[Evidence](WATCH_TERMINAL_CYCLE.md).

## Source diagnostics

- [x] Render filename, line, column, source excerpt and caret for check/watch/build.
- [x] Preserve original source provenance through linking and rewriting.
- [x] Distinguish rule failures, unsupported constructs and approximate anchors.
- [x] Explain common parser expectations and malformed for-loop headers (for syntax is now supported).
- [x] Preserve raw frontend protocols and reset provenance on each watch pass.
- [x] Validate sixteen focused diagnostic observations, thirteen package regressions and seven file/watch observations on macOS ARM64.

[Evidence](DIAGNOSTICS_CYCLE.md). No grammar or normative-rule changes.

## File check targets and dependency watching

- [x] Accept standalone and package-backed `.crb` targets with existing static verification.
- [x] Resolve STD imports and allow library-file checking without `main`.
- [x] Watch transitive local path dependencies and installed STD; refresh manifest graphs.
- [x] Preserve package checking, debounce, source deletion/recovery and ignored outputs.
- [x] Execute seven focused file observations and thirteen package regressions on macOS ARM64.

[Evidence](FILE_CHECK_WATCH_CYCLE.md). No language-rule changes or broad corpus run.

## Bounded sync/async channels

- [x] Implement bounded FIFO transport, ownership-preserving failure and close/drain.
- [x] Integrate native condition waits and authenticated async wait registration.
- [x] Preserve typed cleanup and payload thread-transfer restrictions.
- [x] Carry owning Option results through general Future verification/lowering.
- [x] Execute three combined API programs, five refusals, both runtime witnesses and adjacent mutex regressions.
- [x] Validate macOS ARM64, Linux x86-64 and Windows x86-64; link Windows ARM64 with execution explicitly deferred.
- [x] Document payload integration limits and regenerate the STD/runtime references.

[Evidence](CHANNELS_CYCLE.md). No broad corpus or adversarial campaign.

## Enum patterns, equality and copies — EN1 / V3

- [x] Parse if-let, else-if chains and value expressions through match/scopes.
- [x] Share whole-definition eligibility across enum copying and equality.
- [x] Preserve moves, borrows and once-only payload destruction.
- [x] Execute four fatal-UBSan programs, ten refusals and primitive regressions.
- [x] Rebuild corboc, compare emitted compiler C and check the README package.
- [x] Align grammar and EN/FR documentation and examples.

[Evidence](ENUM_PATTERNS_CYCLE.md). macOS ARM64 execution; runtime unchanged.

## Implicit primitive copies — V3

- [x] Copy primitive by-value inputs and keep their sources available.
- [x] Preserve non-primitive moves, borrowing, drop and address provenance.
- [x] Execute all ten primitive types, joins and eight refusals; validate five updated README examples.
- [x] Update EN/FR rules and references. Leave the independently failing Iter example unchanged.

[Evidence](IMPLICIT_PRIMITIVE_COPY_CYCLE.md). macOS ARM64 execution; no new broad audit.

## Positioned File API integration

- [x] Advance STD pin to the committed read_at/write_at implementation.
- [x] Existing corboc accepts sync/async API and refuses owner destruction with a pending read.
- [x] Record platform witnesses and Windows resource cleanup; ARM64 execution deferred.
- [x] Extend test-only target-emitter tooling with the ARM64 selector.

[Evidence](FILE_POSITIONED_CYCLE.md). No compiler/core implementation changes.

## Package check/watch CLI

- [x] Share package resolution and verifier-only mode; no code generation.
- [x] Watch source/manifest content with debounce and recovery after errors.
- [x] Execute focused package, dependency, error and watch tests on macOS ARM64.
- [x] Probe the native executable-location boundary on macOS/Linux/Windows x86-64.

[Evidence](PACKAGE_CHECK_CYCLE.md). Full cross-platform CLI runs were not repeated.

## Mutex API namespaces

- [x] Move Mutex/MutexGuard to `std::sync` and `std::sync::asyn`.
- [x] Update private compiler bindings, docs and examples.
- [x] Run three fatal-UBSan programs and ten existing refusal checks.

[Evidence](MUTEX_NAMESPACE_CYCLE.md). Runtime unchanged; platform results retained.

## Synchronous defaults / shared-reference mutexes

| Rules / mechanism | Executed evidence | Limits |
| --- | --- | --- |
| API paths / N1 | Six README programs and async buffered File/TCP | Existing signatures retained; no async TLS |
| N4/N5/N8 | Per-field async results; three shared writers, scalar/aggregate guards, lifetime/re-entry refusals | Conservative cases remain; no safety proof |
| N2/N6/N7 | Guard move, payload destruction, terminal compound/indexed cleanup; FIFO waiter detach/handoff | Focused observations only |
| TR1 | Native guard transfer and suspension refused; async guard survives yield | Windows ARM64 compile-only |
| Runtime / ABI | Both queue implementations and existing metrics ABI checks | macOS, Linux Docker, Windows Wine |

[Evidence](SYNC_DEFAULT_MUTEX_CYCLE.md).

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

## Lexical-binding cleanup on `?`

N7/N8 backend correction: lexical blocks no longer contribute binding nodes to
partial-expression temporary cleanup. A focused destructor trace executes under
O1/fatal UBSan; Subdb integration and early-error paths execute as related
regressions. This does not strengthen or change normative rules.
[Report](SUBDB_PROPAGATION_CYCLE.md).

## SubDB static facade and owned fixed fields

Existing SC structural contracts and N4–N8 mechanisms: contracted instance-method
promotion, payload-type inference through `?`, structural fixed-value summaries,
inline owned array fields, disjoint call places and moves into fixed arrays.
Four accepted programs execute with fatal UBSan; three invalid forms reject.
The SubDB facade additionally exercises separate native reader threads, owned
results and selected-index boundaries. No normative-rule change, Rust frontend
update or general safety proof. [Report](SUBDB_FACADE_CYCLE.md).

## Mutation permission revision — implemented, focused evidence

MA1–MA6 revise N5 so that `&mut` supplies no uniqueness assumption. Separate
permission and protection/effect facts admit mutable aliases and content-only
calls; destruction and unresolved effects keep lifetime checks. Nineteen checks
complete: nine fatal-UBSan executions and ten refusals. Native same-lock captures
execute on macOS ARM64/x86-64, Linux x86-64 and Windows x86-64 under Wine;
Windows ARM64 compiles only. The scope is focused, not an independent safety audit.
[Report and limits](MUTABLE_ACCESS_CYCLE.md).

## Ordinary lock names

N1/N8 name resolution: former Mutex/AsyncMutex names resolve as normal user types.
One two-observation program executes under fatal UBSan, including an explicit
method lock contract. Three undeclared names receive the same rule-1 rejection.
No runtime or ABI change, platform replay or object-level annotation implementation.
[Report](ORDINARY_LOCK_NAMES_CYCLE.md).

## Object-level lock contracts

MT11/N5: bare struct markers derive public instance receiver contracts. Six
accepted fixtures execute under O1/fatal UBSan; ten refusals cover re-entry,
possible aliasing and malformed placement. Three explicit retained-lock regressions
pass. The native thread witness executes on macOS ARM64/x86-64, Linux x86-64 and
Windows x86-64 under Wine; Windows ARM64 compiles only. Self-emission is identical.
No native locking implementation or frozen Rust frontend was changed.
[Report and conservative-analysis limits](OBJECT_LOCK_CYCLE.md).

## Thread transfer restrictions (TR1)

Separate representation summaries propagate an opt-out marker through ownership,
closure fields and async state. Five packages execute with fatal UBSan; fourteen
invalid packages reject before code generation. Existing object-lock checks pass
(six executions, ten refusals). This analysis change introduces no platform ABI or
runtime modification; platform suites were not replayed. Windows ARM64 execution
remains deferred. [Report and limits](THREAD_TRANSFER_CYCLE.md).

## Runtime metrics — API and emission integration

Ordinary namespace loading plus runtime cursor hooks; no new language rule or
privileged MemoryStats type. Eight native API observations pass, alongside C and
Corbo ABI witnesses with three concurrent allocators/read sampling. Fatal UBSan
is enabled on host tests. Target API execution: macOS ARM64/x86-64, Linux x86-64,
Windows x86-64 under Wine; Windows ARM64 compile-only. Independent fields are
samples of adjacent instants, not a transactional snapshot. [Report](MEMORY_METRICS_CYCLE.md).

## Self aliases and File text-path integration

Four native alias executions and two specific parser refusals pass. File API
sync/async probes execute on macOS ARM64/x86-64, Linux x86-64 and Windows x86-64
under Wine; Windows ARM64 compiles/links only. Host positioned-I/O regressions
pass under fatal UBSan. The compiler rebuild and package new/check pass.
Exact Windows ACLs are not validated in Wine; default permissions are used for
that target. No frozen Rust frontend or general rule audit was replayed.
See [the report](SELF_FILE_CYCLE.md).

## Recursive places and projected aggregate writes

N1/N3/N5: eleven accepted projected-write programs execute under fatal UBSan;
one dynamic bounds witness traps before access and five invalid programs reject.
The existing tuple-iteration suite passes six executions and seven refusals.
Recursive root, permission and shape checking replaces early AST-shape guesses.
Plain-value replacement uses existing content-access checks; ownership-bearing
replacement rules are not bypassed. Installed compiler smoke checks pass.
Host: macOS ARM64; target ABI/runtime unchanged. No platform matrix replay.
[Focused report](PROJECTED_WRITES_CYCLE.md).

## Selected-file diagnostics and dependency-aware watching

Compiler CLI context selection, not a normative rule change. Nine direct focus
checks and one watch sequence pass; seven existing file-watch cases remain
passing. A normal two-module build executes with output 42. Selected files retain
original source locations and do not inherit unrelated main/module errors;
required module and manifest failures remain relevant. The rebuilt compiler is
installed. Host: macOS ARM64; no target ABI/runtime changes or platform replay.
[Report](SELECTED_FILE_CHECK_CYCLE.md).

## Nominal instance-method dispatch

Struct and enum receivers share method lookup, parameter ownership and borrow
reservations. `scripts/validate_enum_methods.py` checks receiver mutation
permission, moving versus primitive-enum copying, retained enum identity,
borrowed matches and resource cleanup. It also covers generic structs/enums.
This is focused compiler integration coverage, not new normative rules or proof
of general safety. See [the cycle report](ENUM_METHODS_CYCLE.md) and its checklist
for execution/install status.

## Diagnostic classification and context retention

Syntax expectations, normative refusals and compiler limitations have distinct
human-readable categories. `scripts/validate_diagnostic_categories.py` compares
verdicts/raw output with the pre-change baseline and checks precise original
locations, type and move details, unsupported signature reasons and an accepted
program. Existing source/semantic diagnostic suites supply directly related
regressions. [Scope and limitations](DIAGNOSTIC_CATEGORIES_CYCLE.md).

## Enum qualification and projected method receivers

The enum separator does not alter ownership rules. Field method calls carry
ordinary root/borrow and lock-result dependencies into code generation.
`scripts/validate_enum_paths_field_receivers.py` records accepted native/UBSan
executions and permission/lifetime refusals, plus actionable async/constructor
diagnostics. Existing enum/copy/move and semantic-diagnostic regressions remain
applicable. See [scope and evidence](ENUM_PATHS_FIELD_RECEIVERS_CYCLE.md).

## Checked extraction and numeric conversion

Postfix `!` shares the existing successful-payload ownership/borrow representation
with `?`; numeric `as` shares the value-exact checks with `try_from`.
Twenty-one focused native/fatal-UBSan observations pass, plus semantic/category
regressions and raw-protocol comparisons. See [evidence and platform limits](CHECKED_EXTRACTION_CYCLE.md).

## Declared reference methods and general dereferencing

Explicit ref/mut_ref methods precede universal shorthand. A<T>'s helpers borrow
T; nominal * selects the method by access mode and uses ordinary local scope
and loan summaries. Six native/fatal-UBSan programs and eight focused refusals
pass, plus 13 mutex regression cases, diagnostic audits and raw-protocol checks.
[Evidence, observed existing limits and platform scope](REFERENCE_METHODS_CYCLE.md).

## Unresolved dereference receiver robustness

Missing or non-reference receivers no longer cause invalid source slicing or
unsigned borrow-prefix subtraction. Generic wrapper classification waits for
specialization. Eighteen focused cases and watch failure-to-success recovery
pass; the actual unchanged WAL reaches a normal diagnostic without leaving
watch. [Cause, installation and evidence](DEREFERENCE_CRASH_CYCLE.md).

## Field-specific retained dependencies

CheckedValue retains the lifetime root and a separate first-field projection.
Disjointness must cover every retained dependency; an unknown projection remains
conservative. Lifetime cleanup still targets the complete owner. The current
prototype again rejects overlapping active mutable borrows while permitting
proven disjoint fields and last-use release. Focused observations, directly
related regressions and platform scope are recorded in
[the field-dependency report](FIELD_DEPENDENCIES_CYCLE.md).

## Explicit slice arguments in compound await propagation

N1/N3 retain explicit slice borrowing. An unborrowed range supplied to a slice
parameter is a source-level mismatch, not an unsupported compiler construct.
The diagnostic points at that argument, preserves the expected signature and
suggests the explicit shared or mutable borrow. Compound assignments across
`.await?` retain their existing once-evaluated place and early-return behavior.
[Focused execution evidence and limitations](COMPOUND_AWAIT_DIAGNOSTICS_CYCLE.md).

## Omitted slice-reborrow bounds

N1/N4/N5 use the same source slice descriptor and retained borrow edges for
`&slice[..]`, `&mut slice[..]`, `[..end]` and `[start..]` as for explicit bounds.
The omitted start is zero and the omitted end is the runtime source length.
The obsolete syntactic refusal at site 361 is retired; runtime bounds and
permission/overlap checks remain. [Focused evidence](SLICE_REBORROW_CYCLE.md).

## Generic-dependent guard iteration and block slice results

Loop normalization distinguishes an unknown source type from a known next()-based
iterator. Generic-dependent source classification waits for specialization. A
borrowed array header forms its slice view before overloaded dereference is
materialized. Block-result moves preserve slice permission and retained roots,
using existing lifetime checks. Two focused guard executions and ten iteration
regressions pass. [Evidence and source fixes](WAL_FILE_CHECK_CYCLE.md).

## Target byte order and binary API

`target.endian` is evaluated with the existing compile-time selection mechanism
before imports. The STD's static LittleEndian/BigEndian/NativeEndian methods
reuse the existing caller-buffer binary implementation and its checked errors.
The explicit name constant was removed at the user's request.
[Focused execution evidence](BINARY_ORDERS_CYCLE.md).
