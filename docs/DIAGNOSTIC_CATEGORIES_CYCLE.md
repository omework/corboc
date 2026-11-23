# Diagnostic categories and implementation context

Compiler/tooling change. Grammar, normative rules, acceptance decisions, STD and
runtime remain unchanged. The frozen Rust frontend is untouched.

## Diagnostic pipeline

Human-readable source diagnostics name their category: syntax error, rule
violation or compiler limitation. Import/declaration resolution, configuration
and compiler-input failures retain separate explanations. Existing N1–N8 and
E-code identities and exit statuses remain available.

Parser expectations remain speculative until parsing fails. Common function
signature failures now retain the required name, opening parenthesis, parameter
name/type separator, parameter separator or return type. The renderer reports
the token actually encountered or end of input/line. Existing detailed let,
for-loop and block diagnostics remain active.

Rule violations retain the existing failure-site catalog, expected/actual type
summaries and move/drop/borrow provenance. Rendering category labels does not
alter that analysis.

For checker limitations, the unsupported AST node and a reason reach the
renderer before the caller reduces them to numeric status 9. Signature failures
can point at the actual parameter/return annotation rather than the start of the
function. The renderer names the construct and its enclosing function/impl using
the original-source map, including generated-name rewrites. Borrowed/dependent
Option parameters have an explicit signature-path explanation.

Terminal block-lowering failures and unsupported C signature types also retain
context. Speculative expression helpers do not emit errors: a failed probe must
not leave a diagnostic on an otherwise accepted alternative.

Limits are labelled as implementation limits, not evidence of a violated rule.
Some legacy failure paths still only establish that a form cannot be checked or
lowered; their message says that, rather than inventing a narrower cause. Source
mapping fallbacks remain explicitly labelled as anchors. This is not a claim
that every legacy error has an individually complete explanation or that all
status-9 programs are otherwise valid.

Raw frontend modes keep numeric diagnostics. A limitation reported at a more
precise annotation also has a more precise numeric offset; the numeric format
and status are preserved.

## Validation

`scripts/validate_diagnostic_categories.py` compares verdicts with the committed
baseline for syntax errors, type mismatch, a moved value and an unsupported
borrowed-Option signature; it asserts original coordinates, messages, categories
and raw protocol. An accepted enum-method program checks absence of spurious
errors. Existing source and semantic diagnostic suites cover imported sources,
watch recovery, rewriting, expected/actual types and move/borrow locations.

Execution/install results are recorded in the implementation checklist. This
change has no platform ABI or OS-specific behavior; host execution is macOS
ARM64. Windows ARM64 execution remains deferred.

## Adding a diagnostic

At a parser refusal, retain an expectation at the token being rejected and emit
only after the parse fails. At a normative refusal, keep its stable semantic
site and preserve expected/actual types or related ownership origins before
returning. At an implementation gap, call `diagnostic_limitation` with the exact
AST node and a description of the unsupported mechanism. Do not route invalid
syntax or an established rule violation through the limitation helper. Do not
infer a specific missing feature solely from the surrounding type name.

## Completed execution and installation

The nine installed-binary category observations pass, including the accepted
program, signature and statement limitations, top-level/method syntax and raw
protocol comparisons. The existing source-diagnostic suite passes 16 cases,
including watch recovery, imported origins and normal builds. The semantic suite
passes 13 observations/protocol comparisons and its failure-site/history audit.
No full compiler corpus or platform matrix was replayed for this tooling change.

Evidence: `build/diagnostic-categories/installed-results.json`,
`source-regressions.json` and `semantic-regressions.json`. The latter two ran on
the development build; the release was rebuilt from source with the new compiler
and rechecked with the category suite after installation. The last release-only
adjustment prevents lexical code numbers from acquiring an implementation-limit
note solely because they share a numeric code.

`14e3053` was committed and pushed as Jabar before diagnostic implementation.
The compiler was rebuilt/installed both before and after this work. The final
binary is `/Users/jabarkarim/sources/corboc/build/check-file/install/bin/corboc`;
interactive zsh resolves that path. Existing watch processes must be restarted.
The pinned STD/runtime revision remains unchanged. Diagnostic implementation,
focused validation and this report are recorded together in the compiler repository.
