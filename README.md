# corboc

The self-hosted compiler for [Corbo](https://github.com/omework/corbo-lang), an
experimental systems language built around explicit intent, predictable memory
management and static verification.

This repository owns the lexer, parser, static representations, verifier,
placement analysis, code generation and package build command. The compiler
currently emits C11 and invokes a host C compiler. The internal source package
is still named `bootstrap`; the executable and repository are named `corboc`.

## Shared sources

The language repository owns the grammar, rules, STD, runtime, examples and
editor support. [corbo.lock](corbo.lock) pins one exact Git commit for all those
inputs. There is no floating branch dependency or second maintained runtime.

```sh
python3 scripts/corbo_sources.py
python3 scripts/corbo_sources.py --check
```

The first command clones the source into the ignored `.deps/corbo/` cache and
checks out the locked revision. The check rejects a different revision or local
changes to STD, runtime code or normative inputs. SSH access to the language
repository is required. A local Git checkout can supply the same commit offline:

```sh
python3 scripts/corbo_sources.py --from-repo ../corbo-lang
```

That option clones Git objects at the locked commit, not the source checkout's
uncommitted working files. It retains the canonical remote from the lock.

## Build and self-rebuild

Prerequisites: Python 3.11+, Git, a C11/pthread toolchain and an existing
self-hosted Corbo seed supporting the current grammar, `--emit-runtime-c` and
4 MiB source/wide-array capacities. The frozen Rust frontend
cannot compile the current compiler source. A seed binary is not committed here;
provide its path explicitly or set `CORBOC_SEED`.

```sh
python3 scripts/build.py --seed /path/to/corboc --verify-self
export PATH="$PWD/build/install/bin:$PATH"
```

The script checks the runtime resource against the locked source, installs the
pinned STD beside the compiler, builds two compiler generations, compares their
emitted C byte for byte, performs a normal package self-build and runs an external
two-module import program. Artifacts and a machine-readable report are retained
in `build/bootstrap/`. Omit `--verify-self` for a routine development build.
Use `--prefix`, `--cc` and `--cflags` to choose the installation and staged C
compilation. The normal `corboc build` command uses `cc` from `PATH`.

The installed layout is:

```text
build/install/
  bin/corboc
  include/corbo_runtime.h
  share/corbo/corbo.lock
  share/corbo/stdlib/src/
```

## Check a package without building

```sh
corboc check
corboc check path/to/package
corboc check --watch
corboc check path/to/package --watch
```

`check` resolves the package manifest, imports, dependencies and installed STD,
then parses and runs the static verifier. It does not emit C, invoke a C compiler
or create a binary/build directory. Dependency resolution may populate its usual
Git cache. It returns zero on success and the existing nonzero compiler status on
failure. Existing rule/offset diagnostics are retained; this is not yet an IDE
or file/line diagnostic service. `--verify FILE` remains the single-file mode.

`--watch` runs an initial check and stays alive after errors. It polls contents
at 250 ms intervals and rechecks after one stable interval, debouncing rapid saves.
It detects edits (including equal-size edits), additions, deletions and atomic
save-by-rename for `.crb`, `package.toml` and `corbo.lock` files recursively under
the selected project. Hidden entries, root `build`/`target` directories and
`node_modules` are ignored; symlinks are not followed. The scanner uses
bounded 4096-byte paths and a maximum depth of 64. Unreadable trees report a scan
error; recoverable errors during watching are retried as files become readable.
Changes in external path dependencies or installed STD are not watched: rerun
`check` for those. Each run rechecks the whole package; analysis is not incremental.
Status messages go to stderr. Stop watching with Ctrl-C.

## Create a package

```sh
corboc new my_package
cd my_package
corboc build
./build/my_package
```

`new` creates `package.toml`, an empty `src/main.crb`, `.gitignore` and a short
README. It refuses any existing destination, including an empty directory, and
does not initialize Git. The name is a single package identifier: ASCII letters,
digits and underscores, starting with a letter or underscore (up to 255 bytes).
`std` and `runtime` are reserved; paths and hyphenated names are not accepted.
Filesystem/platform filename restrictions also apply. If writing the scaffold
fails after creating the directory, the partial directory is retained and an
error is reported.

`corboc build` automatically finds the STD relative to its installed executable.
From a package root, it creates `build/<package-name>`:

```sh
corboc build
./build/bootstrap
```

The optional manifest setting overrides the binary name:

```toml
[bin]
name = "my-program"
```

Without `[bin]` or its `name`, `[package].name` supplies the name. Binary names
are portable filename components: ASCII letters, digits, `_`, `-` and `.`, with
at least one letter, digit or `_`. A default output always lives under the
selected package, even when building it from elsewhere. `-o` takes precedence
and its relative path is resolved from the caller's working directory:

```sh
corboc build /path/to/package
corboc build -o program
corboc build /path/to/package -o program
corboc build . -o build/install/bin/corboc-next
```

The filename policy adds `.exe` for Windows targets. The native package build
driver currently supports macOS ARM64 only; the other native drivers remain
unimplemented. Explicit output parent directories must already exist.
The compiler self-package remains named `bootstrap` internally, so its default
binary is `build/bootstrap`; use `-o` to choose a `corboc` installation path.

The C header is installed for external helpers. The standalone C memory library
build remains owned by the locked language repository's `scripts/build_c_runtime.py`.

## Runtime resources

Readable native runtime implementations remain in the language repository.
The compiler tracks one generated resource file so installed compilers do not
need the source cache when building user packages. `runtime_implementation="corbo"`
in `corbo.lock` selects compiled Corbo algorithms. The C reference remains available
with `--implementation c` for differential/bootstrap work. That explicit option
changes the generated resource and requires regeneration before a normal locked
build. Default builds never silently substitute the C implementation.

`corboc --emit-runtime-c FILE` is the allocation-free runtime build mode: it checks
scalar code without `main` and emits C without injecting this runtime into itself.
It rejects managed arrays, pools, references and async bodies. Machine/ABI operations
still require `@unchecked`; this mode changes no ordinary program ownership rule.
Runtime resource bytes are packed with a bounded 64 KiB history and decoded by Corbo.
A seed predating this mode cannot regenerate Corbo runtime resources; use a compatible
seed to build this revision.

```sh
python3 scripts/runtime_sources.py --compiler /path/to/compatible/corboc
python3 scripts/runtime_sources.py --check --compiler build/install/bin/corboc
```

To update shared inputs: deliberately update the full commit in `corbo.lock`,
remove or replace the ignored cache, prepare the new pinned checkout, regenerate
the resource, rebuild and validate. A cache with the wrong revision is rejected;
it is never silently switched or reset. `--source /path/to/checkout` can verify
and use a local checkout only when it matches the lock and has unchanged inputs.

## Validation

```sh
python3 validation/check_core_extensions.py --corboc build/install/bin/corboc --keep build/check-core
python3 validation/check_core_mechanisms.py --corboc build/install/bin/corboc --keep build/check-mechanisms
python3 validation/check_c_runtime_bridge.py --corboc build/install/bin/corboc --keep build/check-c
python3 -m unittest discover -s validation -p 'test_*.py'
```

Compiler regression scripts and their fixtures live here. Historical language
repository entry points forward to these implementations; STD integration and
Rust-reference corpus tools remain in the language repository. Set
`CORBOC_SOURCE_ROOT` there if this checkout is not the default sibling `corboc/`.

[Checklist](docs/IMPLEMENTATION_CHECKLIST.md) ·
[Verification matrix](docs/VERIFICATION_MATRIX.md) ·
[Migration report](docs/REPOSITORY_SPLIT.md).

Native compiler self-hosting for this extraction is validated on macOS ARM64.
Generated-program platform evidence and the Wine/native Windows distinction
remain documented in the pinned language repository. This migration does not
establish native compiler execution on every target. Windows ARM64 remains deferred.

Licensed under [MIT](LICENSE-MIT) or [Apache-2.0](LICENSE-APACHE), at your option.

[Corbo runtime integration evidence](docs/CORBO_RUNTIME_CYCLE.md).

### STD synchronization and I/O namespaces

The pinned STD uses synchronous defaults (`std::io::File`, `std::net::tcp`,
`std::time`). Import `std::io::asyn`, `std::net::asyn` or `std::time::asyn`
for explicit asynchronous operations. The former `::sync` paths are removed.
`std::sync::Mutex<T>` and `std::sync::asyn::Mutex<T>` acquire through `lock(&self)` and
release through scope-owned guards. These use ordinary lock/transfer contracts;
Mutex names are not compiler synchronization markers.
See the [STD API convention](https://github.com/omework/corbo-lang/blob/main/docs/ASYNC_API.md).
