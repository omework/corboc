# Compiler repository extraction

Date: 2026-11-18. Scope: source/build organization and pinned shared inputs.
Language rules, parser/checker algorithms and runtime algorithms are unchanged.
The Rust reference remains frozen. No independent audit or mutation campaign
was performed or incorporated in this cycle.

## Result

The self-hosted compiler now lives at the root of `omework/corboc`, locally
`/Users/jabarkarim/sources/corboc`. The former language-repository directory
`compiler/corboc/` was removed after comparing its files against the new checkout.

81 compiler/package files were checked before removal: 79 retained identical
contents; one source comment points to the lock and the generated runtime
resource's provenance comment points to the lock. The latter embeds the same
runtime code. The internal package remains `bootstrap` and existing imports
retain their meaning. The compiler-focused suites and fixtures moved as well.

Readable runtime code, the STD, grammar and normative rules remain in the
language repository. `corbo.lock` pins all shared inputs to
`cd7e97b3a0bf9f808fb27559705b11509d4e1a24`. The isolated `.deps/corbo` checkout
has the canonical remote and detached exact revision; build scripts check
revision and input modifications before using it. Local cloning takes committed
Git objects, never a neighboring checkout's uncommitted files.

Runtime generation and build/install scripts now use this lock. The installation
retains `bin/` and `share/corbo/stdlib/src/`, so the existing executable-relative
STD discovery requires no compiler algorithm changes. An installed copy of the
lock records the STD/runtime revision. The public C header is also installed.

The language repository discovers a sibling `corboc/` or `CORBOC_SOURCE_ROOT`.
Historical validation entry points forward to this repository; corpus tools
include moved source and fixture files with stable `corboc/...` labels. No second
maintained compiler/runtime implementation was left in the language checkout.

## Completed evidence

| Check | Executed result |
| --- | --- |
| Source cache | Exact revision, clean input check and runtime-resource freshness passed. |
| Compiler generations | Seed generated stage1 C; rebuilt compiler generated stage2 C; a second rebuilt compiler generated stage3 C. All three files are byte-identical. |
| Normal self-build | `corboc-stage2 build /Users/jabarkarim/sources/corboc -o .../corboc-cli` succeeded using automatic installed-STD discovery. |
| External package | The normal-build compiler built a separate two-module package with `use smoke::math::answer`; its executable printed `42`, exited successfully and had empty stderr. |
| Core extensions | 21 accepted programs, 20 expected refusals, custom-header/immutable C operand and target-selection/import checks passed. |
| Generic/tuple mechanisms | Nine programs at O0/O2, seven expected refusals and the deterministic readiness-registry witness passed. The C fixture now includes the locked runtime via the include path. |
| C bridge | Nine Corbo fixtures, one C library client and one separately compiled C helper at O0/O2: 22 executions, plus three Corbo refusals and three native C mutability refusals. Passed against the locked runtime. |
| Source-lock checks | Six isolated local-Git tests passed: clean identity; cloning committed contents from a dirty working checkout; modified STD rejection; untracked runtime code rejection; wrong-cache revision rejection without reset; abbreviated revision rejection. |
| Historical entry points | The language-repository mechanism forwarder completed; reference-corpus tools located all 80 compiler source files; inventory retained 119 external compiler/fixture source candidates. |
| Target-emitter tooling | The moved Linux target-emitter helper built successfully from the new compiler root and pinned STD; a target-selection program selected the Linux branch and printed `42`. This is a host-running test emitter, not a native Linux compiler execution. |
| Maintenance | Python syntax, runtime resource freshness, generated STD documentation and whitespace checks passed. |

C SHA-256 for the three compiler generations:

```text
24732e8c0ef2f93ce458898f421ccecd3f3f8f77a3a118701c970847205c19fb
```

`build/bootstrap/report.json` records the seed, source revision, generated-C hash,
normal-build binary and module result. Additional retained logs for this run are
under `/tmp/corboc-extraction/`; compiler artifacts are under `build/`.

## Validation correction

The first clean-source unit test compared canonical `/private/var/...` output to
macOS's `/var/...` temporary-path spelling. It failed despite referring to the
same directory. The fixture now canonicalizes its temporary root; all six tests
were rerun to completion. No source-identity behavior was weakened.

## Limits and reproduction

All extraction/self-hosting execution above ran on macOS ARM64 with Clang.
Generated regression programs used fatal UBSan where their suites specify it.
The extraction changes paths/build tooling, not target code; no new cross-platform
runtime claim is made. Earlier language-repository reports retain the macOS x86,
Linux x86 and Wine evidence. Native Windows and Windows ARM64 gaps remain open;
Windows ARM64 execution was explicitly deferred by the user. No ASan campaign
was run here.

The seed was the existing self-hosted compiler installed in the language checkout.
An initial seed release/distribution is not provided by this migration. Private
GitHub access is needed for remote dependency preparation; the local-Git option
was the preparation path executed here. Extraction validation preceded publication; the compiler and language
repositories retain independent commit histories.

```sh
python3 scripts/corbo_sources.py --from-repo ../crust
python3 scripts/build.py --seed /path/to/compatible/corboc --verify-self
python3 -m unittest discover -s validation -p 'test_*.py'
python3 validation/check_core_extensions.py --corboc build/install/bin/corboc --keep build/check-core
python3 validation/check_core_mechanisms.py --corboc build/install/bin/corboc --keep build/check-mechanisms
python3 validation/check_c_runtime_bridge.py --corboc build/install/bin/corboc --keep build/check-c
```

The user’s commit identity is `Jabar` with the existing email. Both local
repositories and conditional Git identity for Corbo GitHub clones are configured.
A fresh temporary repository with a Corbo remote inherited `Jabar` successfully.
