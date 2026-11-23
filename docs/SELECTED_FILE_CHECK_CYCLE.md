# Selected-file checks and watch targeting

Scope: compiler CLI/source loading. No grammar, language-rule, STD or runtime
change. Directory checks and builds keep their complete-package behavior.

## Behavior and representation

`corboc check path/to/file.crb`, with or without `--watch`, retains that physical
file as the primary target. `PackageFile` now records its source-path range in
the name arena separately from its module identity. Package loading preserves
that identity through dependency visibility assignment.

For a package-backed file, discovery starts from its module and follows qualified
references/imports transitively. Module companions remain present; imported
modules are required context and can produce diagnostics. Grouped imports,
module aliases with qualified descendants and target-conditional imports are
handled before unrelated source files reach full parsing/checking. The linker
still resolves symbols and enforces visibility and alias rules within that
context. The selected source is copied first with the existing origin-map
machinery; source locations retain the original paths and lines.

The installed STD remains available through ordinary linking. Package manifests
and source-loading failures can still prevent checking; this is not error
recovery through broken required context or a claim that the whole package is
valid. Use a directory target to validate the complete package.

Watch discovery remains conservative: local dependency trees, installed STD,
manifests and source changes trigger a fresh check of the same selected target.
It never replaces that target with the changed file. Missing selected files are
reported against their own path and recover after recreation. Standalone-file
behavior is unchanged.

## Focused evidence

`scripts/validate_check_focus.py`: nine direct checks and one watch sequence pass.
They cover selected semantic and syntax failures despite unrelated broken files,
valid target isolation, imported dependency failures, module companions, full
package checking, namespace aliases/descendants, grouped imports, excluded target
imports, and recovery across selected-file/dependency edits.

The existing `scripts/validate_file_watch.py` suite passes all seven recorded
cases, including standalone STD edits, atomic saves, deletion recovery, both
watch flag orders, transitive path dependencies and manifest graph changes.
A normal two-module package builds and its executable prints 42.

The compiler rebuild succeeds. The active binary is
`build/check-file/install/bin/corboc`. A check of the user's WAL file reports its
own line 18 rather than an unrelated main-module diagnostic. SubDB files were
not edited. These observations do not establish that the WAL implementation or
the entire SubDB package is otherwise valid.

Validation host: macOS ARM64. No target-specific native API or ABI was changed;
platform suites were not replayed. Windows ARM64 execution remains deferred.
The Rust frontend remains frozen.
