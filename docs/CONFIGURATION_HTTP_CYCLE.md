# Configuration and HTTP integration cycle

Date: 2026-11-19. Classification: compiler/core specialization plus STD/API parsing.
The frozen Rust frontend was not modified.

## Delivered

- Parse configurable module constants and lexical override blocks. Resolve ordinary,
  qualified and aliased constant identities, reject unmarked/inaccessible targets,
  duplicate identities, runtime values and incompatible numeric types/ranges.
- Carry effective environments through helpers and nominal layouts. Escaped values
  keep their creating specialization; nested blocks restore the enclosing defaults.
- Reduce named constant array bounds before ordinary type checking and lowering.
- Implement synchronous `std::net::http::request` and `response` over the structural
  reader contract. Returned messages own bounded heads and borrow their reader.
- Parse strict CRLF heads, repeated fields, request/status lines, Content-Length and
  chunked framing with bounded trailers. Body construction and destruction never
  drain input; reads stop at the declared boundary.
- Reuse per-field caller summaries through Result/Option. Preserve record provenance,
  reference permissions, binding mutability on returning paths, symbolic borrowed
  record roots, enum field borrows and inferred borrowed method returns.
- Integrate the existing TX8 UTF-8 conversion operation needed for checked ASCII
  views, and defer generic recipe calls until their surrounding recipe is concrete.

## Executed evidence

`validation/check_configuration_http.py` completed **37 checks** on macOS ARM64:
**25 executables** built with `-O1 -fsanitize=undefined -fno-sanitize-recover=all`
and **12 expected compile/package-resolution refusals**. The recorded outputs and
exit statuses all matched; no sanitizer diagnostics occurred.

The set covers defaults, nested overrides/restoration, transitive helper calls,
escaped objects/layouts, aliases, duplicate aliases, visibility, type/range errors,
partial reads, requests and responses, fixed and chunked bodies/trailers, no body,
zero-length body, clean EOF, truncation, conflicting/overflowing framing, exact and
exceeded request-line bounds, header-line/section/count bounds, repeated-header
borrowed views, and a reader destroyed before its message's last use. It includes
four existing aggregate/slice/enum regressions and two UTF-8 probes (valid multibyte
input and rejected overlong encoding).

The optimized compiler emitted its own package C byte-for-byte identically to the
seed's output for the modified sources:

`d8a949ed6f69b56af036cdbfbdc4e107daf794cf42110d147f13bb03e83ead7f`

The generated STD/runtime reference check completed: 92 STD files / 1462 documented
declarations and members; 32 runtime files / 775 declarations and members.
See [machine-readable results](CONFIGURATION_HTTP_RESULTS.json).

## Reproduction

From the compiler checkout, with a compiler built from these modified sources:

```sh
python3 validation/check_configuration_http.py \
  --corboc build/install/bin/corboc \
  --stdlib-dir .deps/corbo/stdlib/src \
  --keep build/configuration-http-published-validation
```

## Published source pin and installed build

The language/STD changes are published in corbo-lang. `corbo.lock` now pins
`aa3bec8add1191f68faf4c7808a2239182d40170`; the dependency cache was advanced to
that clean commit and verified. Runtime resources were regenerated; their bytes
are unchanged, and the freshness check passes against the final pin.

`python3 scripts/build.py --seed build/configuration-http/bin/corboc --prefix build/install`
completed against that pin. The installed compiler's subsequent self-emission is
byte-identical to the seed emission (SHA-256 above). All 37 focused checks were
rerun successfully using `build/install/bin/corboc` and `.deps/corbo/stdlib/src`.

The normal installed command also built and ran a package importing HTTP, without
`--stdlib-dir`. It printed `4, 6, 5, 104, 0, 67` on separate lines: method and target
lengths, body count, first body byte, exhausted-body count and final reader cursor.
Thus new users of this build use the committed STD through automatic discovery;
the earlier working-tree-only selection is no longer required.

Both publication commits use Jabar as author and committer.

## Limits

This is focused integration evidence, not a general safety proof or independent
audit. No broad corpus/mutation campaign or Linux/Windows execution was performed;
Windows ARM64 execution remains deferred. No sockets were required by these parser
checks: the injected reader deliberately limits each read to two bytes.

Configuration currently evaluates existing literal/constant-reference expressions,
not arbitrary compile-time calls or new arithmetic constant expressions. Workspace
bounds are 256 configurable constants, 256 environments, 8192 declarations and the
existing bounded expansion buffers/depth. Exhaustion is a compiler limitation.

Result encoding now supports one Option envelope per arm; arbitrary deeper nested
envelopes and nested pattern syntax are not established by this cycle. TX8 conversion
currently needs an explicit Result type context and a single unit error variant.

HTTP is a synchronous low-level parser, not an HTTP server or complete exchange
engine. Async HTTP, serialization, close-delimited bodies and protocol handoff are
not implemented here. Response body indication follows headers; callers handle HEAD
and request/status-dependent exceptions. Transfer-Encoding supports only chunked;
duplicate Content-Length and conflicting framing are rejected. Chunk extensions are
bounded visible ASCII, not fully interpreted. When a remaining section budget limits
a line, exhaustion can report LineTooLong rather than HeadersTooLarge. Transport-error
wrapping is implemented; this cycle did not inject an underlying read error.
