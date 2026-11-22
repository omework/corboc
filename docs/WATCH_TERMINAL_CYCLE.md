# Interactive watch refresh

Scope: CLI presentation only. No language-rule, STD or runtime changes.

Watch clears the visible terminal before each check, including the initial check
and scan failures. It reprints the watch status afterward. Unix checks stderr
with `isatty` and leaves absent/`dumb` TERM unchanged; Windows uses console APIs.
Redirected logs remain append-only. Clearing does not erase terminal scrollback.

Validation: three focused macOS ARM64 observations passed: an xterm pseudo-terminal
clears both initially and after a save introducing a diagnostic; a dumb terminal
and a redirected pipe preserve output without escape sequences. All three report
the new source error. Rebuilt and updated the local compiler installation. Windows
execution has not been repeated for this presentation change.
