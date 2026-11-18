# Compiler extraction verification matrix

| Property | Evidence | Status |
| --- | --- | --- |
| Compiler source preservation | 81 source/package files compared before removal of the old directory; only generated-resource metadata and one source comment differ. No language algorithm changed. | Complete |
| Shared-source identity | One exact revision for STD/runtime/spec, checked cache and regenerated resource. | Six source-lock checks passed |
| Self-hosting and installed STD discovery | Two rebuilt generations, byte-identical emitted compiler C, normal self-build and external two-module program. | Complete on macOS ARM64 |
| Compiler mechanisms | Core-extension, generic/tuple and C runtime bridge regression suites. | Three suites and historical forwarder completed on macOS ARM64 |

The full language-rule matrix and historical platform evidence remain in the
language repository at the revision named by `corbo.lock`. This table records
only extraction evidence; it is not a new safety audit.

[Detailed executed evidence and limits](REPOSITORY_SPLIT.md).

## Corbo runtime integration

| Property | Executed evidence | Scope |
| --- | --- | --- |
| Freestanding runtime boundary | Two scalar accepts, six managed/unchecked-boundary refusals; normal application suites passed. | Host macOS ARM64; no new language rule |
| Resource packing | Five independent round trips and actual Corbo decoder execution across 64 KiB history wrap under fatal UBSan. | Controlled generated resources, not an untrusted-stream API |
| Integrated runtime | Core-extension, generic/tuple/registry and C bridge suites passed; pinned Corbo implementation selected by default. | Host; platform runtime comparisons and network runs recorded in the language cycle report |

[Corbo runtime cycle](CORBO_RUNTIME_CYCLE.md).

Pinned reconstruction completed: three byte-identical generated compiler C files,
normal compiler self-build and external two-module program printing `42`.
Native compiler execution remains macOS ARM64 evidence.
