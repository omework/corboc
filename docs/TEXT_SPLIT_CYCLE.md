# Borrowed text splitting integration

## Classification

STD/API addition with general compiler support for immutable UTF-8 descriptors.
No grammar or normative memory-rule change. The splitting algorithm remains in
Corbo STD source, not in the compiler or native runtime.

## Implemented

- Preserve `&str` descriptor roots through names, text fields, constructors,
  shared slices and `Option<&str>` results.
- Resolve a returned view to its external text field, independently of the
  iterator's mutable cursor, and forward symbolic field dependencies through
  a borrowed source.
- Lower bounds-checked, UTF-8-boundary-checked views using evaluated descriptor
  temporaries and byte casts for the runtime's opaque data address.
- Resolve the source-defined native `split` convenience method in package
  linking, checking, generic result inference and lowering. Nominal methods
  retain priority during generic result inference.
- Apply the existing exclusive-loan conflict analysis before `String.push_str`
  mutates bytes. An invalid program accepted during the focused checks is now
  refused under N5.

## Executed evidence

The language checkout's `validation/check_text_split.py` executes twelve
successful programs at O1 with fatal UBSan and checks four expected refusals.
They include UTF-8 and byte contents, empty text/separators, overlap, exhaustion,
owned/named views, independent iterator and separator lifetimes, and the
existing `Iter` wrapper. Its README text package also executes.

Seven existing focused cases pass with the final artifact:

```sh
python3 validation/check_coverage_gaps.py \
  --corboc build/text-split/corboc --stdlib ../crust/stdlib/src \
  --only borrowed_text_len,byte_content_eq,buffered_custom_sink,buffered_count,borrow_chain,reject_dangling,reject_loan_write \
  --keep build/text-split-regressions
```

The updated compiler emits its own package, its emitted C builds successfully,
and the resulting `build/text-split/corboc` emits byte-identical C on the next
pass (`build/text-split/stage2.c` and `stage3.c`). The initial old-seed emission
naturally differs: the new text lowering now materializes receiver temporaries
for descriptor operations. No runtime resource source or byte payload changed.

## Reproduction and limits

The [language-side report](https://github.com/omework/din-lang/blob/d15cd7b6d6a567c4b7e98211b7fb0c7e2e5a7a90/docs/cycles/TEXT_SPLIT_CYCLE.md) contains
API semantics and focused validation commands. Those commands explicitly select
the working language checkout's STD. `corbo.lock` now pins
`d15cd7b6d6a567c4b7e98211b7fb0c7e2e5a7a90`, the published language/STD
commit containing the splitter. The dependency checkout was advanced cleanly
using Git, and runtime resource regeneration produced identical embedded bytes.

The pinned install build completed with:

```sh
python3 scripts/build.py --seed build/text-split/corboc
build/install/bin/corboc build ../crust/examples/features/text -o build/text-split/pinned-text
build/text-split/pinned-text
```

The normal build automatically resolved the installed STD and printed
`13, 2, 5, 6, 0`. The pinned compiler C SHA-256 is
`1310fa6d675a0ef2157fb7d48f96d7399db08c11edc7932bc76b532552e7e779`.
This install build did not rerun the full `--verify-self` campaign; the earlier
successive-emission comparison remains recorded separately above.

Execution evidence here is macOS ARM64 only. No platform-specific implementation
was added; Linux/Windows execution, arbitrary generic compositions and an
independent adversarial audit were not part of this change. Windows ARM64
execution remains deferred. The Rust frontend remains frozen. Passing these
checks is not a general safety proof.
