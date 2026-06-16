# repo-signal Integration

`repo-signal` provides structured readiness and inspection signals.

## Relationship

It is a strong source for memory records because its outputs are already shaped
as stable JSON contracts such as `inspect.v1`, `doctor.v1`, and `report.v1`.

## Rule

When exported into mqobsidian, the schema provenance should be preserved so the
memory layer can always tell which runtime contract produced the record.
