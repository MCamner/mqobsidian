# repo-signal Integration

`repo-signal` provides structured readiness and inspection signals.

## Relationship

It is a strong source for memory records because its outputs are already shaped
as stable JSON contracts such as `inspect.v1`, `doctor.v1`, and `report.v1`.

## Rule

When exported into mqobsidian, the schema provenance should be preserved so the
memory layer can always tell which runtime contract produced the record.

## Review export

`repo-signal review-export [path]` runs a fresh `inspect.v1` analysis and writes
a compact `repo-review.v1` Markdown note under `reviews/`. It preserves
`source_schema: inspect.v1`, omits the target repository's absolute path, and
refuses to replace an existing same-day export unless `--force` is explicit.

Use `$MQ_OBSIDIAN_DIR` to select the vault, or pass `--vault PATH` explicitly.
Observation emission remains a separate, opt-in proposal flow.
