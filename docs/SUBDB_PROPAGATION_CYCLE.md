# Subdb: lexical cleanup during error propagation

Compiler/backend fix; no grammar or normative-rule change.

`drop_partial_evaluation` walked beyond an enclosing lexical block and treated
its earlier binding nodes as expression temporaries. On a `?` error arm this
emitted nonexistent `t<binding-id>` references before the ordinary `v<binding-id>`
cleanup. The Subdb integration program consequently passed frontend checks but
its generated C failed to compile.

The walk now stops at AST kind 2 (a lexical block). Existing visible-binding
cleanup remains responsible for those locals; expression-level partial operands
remain under the existing partial-evaluation path.

The compiler was rebuilt from its readable source using the installed compiler
and the working STD. The focused `propagation_binding_cleanup` fixture compiles
and executes at O1 with fatal UBSan, producing `1` then `true`: the retained
local is destroyed once on propagation, then the caller observes the error.
Subdb's integration, rejection and restart fixtures also compile and execute
under fatal UBSan. See the sibling Subdb validation report for target evidence.

The temporary development compiler is `build/subdb/bin/corboc`. The release
install and STD lock were not changed or pinned to an unpublished working tree.
No broad language-safety proof, adversarial campaign or Rust frontend update
is claimed.
