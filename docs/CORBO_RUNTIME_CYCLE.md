# Corbo runtime compiler integration

Classification: compiler/runtime and build integration. No normative language
rule or source grammar changed. The Rust reference was not modified.

## Implementation

`corbo.lock` now selects `runtime_implementation="corbo"` and pins
`6c16675e4073dd9778c1ac7c1c73d51ebe1a7199` in the language repository.
The normal resource generator compiles that checkout's runtime source with
`--emit-runtime-c`; no development-source override is required for a build.
The C implementation remains an explicit reference/bootstrap selection.

The new mode retains ordinary checking but accepts scalar libraries without
`main` and emits no managed allocation or scope rewind. Managed aggregates,
references, pools and async bodies are refused. Runtime locals use native call
frames/registers in the current C backend. Raw access/callback/platform bindings
remain explicitly unchecked; this is not a new exemption for ordinary programs.
Generated runtime functions are namespaced independently of application IDs.

The package source/wide-array limit is now 4 MiB and its token capacity is
1536 Ki tokens plus sentinels. Individual source reading supports 512 KiB.
The unchanged AST arena remains bounded. Packed runtime resources use a bounded
64 KiB decoder history, avoiding oversized decimal byte initializers without
adding a compression library dependency.

A compatible self-hosted seed must understand this build mode and those current
capacities. An older seed cannot perform the runtime-resource regeneration step.
There is no committed compiler binary or implicit fallback to the C reference.

## Executed evidence

- Runtime mode: two accepted scalar/opaque libraries and six expected refusals
  (entry point, array, pool, async, borrowing and C outside unchecked).
- Resource packing: five independent expansion round trips plus execution of
  the real Corbo decoder across the 64 KiB history boundary under fatal UBSan.
- Normal integrated compiler: core extensions, generic/tuple/registry and C ABI
  suites completed. The language repository's STD iterator suite also passed.
- All six source-lock regression tests completed.
- Pinned-source runtime regeneration/freshness check passed without a development
  override. Source and resource generation are deterministic.

Pinned self-reconstruction completed successfully: all three generated compiler
C files matched byte for byte, with SHA-256
`cb0b0304fa0680c81462562cfaf3187eff4075d4058c2225b794f05ff56719f9`.
The normal `corboc build` command rebuilt the compiler and that binary built and
ran the external two-module smoke package, printing `42`.
`build/bootstrap/report.json` records `self_verified: true` and the pinned revision.

The first transitional build used a seed embedding an earlier runtime and
therefore emitted a different runtime prelude from the new compiler. That
comparison was reported as a failure, not hidden or treated as a safety defect.
The final reconstruction uses a seed already built with the same pinned runtime.

## Platform runtime parity

The language-repository differential harness inventoried all 114 C reference
function definitions and compared both implementations in 48 executions per
target: macOS ARM64 native, macOS x86-64/Rosetta, Linux x86-64/Docker and Windows
x86-64/Wine. All 192 executions matched. It covers memory/cleanup, tasks,
launch failures, descriptor/completion state and boundary failures. Real
TCP/UDP and production multi-wait kqueue/epoll/IOCP checks also passed on all four.

The C-compatible Corbo memory archive linked and ran the existing ABI client on
all four targets. This does not add a public standalone scheduler ABI.
The full source map, corrected callback/Windows-capacity defects, commands and
limits are in the language repository's
[cycle report](https://github.com/omework/din-lang/blob/main/docs/cycles/CORBO_RUNTIME_CYCLE.md).

These are generated-program platform checks. Native compiler reconstruction
remains host macOS ARM64 evidence. Wine is not native Windows hardware; Windows
ARM64 execution is explicitly deferred and Linux ARM64 was not newly executed.
No new independent audit, mutation campaign, ASan claim or general safety proof
is included. Low-level C ABI/platform bindings remain, alongside the retained C
comparison implementation. This work does not claim a C-free toolchain.

## Reproduce

```sh
python3 scripts/corbo_sources.py --from-repo ../crust
python3 scripts/runtime_sources.py --compiler /path/to/compatible/corboc
python3 scripts/build.py --seed /path/to/compatible/corboc --verify-self
python3 validation/check_runtime_emission.py --compiler build/install/bin/corboc --keep build/check-runtime
python3 validation/check_core_extensions.py --corboc build/install/bin/corboc --keep build/check-core
python3 validation/check_core_mechanisms.py --corboc build/install/bin/corboc --keep build/check-mechanisms
python3 validation/check_c_runtime_bridge.py --corboc build/install/bin/corboc --keep build/check-c
python3 -m unittest discover -s validation -p 'test_*.py'
```

Retain `build/bootstrap/report.json` and each suite's output/`--keep` artifacts.
The source runtime and its report are versioned in the language repository;
this repository records the compiler integration and tested source pin.
