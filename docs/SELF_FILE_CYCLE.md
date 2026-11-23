# Self aliases and text-path File APIs

Compiler/core: `Self` resolves to the enclosing impl target before generic
specialization, retaining source offsets for diagnostics. Constructor literals,
associated calls, receivers and borrowed types use that alias. Module linking
leaves `Self` for this scoped resolution. No ownership or borrowing rule changes.
Four native programs cover receivers, generic types, `&Self` and an imported
implementation. Outside-impl aliases and additional generic arguments reject
with E0111/E0112. `validation/check_self_type.py` maintains these checks.

API/STD: public sync/async File open, create, rename and delete accept UTF-8
`&str`. The private syscall boundary keeps bounded NUL-terminated buffers.
FileMode READ and WRITE are independent bits; CREATE, EXCLUSIVE, CREATE_NEW,
APPEND, TRUNCATE and SYNC compose explicitly. Existing aliases remain available.
The API caps paths at 32767 UTF-8 bytes and rejects empty or embedded-NUL paths.

Async contracts omit static text views from caller-root reservations: their
storage does not belong to a caller scope. Non-static views retain their
existing root and loan links. No File-specific verifier exception was added.

The compiler's internal byte-path boundary converts UTF-8 before invoking File.
Package checks/builds and compiler source emission use that same adapter.
The compiler rebuild uses an explicit working-STD override, recorded with a
source digest; the committed STD pin has not been silently changed.

Validation results are recorded below after target execution. The Rust frontend
is frozen. Cross-target emitters run on the host and produce target programs;
they are not native compiler binaries. Windows ARM64 execution remains deferred.

## Results

- Four native Self programs pass, including imported/generic associated calls;
  two invalid forms reject with the expected diagnostics.
- Sync and async File API probes execute on macOS ARM64/x86-64, Linux x86-64
  and Windows x86-64 under Wine. Windows ARM64 compiles and links only.
- Unix runs use fatal UBSan. Exact Windows ACL verification is not claimed:
  Wine returns ERROR_NOT_SUPPORTED, so the Windows API probe uses DefaultMode.
- Existing positioned-I/O sync/async host probes pass under fatal UBSan and keep
  their invalid-lifetime refusal.
- The compiler rebuild, `new` followed by package `check`, and installed Self
  check pass. The active installation is `build/check-file/install/bin/corboc`,
  with the matching working STD and recorded development-source digest.

The STD pin now references Corbo `d6601104146b0b84b03849c55fc1111184c44d1c`.
The normal pinned build resolves that API; the explicit --stdlib-dir option
remains available for development.
