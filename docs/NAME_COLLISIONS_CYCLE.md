# Rich duplicate-name diagnostics

Date: 2026-11-24. Compiler/tooling change; no syntax, namespace or ownership rule changes. STD/runtime inputs and the Corbo lock are unchanged.

E0014 identifies the local name being introduced, the existing component's kind and qualified module identity, and the incoming component's kind and identity. It points at the imported name/alias rather than the use keyword and displays related source snippets for both declarations. Repeated import names include the previous import's binding location. Duplicate declarations suggest a rename; an import collision suggests as; an ambiguous type/module path receives a path-disambiguation hint.

Names are described before linker mangling. The existing bounded source-provenance controller carries related origins and renders the richer resolution message. Source labels and text are reset with the existing check/watch context. Import failures emit one diagnostic rather than appending a second generic E0014. The numeric/machine interface is unchanged.

## Executed validation

[Eight focused observations](NAME_COLLISIONS_RESULTS.json) pass: root-module type versus imported child type (the reported arrangement), two imports, conflicting aliases, two same-module declarations, module/type path ambiguity, successful alias disambiguation, and existing syntax/type formatter behavior. Five failing resolution verdicts match the baseline; all five raw emit-package-c stdout/stderr/exit tuples remain identical. The root/import case asserts both source files, both qualified identities and the exact imported-name column. The current SubDB main file also checks successfully; no SubDB source was edited.

The compiler was rebuilt and installed at the existing PATH. Host execution: macOS ARM64. No new platform-specific behavior was added; Linux/Windows execution was not repeated and Windows ARM64 remains deferred. These focused observations are not a general compiler-safety proof.

Reproduce using scripts/validate_name_collisions.py with --compiler, --baseline and --out. The pre-change binary is retained at build/mixed-members/ready/bin/corboc in this checkout. Restart a running watch session to load the new executable.
