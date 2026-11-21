# Positioned File API pin

API/STD integration, 2026-11-22. No frontend, verifier or runtime change was
needed in corboc. The existing compiler accepts the new shared-receiver
read_at/write_at methods and their async worker forwarding.

STD pin: `e577e97319ff7bda3c9e4b15af0b53158e732ecb`.

The pinned language report `docs/cycles/FILE_POSITIONED_CYCLE.md` and its JSON
record sync/async cursor preservation, independent byte checks, range/mode/EOF
behavior, rename, move cleanup and a pending-Future owner-destruction refusal.
They execute under fatal UBSan on macOS ARM64/x86-64 and Linux x86-64, and under
Wine on Windows x86-64. Windows interposition verifies closure of companion
handles and per-request events. Windows ARM64 is compile/link-only; execution
remains deferred.

Cross-target code uses host-running test-only variants of current corboc with
matching target and assembly/register behavior; it does not establish native
compiler execution on each target. The maintained create_target_emitter helper
now accepts `--arch aarch64` as well as its existing x86-64 default; its command
line parsing was checked. Runtime sources are unchanged. No broad corpus or
self-reconstruction was repeated for this API change.
