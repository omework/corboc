# Static binary byte-order namespaces

Scope: STD API change plus the target-selection property needed by that API.
No ownership/borrowing rule, runtime primitive or frozen Rust frontend change.

## Implementation

The STD adds `LittleEndian`, `BigEndian` and `NativeEndian` in
`stdlib/src/encoding/binary/orders.crb`. Static read/write methods cover u8, u16,
u32, u64, i32, i64, f32, f64, bool and usize on supported 64-bit targets. They
delegate to existing binary functions without hidden storage. Existing flat
functions remain available. NativeEndian uses conditional static implementations,
not a new language-level type-alias mechanism or runtime dispatch.

`target.endian` selects `"little"` or `"big"` using native compiler-target
preprocessor metadata; the compiler build must determine its byte order. Windows
uses its supported little-endian target convention. The property participates in
the existing selection pass before import resolution. It describes the compiler's
configured target, consistent with the other target properties.

The user removed the private NAME constant as unnecessary. No NAME member was
added. The temporary exploration of string-literal constants was reverted; no
string-constant grammar or compiler extension is included.

## Focused execution

`scripts/validate_binary_orders.py` passes two programs with fatal UBSan:

- All 60 read/write methods, using representative values for each primitive and
  trailing-byte sentinels; explicit known little-/big-endian bytes; native-order
  selection; short-buffer output preservation and invalid-boolean rejection.
  The program emits 35 successful checks.
- Target selection with an inactive invalid import, proving excluded branches
  are removed before import resolution on the executed little-endian target.

The README binary example builds with automatic installed-STD discovery and
prints `4`, `16909060`, `67305985`. STD/runtime documentation inventory checks
pass after regenerating the STD reference.

Execution is on macOS ARM64. Explicit big-endian encoding is exercised on that
host; no big-endian-host, Linux or Windows execution is claimed for this API lot.
Windows ARM64 execution remains deferred. No broad corpus/safety campaign ran.

## Installation

The compiler is installed at `build/check-file/install/bin/corboc` with SHA-256
`e605b521ca973ccc9cc0116ff16bc365c82a27974c0ecc424a2145e89175dc09`. Validation used the development STD snapshot from the sibling language checkout.
On publication, `corbo.lock` was advanced to
`86433deda39ae82e4d840859a9007cfcdb7136c1`. Its STD digest matches the installed
tested snapshot exactly. Installation metadata now uses this pin and no
`development-stdlib.json` override. The native compiler binary is unchanged.
Results and installation metadata are under `build/binary-orders-final/`.
