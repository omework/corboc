# Async-default API reorganization

Scope: API/STD organization, not a grammar or language-rule change. Compiler
integration is limited to its own blocking File imports and existing encoded
private-layout namespace metadata. No new ownership/checking mechanism or
runtime backend was added. Rust remains frozen. The namespace decision was
explicitly accepted by the user.

## Implemented

- Default async File, buffered wrappers, TCP/UDP and sleep/Timer.
- Explicit blocking variants under io::sync, net::sync and time::sync.
- Shared File options/stats at io root; shared Duration/Instant/Error at time root.
- Instant::remaining query allows the child blocking Timer to use public methods.
- Existing blocking TLS moved intact under net::sync::tls, including its codecs
  and key helpers; no async TLS implementation claimed. HTTP parser contract unchanged.
- Active STD imports, example packages and validation generators migrated.
  Historical cycle reports, archived corpora and the frozen Rust frontend retain
  their original namespaces; their historical results are not replay claims.
- Removed public asyn aliases; preserved internal sys network backend names.
- English/French README convention, coverage table and complete async File example.
  Removed redundant primitive/error drops in the new examples, retaining early
  File closure before deletion. Generated API reference updated.

## Executed evidence

macOS ARM64, active corboc:

- README file, buffered, network, time, async_time, bounded_text, binary and new async_file packages:
  successful O1/fatal-UBSan executions, source blocks synchronized.
- Existing async buffered File: O0/O2 fatal UBSan plus eight borrow refusals.
- Existing async buffered TCP: O0/O2 fatal UBSan against an independent Python peer.
- Existing async TCP split and UDP: O0/O2 fatal UBSan, plus rejection of root
  connection destruction while its split tasks retain it.
- Existing TLS client/server against OpenSSL: application exchange in native and
  fatal-UBSan configurations; out-of-order Finished, certificate/key mismatch
  refusals retained; Session traffic state remains private.
- Normal `corboc build` discovers the matching bundled STD and runs async_file (output 2).
- corboc itself compiled using the migrated blocking imports; no broad historical
  suite or independent audit was run for this API-only change.

Platform probes use seven programs: blocking/async File, blocking/async timer,
blocking UDP and async TCP/UDP. Each executes on macOS x86-64 (Rosetta), Linux
x86-64 (Docker), Windows x86-64 (Wine); each compiles to a Windows ARM64 object.
Linux ARM64 executes the two timer probes; File/socket Linux ARM64 support is
not added. macOS/Linux runs use O1 fatal UBSan; Windows uses O1 without UBSan.
Windows ARM64 execution remains deferred by the user's instruction.

Temporary host emitters select the destination's existing STD assembly backend;
they are not native compiler builds on each destination. Toolchains: host clang,
Docker rust:1.94-bookworm, Zig 0.14.1, Wine. Platform outcomes are retained in
the language repository’s docs/cycles/ASYNC_DEFAULT_API_RESULTS.json. These are namespace/integration
regressions, not a fresh cryptographic audit or general safety proof. Existing
OS primitives and runtime machine code were not changed.

## Reproduction

```sh
python3 validation/check_documentation.py --corboc ../corboc/build/async-default/bin/corboc --only async_file
python3 validation/check_rust_buffered_io.py --corboc ../corboc/build/async-default/bin/corboc --async
python3 validation/check_rust_buffered_io.py --corboc ../corboc/build/async-default/bin/corboc --async --tcp
python3 validation/check_network_waits.py --corboc ../corboc/build/async-default/bin/corboc --keep build/async-default-network
python3 validation/check_tls13_handshake.py --corboc ../corboc/build/async-default/bin/corboc
python3 scripts/stdlib_docs.py --check
```

Publication updates the compiler's STD pin to this committed API layout; the
published lock must not reference an uncommitted working tree. The development
compiler is retained under corboc/build/async-default, with matching bundled STD.

## Publication

corbo.lock pins `4ccedd17788c681756c11f189bad7384f318738a`, the committed async-default STD/API layout.

The clean pinned cache passes scripts/corbo_sources.py --check.
Embedded runtime freshness passes scripts/runtime_sources.py --check with
build/async-default/bin/corboc; readable runtime sources are unchanged.
