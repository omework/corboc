# Mutex synchronization namespaces

API/package organization only. No grammar, ownership, borrowing, lock or runtime changes.

- Move Mutex and MutexGuard to `std::sync` and `std::sync::asyn`.
- Remove the former root and `std::asyn` declarations; no compatibility aliases.
- Update compiler private-layout paths and the private async wait-hook path.
- Update README EN/FR, API guides, source-linked API reference and fixtures.

## Focused validation

The rebuilt corboc passed three existing executable programs with fatal UBSan
on macOS ARM64: scalar guards (`42, 42`), contending native/async tasks (`3, 4`),
and aggregate payload cleanup (`41, 99, 99, 41`). All ten existing refusal cases
remain rejected, including forged guards, foreign private-field access and
private wait-binding import. Generated STD/runtime documentation checks pass.

Explicit imports of both Mutex and both MutexGuard types succeed at their new
paths. Imports from `std::Mutex` and `std::asyn::Mutex` fail with import diagnostic 13.

The runtime and platform backends are unchanged. Prior platform execution
results remain in SYNC_DEFAULT_MUTEX_CYCLE.md; they were not rerun for this move.
Windows ARM64 execution remains deferred. No broad corpus or safety audit.

Reproduce from corboc:

```sh
python3 scripts/validate_mutex.py --compiler build/asyn-mutex/corboc-sync-namespace --stdlib ../corbo-lang/stdlib/src --out build/mutex-namespace
```

## Pinned installed build

STD pin: `046d01ff261affb66955e645809c593814516ac0`.
The updated compiler was reconstructed and installed with the pinned STD.
Normal `corboc build` resolves its bundled STD and builds the README mutex
example, whose executable prints `42, 42`. The generated runtime bridge check
passes. Multi-generation equivalence was not rerun for this package move.
