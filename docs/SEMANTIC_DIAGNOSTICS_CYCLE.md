# Semantic diagnostic context

This compiler/tooling change enriches diagnostics without changing grammar,
normative rules, verifier return values or ownership assignments. The Rust
frontend and pinned STD/runtime remain unchanged.

## Implementation

Each normative refusal carries a stable failure-site identity and a description.
The [site catalog](SEMANTIC_DIAGNOSTIC_SITES.json) records its rule, source
function and local condition. Type comparisons can retain explicit expected and
actual type codes. The renderer also uses the active operation, binding,
parameter annotation and constructor spelling to recover source-level names.
It does not expose linked internal identifiers as user type names.

Diagnostic history observes checked-value writes after the existing assignment.
It retains move, destruction and borrow origins and distinguishes an explicit
`drop` from other consumption. Failed dependency walks retain the unavailable
root; conflicting-borrow checks retain the conflicting reference. Secondary
labels pass through the same original-source mapping as primary errors.

The diagnostic service uses bounded storage and scoped read-only native views
of the AST, static graph and checked values. Views are invalidated before their
owning verifier returns; nested operation frames restore alternate worker views.
ABI size and alignment assertions guard the private native record mirrors.
No diagnostic writes through these views or alters a verifier verdict. Unknown
or unavailable type information is not replaced with an invented concrete type.
Some compound constraints retain a broader operation description when the
verifier has no finer subreason. A related location may identify the enclosing
operation rather than one exact token.

## Focused validation

The source audit checks coverage of 1,006 failure-site identities and observation
of 346 checked-value constructor writes. These are instrumentation counts,
not 1,006 executed semantic tests.

The focused runner compares rejection verdicts with the preceding installed
compiler and inspects diagnostic contents for primitive and nominal mismatches,
arguments, undefined values, moves, explicit destruction, mutation permission,
escaping references and destruction with a live borrow. It also checks accepted
iteration and the unchanged raw `--verify` protocol.

Executed on 2026-11-22, macOS ARM64:

- Thirteen final semantic observations pass on the self-rebuilt binary; all eleven
  rejected examples retain the baseline verdict and exit status.
- Sixteen existing source-diagnostic observations and ten iteration regressions
  pass on the preceding diagnostic generation. This includes imported sources,
  generic and closure lowering, watch recovery, normal build and accepted
  executable iteration/cleanup examples.
- The diagnostic compiler successfully rebuilds the final compiler from its own
  package. This is a self-rebuild, not a three-generation byte-identity campaign.
- The final binary replaces `build/check-file/install/bin/corboc` atomically.
  Accepted and rejected installed smoke checks pass, including expected/actual
  output. The installed STD remains at the existing pinned revision.
- `git diff --check` passes. No fresh Linux/Windows execution was performed;
  Windows ARM64 execution remains deferred.

[Recorded observations](SEMANTIC_DIAGNOSTICS_RESULTS.json).

Reproduce the semantic checks with:

```sh
python3 scripts/validate_semantic_diagnostics.py \
    --compiler build/semantic/rebuilt/bin/corboc \
    --baseline build/semantic/baseline-corboc
```

The focused suite checks diagnostic content and preserved verdicts. It is not
an adversarial rule-breaking campaign or a proof of verifier correctness.
