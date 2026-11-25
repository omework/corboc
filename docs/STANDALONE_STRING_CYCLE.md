# Standalone regional String

## Scope and implementation

Compiler/API integration; no new grammar production or normative borrowing rule.
`String::new()` and bare String annotations select an ordinary move-only STD
StringValue object. Its fixed descriptor follows normal datastack/frame placement;
its bytes use the existing regional allocation policy. Pooled String payloads and
bounded inline String<N> remain unchanged.

The STD implementation reuses stable region registration and cleanup from the
existing standalone-vector storage bridge. Its zero-sized array anchor establishes
an ordinary borrow of the descriptor; the unchecked bridge substitutes the actual
regional byte pointer and length. It does not expose mutable bytes or give views
an independent lifetime. `as_str()` validates UTF-8 while deriving its view.
Runtime registration mapping overhead remains separate from payload-byte budgets.
The universal ref() operation retains its existing descriptor-borrow semantics;
as_str() is the explicit text-view API.

Borrowed ranges are normalized through as_str() and existing UTF-8 bounds checks.
Two general compiler gaps were fixed: type guessing for instance-method results,
and retaining text provenance through parentheses. The latter was exposed by a
refusal check: grouped slicing initially erased its target, incorrectly allowing
the owner to be dropped before the view's last use. It now preserves that edge.

Implementation: src/direct_strings/direct_strings.crb,
src/process_arguments/process_arguments.crb, src/lowering/lowering.crb,
src/package_link/package_link.crb and STD collections/string_value.crb.
No runtime source or ABI change was needed. No hidden pool or general-purpose
heap fallback was introduced.

## Executed validation

[Focused results](STANDALONE_STRING_RESULTS.json), reproduced by
scripts/validate_standalone_string.py. On macOS ARM64:

- Five executable programs passed fatal UBSan: UTF-8 append/views/slicing and
  universal ref(), transfer through functions/scopes/aggregate owners with
  occupied-byte cleanup accounting, borrowed split, pooled/inline compatibility,
  and String ownership/extraction/cleanup in a standalone Vector.
- Four expected rule refusals passed: destruction with a live text view,
  append with a live byte view, use after move, and an escaping borrowed view.
- Two runtime-constraint checks terminated as expected: splitting a UTF-8
  character at an invalid byte boundary and exceeding the local region budget.

The modified compiler successfully reconstructed its source with the preceding
self-hosted generation. No three-generation fixed point or broad corpus campaign
was run. Linux and Windows execution was not performed; Windows ARM64 remains
explicitly deferred. Platform registration helpers are reused unchanged.

Installed binary SHA-256: `cc408e45a27c498069f4a07ddbbe19567ff3c658fda7c15ad00787eabfc342b5`.
Installed at `/Users/jabarkarim/sources/corboc/build/check-file/install/bin/corboc`
with the matching working STD. corbo.lock remains at its committed revision;
the new STD is an explicit development override until a later commit/pin update.
No commit or push was requested or performed.

## API scope

Standalone methods: new, byte_len, is_empty, push_str, as_bytes, as_str and split;
shared UTF-8 range notation is preserved. Additional String manipulation APIs are
not added by this constructor integration. Current as_str() performs UTF-8
validation rather than promising constant-time view construction.

## Installed smoke checks

The installed PATH compiler builds the updated README text package; it prints
`13 / 2 / 5 / 6 / 0`. The actual SubDB dispatcher file also checks successfully.
Generated installed HTML API docs (1,632 declarations across 92 packages) and
checked STD/runtime Markdown documentation freshness. Working-tree diff checks
passed in both repositories.

## Committed dependency alignment

Corbo was committed and pushed as `5e6102327da38094caf2e48c27ab3aa866c6d986`.
corbo.lock now pins that revision. The clean source cache and runtime bridge
freshness checks pass. The installed STD matches the committed files byte for
byte; installation metadata is aligned with this pin. The development-override
notes above describe the implementation/validation stage before this commit.
