# Field-specific retained dependencies

Scope: compiler/core. The user explicitly restored the prototype policy of one
active mutable reference per overlapping place. No grammar or STD API changed.

## Cause and representation

A guard produced by `self.tracker.lock().await` retained `self` as its lifetime
root. Access checking reused that whole root and lost the tracker field path.
Consequently, an access to the sibling `self.file` was rejected.

CheckedValue now carries `projection`: the first selected field below its
lifetime `target`; zero means whole or unknown storage. All constructors
initialize it explicitly, and the native diagnostic view has the matching layout.
Receiver/argument preparation, returned-value summaries, task copies and retained
lock markers carry this fact. Async launch checking uses the captured receiver
for the field proof and the enclosing launch for execution ordering.

Disjointness follows the retained constructor dependency graph and must hold for
every dependency on the same root. A different field can permit access; an equal
or unknown projection cannot. The lifetime root stays unchanged, so destruction
of the containing object still conflicts. This is independent of concrete
Mutex, File or other nominal type names. Precision is currently at the first
field selector; unknown or deeper unresolved cases remain conservative.

## Mutable-borrow policy

Ordinary mutable borrow creation and simultaneously retained call arguments no
longer use the prior permission-only overlap exemption. Two active mutable
borrows of the same place are rejected. Disjoint fields and successive borrows
after the preceding last use remain accepted. Shared lock APIs retain their
declared synchronization contracts; lock implementations remain developer-owned.

The accepted temporary policy is documented in the language repository's
`docs/MUTABLE_ACCESS.md`, its French counterpart and the canonical N5 summary.

## Validation

Focused runner: `scripts/validate_field_dependencies.py`. Positive cases execute
with fatal UBSan, negative cases require a normative refusal rather than an
unsupported-feature exit. The nine initial cases cover async/sync sibling
access, disjoint field borrows, successive mutable borrows, overlapping local
and argument borrows, same-field acquisition, whole-owner access and owner drop.
All nine passed on macOS ARM64.

The existing 18 reference-method cases and 13 mutex cases also passed. The
diagnostic-site audit passed: 1,017 sites and 353 observed state writes. A rebuilt
compiler accepted its own complete source. The tenth observation uses the real async File API: a tracker guard remains live
across `write_at(&data[..], cursor).await?`, then its cursor is updated. It writes
two bytes and passes with fatal UBSan. All ten focused cases pass on the final
build; async guard dereferencing and all 13 mutex cases were rerun after the
launch-path correction and pass.

The final compiler is installed at
`build/check-file/install/bin/corboc`, the existing shell PATH location. Its
SHA-256 is `57e82e9b9f1824f13aa17cb9253bf9d24af79fc3b545a6231d04361d0bd5c82c`. The STD/runtime source is unchanged.
The language documentation is committed at `81b9f93642ee137ef571197c6a9fac79c80ec2f3`;
`corbo.lock` pins this revision. The final requested rebuild uses this pin.

No cross-platform replay was performed: this changes shared compiler analysis,
not platform code. Windows ARM64 execution remains deferred. These observations
are regression evidence, not a general safety proof.

## Remaining independent issue

The unchanged SubDB source also contains an unborrowed `buf[..]` argument where
File expects `&[u8]`. Its diagnostic is separately recorded in
[the diagnostic backlog](DIAGNOSTIC_BACKLOG.md). SubDB was not edited.
