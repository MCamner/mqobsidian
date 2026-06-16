# mqobsidian Memory Model

This repo models MQ memory as structured, reviewable layers.

## Layers

* `decision-record.v1`
  Architectural decisions and durable boundaries.
* `repo-review.v1`
  Sanitized repository review outputs worth keeping as reusable context.
* `learn-record.v1`
  Verified patterns, lessons, and reusable fixes.
* `stack-truth.v1`
  Current or recent stack status snapshots.
* `endpoint-truth.v1`
  Enterprise endpoint or UMS readiness snapshots.
* `context-pack.v1`
  Small task-scoped context bundles for Codex and Claude Code.

## Rules

* Every stored artifact should have a schema name and timestamp.
* Facts should be separated from interpretation and recommendation.
* Sensitive details must be removed or replaced before export.
* Runtime truth stays in the source repo or tool; mqobsidian stores the memory
  of it, not ownership of it.
* Root instruction files should stay short; deeper context belongs in reusable
  cards or task packs.

## Lifecycle

```text
raw signal
-> validated output
-> sanitized export
-> memory record
-> reused as future context
```
