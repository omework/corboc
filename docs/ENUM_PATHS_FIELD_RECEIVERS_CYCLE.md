# Enum qualification and field method receivers

Compiler/core integration with an approved enum spelling extension. Normative
ownership, borrowing, synchronization and branch rules remain unchanged. The
Rust frontend remains frozen. No STD/native runtime/OS ABI implementation changed.

## Enum paths

`Enum::Variant`, including positional/named payloads, lowers to the same enum
AST as the retained compatibility spelling `Enum.Variant`. Known enum member
separators are marked during nominal token classification without modifying
source spans or lexer output. Pattern parsing retains the final qualified member
separately from its owner; this also covers import aliases. Qualified owners,
Self and generic specializations continue through existing name resolution.
Associated calls such as `Enum::create()` keep their function-call meaning.
Enum values in struct fields reuse the declared-type constructor checking path,
including direct empty variants and named/positional payload constructors.
The language repository updates its grammar, rule documents, README variants and
feature example to the preferred spelling.

## Projected receiver identity

Method lookup derives nominal identity through nested field places instead of
requiring a bare variable. Reserving a borrowed receiver uses the ordinary place
resolver to check owner liveness, access visibility and mutation permission.
The reference summary retains the original owner's target and parent loan and
the projected type. Returned borrows/lock contracts keep those dependencies.
A consuming receiver still follows the ordinary argument move/copy path.

The backend evaluates a projected receiver's address before arguments and uses
that address for the existing function/async invocation path. It does not copy
an owning object to call its methods. Poll frames retain projected receiver
pointers across a supported suspended argument. The existing sole-argument
await lowering boundary now also accepts a method-call parent.

This does not add implicit dereference syntax for arbitrary reference bindings:
`(*holder).field.method()` follows existing rules, while implicit `self.field`
continues to work. Dynamic indexing of multi-element aggregate arrays has its
separate existing place-analysis limits; this change does not claim to remove
those limits or arbitrary awaited-argument restrictions.

## Diagnostics

The retained sites explain that `?` requires Result/Option, that a Future needs
awaiting first, and that `.await` requires an async context. A missing-field
failure retains the member declaration before returning: the message names
both member and struct and labels the required field's declaration. Source
rewrite anchors remain explicit when exact original locations cannot be retained.

## Validation scope

`scripts/validate_enum_paths_field_receivers.py` executes qualified/aliased enum
patterns and construction, named/positional payloads, generic/Self paths,
associated methods, enum-field copying, nested synchronous/mutable/async field
calls and a real STD asynchronous mutex guard under fatal UBSan. The method
argument case suspends after the receiver was prepared. Focused refusals cover
mutation permission, a still-borrowed owner being destroyed and the three
reported diagnostic families. Existing enum and semantic-diagnostic suites
supply directly related regressions.

Results and install status are tracked in the implementation checklist. Execution
host is macOS ARM64. No full platform matrix was replayed for this target-neutral
compiler change; Windows ARM64 execution remains deferred.

## Completed evidence

All three new fixtures execute with fatal UBSan and their expected outputs:
qualified enum paths/aliases/generics/Self and field copies; nested field methods
with a suspended argument; and the STD async mutex as a field. Its protected
payload also contains a fixed array of `(usize, enum)` tuples. Five focused
refusals pass for synchronous await, Future propagation, a missing field,
mutation permission and a borrowed mutex owner's destruction.

The existing enum suite passes four executable fixtures and ten refusals against
the complete compiler. The semantic suite passes its site/history audit and
13 observations/protocol comparisons against the preceding compiler build.
Evidence is in `build/enum-paths-field-methods/evidence/results.json`,
`enum-regressions-final/results.json` and `semantic-regressions.json`.

A fresh compiler rebuild from the updated Corbo sources succeeds with the pinned
STD/runtime. Its binary was installed atomically at
`/Users/jabarkarim/sources/corboc/build/check-file/install/bin/corboc`.
The installed binary checks all three new fixture packages, and interactive zsh
resolves that exact path. Existing watch processes need restarting.

No SubDB source was edited. The language repository has specification, grammar,
README translations and enum example updates only; runtime and STD source are
unchanged. The shared-source pin now references `895ec887e00ed6cebc484bfe847d6e8dbf0c648f` to keep the grammar
and rules aligned with the committed language revision. Both repositories record
these changes as Jabar.
