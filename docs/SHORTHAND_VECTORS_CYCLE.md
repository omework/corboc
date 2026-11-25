# Field shorthand and standalone regional vectors

## Scope and implementation

Compiler/core: normalize `Self { file }` into `Self { file: file }` before
qualification and specialization, preserving ordinary move and borrowing checks.
Resolve bare `Vector<T>` and `Vector::new()` to an ordinary generic STD object;
infer its element type from an explicit binding or receiving field. Existing
`Pool<Vector<T>>` and `A<Vector<T>>` syntax retain their tracked path.
Order nested array layouts before enclosing Option/Result C declarations.

API/STD: `VectorValue<T>` implements new, len, is_empty, push, pop and clear.
Its fixed descriptor uses ordinary datastack/frame placement, while element data
uses the runtime region policy. No caller-provided pool is required. Stable
runtime registration currently uses a small OS virtual-memory mapping, outside
the element-region budget; this is implementation overhead, not inline data.
The destructor releases regional storage and registration once after ownership
transfer. Runtime source and ABI were unchanged.

The actual SubDB dispatcher needed two API corrections as well: `.async?` to
`.await?`, and importing the asynchronous FileError alongside its File type.
Its existing bare `groups: Vector<GroupMetadata>` now checks without introducing
a pool parameter or changing business policies.

## Executed validation

[Focused results](SHORTHAND_VECTORS_RESULTS.json): five programs passed under
fatal UBSan on macOS ARM64, covering shorthand/import qualification and destruction,
standalone struct elements, movement out of a region scope, pooled compatibility,
and an executable full async RawTable constructor. Four related cases were
rejected: moved shorthand input, undefined shorthand input, unsupported owning
elements, and transfer=false element propagation.

An isolated Linux ARM64 container also compiled and executed the emitted regional
scope-transfer program under fatal UBSan (output `12`). This exercises the Unix
allocation path; it is not Linux compiler reconstruction or broad corpus parity.
Windows execution was unavailable; Windows and Windows ARM64 remain unvalidated
for this cycle. No independent audit or broad rule-breaking campaign was run.

The modified compiler rebuilt the final compiler generation successfully.
Installed binary SHA-256:
`dc6d13ce6ec76ec640dc5a2a5333510927fa2f2a95df0072d5e16bd3d37ae267`.
Installed at `/Users/jabarkarim/sources/corboc/build/check-file/install/bin/corboc`
together with the matching working-tree STD. The installed compiler checks the
actual `/Users/jabarkarim/sources/subdb/src/dispatcher.crb` successfully. The
updated README budget package builds and prints `1000`.

Generated installed HTML documentation (1,620 declarations, 92 packages), and
checked Markdown STD/runtime documentation freshness successfully.
The build used an explicit development STD override: corbo.lock still pins the
previous committed revision; no dirty input was silently recorded as a commit.
No commit or push was requested or performed.

## Remaining implementation scope

Standalone elements currently use the existing plain-data classification:
primitives and recursively accepted plain structs/enums without destructors,
reference dependencies or owned resources. This is an implementation limit, not
a language restriction. Such dependency-bearing elements still require the older
tracked pooled vector path. Standalone indexing, slicing and full native-vector
API parity are not claimed. Unsupported element diagnostics currently include a
secondary generic N1 after the primary compiler-limitation message.
Source remapping retains generated-source anchors in some diagnostics.
