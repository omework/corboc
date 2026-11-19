# Canonical Corbo language repository

## Scope

Repository/build configuration only. The language, STD and readable runtime now
live in [omework/corbo-lang](https://github.com/omework/corbo-lang). The compiler
remains in this repository. No compiler algorithm or language rule changed.

The language repository begins with one parentless snapshot commit,
`d5e96d158dee8cce6579f2c857b01a625a8407e3`, based on the 5,083 tracked din-lang
files at `f905f1afd8c462f633e0ae09d5f058ad9de6c321`. Its migration record and
updated repository instructions add one file, for 5,084 files in the new tree.
The earlier history remains in din-lang; it was not imported into corbo-lang.
Historical reports retain their original paths and commit references.

## Handoff

`corbo.lock` now uses `git@github.com:omework/corbo-lang.git` and pins the initial
snapshot. The README points to that repository and shows the sibling checkout
`../corbo-lang`. The dependency cache was checked clean, fetched through Git,
advanced to the new revision and assigned the new canonical origin URL. No
source files were edited inside the cache. The source-lock verification passes.

## Executed validation

- All original snapshot files were compared byte for byte before the intended
  README/repository-guide/matrix edits. STD/runtime code, grammar, language rules
  and validation guidelines remain byte-identical.
- The new checkout's generated reference check passes: 90 STD files / 1,382
  documented members and 32 runtime files / 775 documented members.
- README/source synchronization and the UTF-8 text example pass on macOS ARM64
  at O1 with fatal UBSan.
- Runtime resource generation is still current for the locked sources.
- `python3 scripts/build.py --seed build/repository-migration/seed` completes,
  installing the new source lock and STD.
- Its emitted C SHA-256 is
  `584dd5c2270488d46ad5a62569c156eeb2e159e1892435c0b7f98ad640105b60`,
  identical to the build before repository migration.
- The installed compiler builds a package directly from the new language
  checkout with `corboc build`; `build/feature_demo` prints `42`.
- The new language remote's default branch is `main`, pointing to the single
  initial snapshot commit. Both author and committer are Jabar.

Artifacts are retained under `build/repository-migration` and
`build/bootstrap/report.json`; the language snapshot comparison is retained in
that checkout's ignored `build/repository-migration/snapshot.json`.

No broad compiler campaign, full self-reconstruction campaign, other-platform
execution or independent safety audit was performed for this organization-only
change. Existing platform and safety limitations remain unchanged. The original
language checkout is retained and unmodified.
