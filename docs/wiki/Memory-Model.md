# mqobsidian Memory Model

This repo models MQ memory as structured, reviewable layers.

## Layers

- `decision-record.v1`: architectural decisions and durable boundaries.
- `repo-review.v1`: sanitized repository review outputs worth reusing.
- `learn-record.v1`: verified patterns, lessons, and reusable fixes.
- `stack-truth.v1`: current or recent stack status snapshots.
- `endpoint-truth.v1`: endpoint or UMS readiness snapshots.
- `context-pack.v1`: small task-scoped context bundles for Codex and Claude.

## Rules

- Every stored artifact should have a schema name and timestamp.
- Facts should be separated from interpretation and recommendation.
- Sensitive details must be removed or replaced before export.
- Runtime truth stays in the source repo or tool.
- Root instruction files should stay short.

## Lifecycle

```text
raw signal
  -> validated output
  -> sanitized export
  -> memory record
  -> reused as future context
```
