# General callable integration

Scope: compiler/core implementation of the existing closure syntax and rules.
No normative rule, trait, runtime ABI or STD API was added.

## Implementation

`src/callables/callables.crb` materializes a concrete record for each closure.
Its fields hold the captures, its ordinary constructor initializes them at the
closure's creation point, and its invocation method borrows the record. Mutation
of captures selects a mutable receiver. Primitive/shared-reference captures copy
without `move`; explicit `move` transfers the captured bindings.

The callable signature remains `fn(...) -> R`, `&fn(...) -> R` or
`&mut fn(...) -> R`. Functions accepting these parameters specialize to each
concrete capture record after checking the signature. The passing mode is
preserved: the resulting ordinary record argument moves, borrows, or mutably
borrows the instance. Further forwarding specializes in the same way.

Invocation thunks support immediate calls and expression receivers. Redundant
parentheses are normalized, and evaluating the receiver before the remaining
arguments preserves ordinary call evaluation order. Constructors and thunks use
existing inferred contracts, provenance, ownership summaries, cleanup and the
post-AST placement plan. There is no erased capture pointer or new allocator.

Expansion reuses one bounded workspace. Each iteration clears graph links before
rebuilding them; failing to clear the reused graph caused a development hang
and was corrected. Generated declarations are placed beside their defining
item, retaining its module visibility. Expansion also follows iterator lowering,
so independent callbacks and STD iterator adapters compose.

Two existing reborrow gaps exposed by the generated records were corrected:
local record reborrows use the record-argument loan checks, and scalar reborrows
carry their target and parent through constructor/call contracts. A shared
reborrow retains the borrowed target rather than inventing ownership of it.

## Completed validation

Platform: native macOS ARM64. The modified compiler was built using the existing
self-hosted seed. Each accepted test's generated C was compiled with
`-O1 -fsanitize=undefined -fno-sanitize-recover=all`; status, stdout and stderr
were checked. Evidence is retained in `build/general-callables/report.json`.

| Program | Executed behavior |
| --- | --- |
| `modes` | Explicit callable binding, named/immediate calls, shared/owned arguments, forwarding, two concrete callback types; `42, 10, 20, 2, 42, 42`. |
| `mutable` | Repeated calls, `&mut fn` and `mut f: fn`; capture state progresses through `2, 7, 5, 6`. |
| `borrow` | A moved mutable reference remains attached to its target; `11, 12, 12`, including access after capture-object cleanup. |
| `cleanup` | Resource capture moved with the callable, then consumed by a function; `9, 90, 9` distinguishes one destructor call from returned values. |
| `shared_capture` | Shared-reference capture preserves the outer reference and target; `7, 7`. |
| `pipeline_interop` | General callback and STD filter/map/reduce/collect in the same package; `42, 1, 120, 7`. |

Seven invalid programs were rejected with compiler status 8:

| Program | Diagnostic rule |
| --- | --- |
| Write to a captured target before the callback's last use | N5 |
| Use a primitive binding after explicit move capture | N6 |
| Incompatible callable signature | N1 |
| Use a callable after passing it by value | N6 |
| Mutate captures through `&fn` | N5 |
| Capture a resource without `move` | N3 |
| Let a captured reference escape its target's scope | N4 |

The language checkout also executed the updated README closure package
(`42, 10, 20, 2, 1, 2`) and the former rejected callable package (`42, 2`),
both under the same sanitizer configuration. README/source synchronization passed.
The former callable limitation is removed from the active rejection list.

## Reproduction and limits

```sh
python3 validation/check_callables.py \
  --corboc build/install/bin/corboc --keep build/general-callables
```

In the language checkout:

```sh
python3 validation/check_documentation.py \
  --corboc ../corboc/build/install/bin/corboc \
  --keep build/general-callables-docs --only closures
```

This is focused implementation/regression evidence: eight distinct executable
programs and seven refusals. No full corpus, new self-reconstruction cycle,
ASan, mutation campaign or independent safety audit was run. The Rust reference
was not changed. Other platforms were not rerun; Windows ARM64 execution remains
deferred. The bounded expansion workspace retains the compiler's existing
source/node limits. No claim of universal callable-composition coverage or a
uniform erased representation for heterogeneous closure storage is made.
