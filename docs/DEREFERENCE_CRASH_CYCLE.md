# Unresolved dereference receiver crash

The installed compiler aborted with `corbo: borne de tranche hors du tableau`
while checking the selected WAL file. An exit breakpoint traced the abort to
`mutation_consumer` in `src/generics/dereference.crb`.

A failed method lookup returned node zero, which was then interpreted as a
method declaration. Its unrelated first declaration/field was used as a receiver
annotation, producing a reversed source slice. In addition, generic wrapper
ref targets could still be T when their consuming method was classified.

The fix leaves unresolved/non-instance methods to ordinary diagnostics,
validates a typed borrow annotation before slicing it, and defers generic
wrapper dereferencing until specialization resolves its target. A related
by-value receiver regression exposed a second abort: the shared borrow-prefix
classifier subtracted one from an empty prefix. It now first requires an actual
leading ampersand, and otherwise reports a non-borrowing prefix.

This is a compiler implementation fix, with no language-rule, grammar, STD or
runtime changes. The Corbo revision remains pinned. The Rust frontend is frozen.
Validation is limited to focused reference-method cases and watch recovery on
macOS ARM64; no full platform/adversarial replay is claimed.

The actual SubDB source is not edited. Its selected-file check now reaches an
ordinary field diagnostic: a guard over Tracker dereferences to Tracker, so
`(*guard).tracker.cursor` asks for a nonexistent tracker field; the payload's
cursor is `(*guard).cursor`.

## Completed validation and installation

All 18 focused reference-method cases pass, including seven executable programs
under fatal UBSan and eleven refusals. The new cases cover a missing method,
a non-borrowing consuming receiver, an invalid by-value ref method, and mutable
method use through a specialized generic wrapper. Compiler runtime abort text
is explicitly forbidden in these checks. The diagnostic-site/history audit
passes without new refusal sites or normative rule changes.

Watch reports the unresolved-method diagnostic, remains alive, and reports
success after saving a valid test program. The unchanged WAL source reports its
normal field error while watch remains alive. The rebuilt binary is installed
at the existing PATH. Machine-readable evidence is in
`docs/DEREFERENCE_CRASH_RESULTS.json`. Restart existing watch processes.
