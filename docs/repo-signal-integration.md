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

## Observation emission

Emission is opt-in and failure-isolated. When enabled, a real `inspect` run maps
its top issue to one `memory-observation.v1` record appended to
`memory/observations/repo-signal.observations.jsonl` in the vault.

An observation is a proposal, not a memory. Producing one does not promote it:
scoring and promotion stay with `mqobsidian`. All MQ repos may produce
`memory-observation.v1` records (ADR-008); `repo-signal` is one such producer,
not a special case.
