# SubDB facade: structural methods and owned fixed fields

Compiler/backend corrections required by an API implementation. No new primitive,
grammar or normative memory rule. The Rust frontend stays frozen. The STD pin and
release installation were not changed to an unpublished working tree.

## General mechanisms

- Independently constrained methods on a nongeneric owner are promoted to ordinary
  generic function recipes. The receiver becomes an explicit argument, preserving
  receiver evaluation, reference mode and ordinary structural signature checks.
  The `?` expression contributes its successful payload type to receiver inference.
- Dependency-free fixed records use the existing structural `value_record` summary
  consistently for returns, envelope reconstruction and native worker captures.
  This includes owned fixed arrays and nested records. Dependency-bearing records
  remain on the existing dependency path.
- Owned fixed-array fields are inline C values, even above the freestanding-array
  datastack threshold. Previously a large field was a pointer into a constructor's
  temporary datastack storage: a returned context could alias a later context.
  Only direct owned array fields are inlined; arrays behind references, allocation
  wrappers and pools keep their existing representation. Freestanding arrays
  continue to use the placement plan and datastack.
- The early call-reservation check uses the existing disjoint-field proof, matching
  the later argument checker; mutable aliasing of the same field still fails.
- Fixed arrays accept named structurally replicable record values as elements.
  Evaluation uses ordinary moves and preserves nominal record identity. Subsequent
  use of a moved element binding is rejected. This does not extend replication to
  owning resources, references or user destructors.

The preceding lexical-block `?` cleanup correction is documented separately in
[SUBDB_PROPAGATION_CYCLE.md](SUBDB_PROPAGATION_CYCLE.md).

## Focused evidence

Four accepted programs execute with O1/fatal UBSan: generic method invocation
(`42`, `1`), returned nested records with independent 8192-byte fields (`true`,
`true`), disjoint mutable fields (`true`), and lexical propagation cleanup (`1`,
`true`). Three negatives reject missing contract methods, overlapping mutable
fields and reuse after an array-element move. The retained snapshot is
`validation/subdb-facade-results.json`; `scripts/validate_subdb_facade.py` reruns
these seven checks with an explicitly selected development compiler and STD.

The SubDB application adds thirty observations covering registration/reopen,
optional requested indexes, logical frame loading, compressed groups, captured
index/data bounds, schema mismatch, invalid ranges and two native reader threads.
Its earlier storage/rejection/restart programs still execute under fatal UBSan.
Platform results and precise limits live in the sibling SubDB validation report.
This focused work is not a general language-safety proof or adversarial campaign.

## Development build

`build/subdb/bin/corboc` is the rebuilt development compiler. It is used with the
working sibling STD explicitly; the release install and `corbo.lock` are unchanged.
Generic-owner methods still use the existing nominal specialization mechanism;
this pass targets independently generic methods whose owner is already concrete.

## Publication follow-up

The previously separate development changes are published together with the
mutation-permission cycle. The compiler now pins committed Corbo revision
`d54cf3063861498fc721b78d9bbd11ba6ac8f667`, including the required File APIs. The earlier aliased-buffer refusal was
reclassified as a valid content-only aliasing case under MA1–MA6; historical
snapshots retain their original verdicts.
