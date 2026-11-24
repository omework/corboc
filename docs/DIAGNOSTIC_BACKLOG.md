# Pending diagnostic improvements

## Borrow required for a slice argument

Status: recorded; not implemented. This is diagnostic work, not a language-rule
or implicit-borrowing change.

Given an API parameter `output: &mut [u8]`, a call with `buf[..]` currently
produces E0009, claiming an unsupported operand/dependency form. The same call
with `&mut buf[..]` is accepted, including when its Result is discarded.

Expected diagnostic:

- Point at the buffer argument, not the beginning of the complete statement.
- Explain that the argument requires an explicit mutable borrow.
- Show expected `&mut [u8]` versus the unborrowed slice expression `buf[..]`.
- Suggest `&mut buf[..]`; do not insert a borrow automatically.
- Use the ordinary argument/type error category, rather than a compiler limit.
- Preserve the independently chosen Result handling policy.

Observed with `std::encoding::binary::write_u16_be(value, buf[..])`.
Both `write_u16_be(value, &mut buf[..]);` and binding/unwrapping its Result pass
with installed corboc `52c816c` on macOS ARM64.

## Separate analysis defect: guard over one field blocks a sibling field

Status: corrected by the field-projection implementation. See
[the implementation report](FIELD_DEPENDENCIES_CYCLE.md).

In an async instance method, keeping the result of
`self.tracker.lock().await` alive causes a subsequent shared method call on
`self.other` to be rejected by N5. Releasing the guard before accessing the other
field makes the otherwise identical source pass. This reproduces the reported
`self.file.write_at(...)` refusal in WAL without using File or network IO.

The retained guard dependency uses the aggregate root, and the current
field-disjointness proof fails to recover/use the tracker projection. The
compiler should preserve and use the field path across acquisition/await and
the returned guard. Tracker and file are disjoint fields; the guard must retain
its target's lifetime and lock dependencies without reserving every sibling
field. This is an implementation precision issue, not a new language rule.
