# Package build defaults

## Scope

Build/CLI and manifest support only. No Corbo grammar, typing, ownership or
borrowing rule changed. The frozen Rust frontend is unchanged.

Accepted commands are `corboc build`, `corboc build PACKAGE`,
`corboc build -o OUTPUT`, and `corboc build PACKAGE -o OUTPUT`.
Without `-o`, the compiler reads `[bin].name`, falling back to `[package].name`,
and creates `PACKAGE/build/NAME`. An absent package argument means the current
directory. The filename policy appends `.exe` for Windows targets.

`[bin]` is optional, and an empty section keeps the package name. Binary names
are portable filename components containing ASCII letters, digits, `_`, `-`
and `.`, with at least one letter, digit or `_`. Empty names, paths, duplicate
properties/sections and unsupported properties are rejected. Section order is
independent of package/dependency handling. A dependency's binary configuration
does not change the importing package's output.

Explicit output paths keep their previous caller-relative behavior and parent
requirements. The existing temporary-directory/publication flow is reused;
failed compilation does not replace an existing executable.

## Implementation

The shared manifest parser records optional binary-name spans independently
of package and dependency spans. The default-output helper resolves the root
manifest and constructs a bounded, terminated path. The CLI handles the four
forms before source-file options. Its existing macOS ARM64 driver creates the
default directory with mkdir, accepting an existing directory but rejecting an
ordinary file in its place. No shell command string is built.

## Executed validation

```sh
python3 scripts/build.py --seed build/package-build/seed
python3 validation/check_package_build.py \
  --corboc build/install/bin/corboc --keep build/package-build/validation
```

All 18 recorded checks passed on macOS ARM64: nine successful build-and-run
commands, eight expected command failures, and a separate publication/cleanup
check. They cover package-name defaults, repeated builds, configured names,
current-directory `-o`, explicit package paths containing spaces, the legacy
explicit output form, an empty binary section, two-module packages with path
and STD dependencies on both sides of `[bin]`, empty/path/duplicate settings,
a missing manifest, a blocked build directory, malformed CLI arguments and
syntax failure. The failed-build witness retains the previous binary's SHA-256
and leaves no temporary workspace behind.

The updated language README source markers still match their complete packages;
the hello package executes, and STD/runtime generated-reference inventories
remain current. Sources, stdout/stderr, execution results and report.json are
retained under the ignored validation directory.

## Limits

The existing native build driver is macOS ARM64 only. Linux, Windows and macOS
x86-64 native build drivers are not introduced by this change. The Windows
filename suffix is represented in target-selected code but no Windows native
build execution is claimed. Windows ARM64 execution remains deferred.

No broad compiler corpus, full self-reconstruction campaign or independent
safety audit was required for this CLI/manifest change. The generated C is
compiled using the existing host toolchain settings.

## Published inputs and install build

`corbo.lock` pins `f905f1afd8c462f633e0ae09d5f058ad9de6c321`, which contains
the accepted manifest and README updates. The clean dependency checkout and
runtime resource freshness check pass. The final pinned install build completed;
its generated C SHA-256 is
`584dd5c2270488d46ad5a62569c156eeb2e159e1892435c0b7f98ad640105b60`,
identical to the development build used for the 18 focused checks.
The actual README package-root command builds `build/feature_demo` and executes
with stdout `42`. No explicit STD directory or output directory setup is needed.
