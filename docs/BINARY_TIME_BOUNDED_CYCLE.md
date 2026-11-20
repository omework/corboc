# Bounded strings, binary encoding and time

Date: 2026-11-20. Scope: core integration for TX23 and directly exposed generic,
borrow and visibility mechanisms; STD APIs for binary conversion and time.
The Rust frontend remains frozen. No new primitive or normative rule was added.

## Implementation

`String<N>` selects the STD's ordinary `BoundedString<N>` template. A numeric
argument has its own AST kind (94), rather than acquiring an expression's i64
type. Specialization substitutes the fixed array bound, normalizes equivalent
integer literals and leaves ordinary `String` growing. Layout is a native usize
length followed by `[u8; N]` and native padding; it is not a disk-format ABI.
`new`, `try_from`, `set`, `len`, `capacity`, `as_bytes` and checked `as_str` are
implemented. Oversized replacement returns TooLong before mutation; unused payload
bytes are zeroed. No general implicit Copy classification is introduced.

Core fixes defer unresolved generic array lengths past configuration expansion,
carry explicit static type arguments into generic method inference, and remap
private template metadata to generated concrete declarations. Shared text inside
Result retains its source root. Explicit `&*allocation` can borrow an owned
nominal payload through its pool slot, retaining allocation lifetime and loans.
These reuse ordinary nominal values and dependency summaries rather than adding
a separate bounded-string ownership model.

`std::encoding::binary` provides explicit `_le`/`_be` reads and writes for
u16/u32/u64/i32/i64/f32/f64 and 64-bit-target usize aliases. u8 and bool are single
byte operations. Short buffers return errors before writes; trailing output is
untouched. Boolean input must be zero or one. Signed/floating bit transfer uses
small existing unchecked assembly helpers; integer byte order is pure Corbo.

`std::time` provides Duration, Instant, sleep and reusable deadline Timer.
Linux/macOS use CLOCK_MONOTONIC and nanosleep; Windows uses performance counters
and Sleep. Interrupted waits recheck the deadline. Async sleep/Timer delegate to
existing spawn_blocking workers: one worker per active wait, with the calling
task suspended. This is not a new shared timer reactor. See the language repository’s API document
for signatures and clock/error details.

## Executed evidence

On macOS ARM64, the focused suite passes nine accepted O1/fatal-UBSan programs
and ten expected refusals (nine status 8, one syntax status 7). Accepted coverage:
byte order, signed extrema, float round trips, bool validation, short buffers,
monotonic waits, async waits, UTF-8 byte limits, exact-bound values, unchanged
oversized replacement, borrowed views, moves, distinct/equivalent capacities,
zero capacity, aliases/qualified names, growing/inline coexistence and pool
payload borrowing. Refusals cover mismatched capacities/types, private fields,
invalid type arguments, move reuse and expired/conflicting byte/text/pool loans.
An unsupported-backend status (9) does not count as an expected rejection.

Two additional O1/fatal-UBSan programs pass: named constant array lengths and
ordinary generic structs instantiated with distinct primitive types. A preliminary
array `.len()` probe failed identically in the baseline and candidate (status 9);
the constant regression uses supported element indexing instead. This existing
API limitation was not expanded into this task.

The compiler rebuilds against the updated STD; stage2 and stage3 emit byte-identical
C. The development compiler and matching STD are retained under
`../corboc/build/binary-time/`. The installed/published compiler and corbo.lock
remain unchanged; the latter still pins `600b409a0edae3112fd0dd68e246cd0798a0a666`.
No dirty source tree is presented as a published revision.
The bundled development compiler also builds and executes the bounded-string
fixture with automatic STD discovery (no explicit --stdlib-dir).

Platform probes, three API programs (binary, blocking time, async time) and
three portable bounded-layout programs (UTF-8 replacement, capacity identity,
pool borrowing) per listed target:

| Target | Execution | Instrumentation |
| --- | --- | --- |
| macOS ARM64 | Host functional suite, including all six probes | O1 fatal UBSan |
| macOS x86-64 | Six probes, Rosetta | O1 fatal UBSan |
| Linux ARM64 | Six probes, Docker | O1 fatal UBSan |
| Linux x86-64 | Six probes, Docker | O1 fatal UBSan |
| Windows x86-64 | Six probes, Wine | O1; no UBSan |
| Windows ARM64 | Six object compilations only | Zig target compile; execution deferred |

Platform-specific API C was emitted using temporary host executables with target
metadata/assembly selection configured for each destination. These exercise the
actual STD backends; they are not native compiler rebuilds on those operating
systems. Portable bounded-layout C was emitted by the updated compiler and
cross-compiled unchanged. Final Windows probes were rerun after switching the
clock to QueryPerformanceCounter. Linux uses Docker rust:1.94-bookworm, Windows
uses Zig 0.14.1 and Wine, macOS uses host clang. Machine-readable outcomes are
in the language repository’s `docs/cycles/BINARY_TIME_BOUNDED_RESULTS.json`.

Generated API inventory: 96 STD files / 1,575 documented declarations and
members; 32 runtime files / 777 entries. No runtime implementation changed.

## Reproduction and limits

From corbo-lang with the sibling compiler checkout:

```sh
python3 validation/check_binary_time_strings.py --corboc ../corboc/build/binary-time/bin/corboc
python3 scripts/stdlib_docs.py --check
```

The runner retains C, executables and report.json under build/binary-time.
Host probes use this working STD explicitly. Stage2/stage3 reconstruction also
uses `--stdlib-dir ../corbo-lang/stdlib/src` rather than the old committed cache.

No broad historical corpus, mutation campaign, independent audit, exhaustive
floating-bit campaign, 32-bit target or Windows ARM64 execution was performed.
QPC's rare high-frequency overflow-avoidance fallback is not exercised by the
available Windows clock. Async worker exhaustion and platform clock failures
are represented by errors but were not fault-injected. Endianness is explicit
in serialization, independent of host order; native struct padding is not
serialized. Calendar time, periodic/cancellation APIs and a shared timer reactor
are outside the retained API. Successful probes are scoped evidence, not a
proof of complete language safety.

## Publication

The language/STD lot is committed as `8a35f8faaf6fd37f68768b8587a211c03c2bbcdf`. corbo.lock now pins
that revision. The earlier unchanged-pin statements record the implementation
validation phase, before this requested publication step. The installed binary
remains unchanged; the matching development compiler is in build/binary-time.

Publication checks completed: `python3 scripts/corbo_sources.py --check`
accepts the clean cache at the pinned revision;
`python3 scripts/runtime_sources.py --check --compiler build/binary-time/bin/corboc`
confirms that the embedded bridge matches the pinned readable runtime.
