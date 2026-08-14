# mqobsidian Memory Model

This repo models MQ memory as structured, reviewable layers. It owns 23
contracts, each declared in `.mq/repo-contract.json` and backed by a
`schemas/<name>.v1.json` file. Consumer repos may validate against these shapes
but must not redefine them locally.

## Records vs manifests

Per DEC-002, two layers are kept distinct:

- **records / events** — source evidence and history. Consumers do not rebuild
  current truth from these.
- **manifests / views** — the current-truth surfaces, answering "what is true
  right now?" as a read, not a computation.

## Records and events

| Contract | Purpose |
| --- | --- |
| `memory-observation.v1` | One evidence-bearing observation a repo emits when it notices a potentially reusable pattern. A proposal, not a memory. Producers: all MQ repos. |
| `memory-score.v1` | Current ranking and promotion tier of one memory. `mqobsidian` is the sole producer. |
| `promotion-event.v1` | Audit-trail event recorded when a memory changes tier. `mqobsidian` is the sole producer. |
| `memory-query.v1` | A repo asking `mqobsidian` for relevant memory before or during a task. Read-only. |
| `workflow-observation.v1` | One sanitized workflow-run observation. `mqobsidian` owns the vocabulary; `mq-agent` emits records. |
| `feedback-signal.v1` | One pack-usage feedback event. Kept separate from promotion. |
| `decision-record.v1` | Architectural decisions and durable boundaries. |
| `learn-record.v1` | Verified patterns, lessons, and reusable fixes. |
| `repo-review.v1` | Sanitized repository review outputs worth reusing. |
| `stack-truth.v1` | Current or recent stack status snapshots. |
| `endpoint-truth.v1` | Endpoint or UMS readiness snapshots. |

## Current-truth surfaces

| Contract | Purpose |
| --- | --- |
| `truth-export-index.v1` | The single canonical entry point consumers read first. |
| `status-manifest.v1` | Canonical current-status surface for the MQ stack. |
| `inbox-manifest.v1` | Exported view of the promotion inbox: observed but not yet promoted. |
| `memory-score-manifest.v1` | Complete score records keyed by `memory_id`. |
| `memory-evidence-manifest.v1` | Sanitized evidence records keyed by exact evidence ref. |
| `promotion-policy.v1` | Versioned promotion weights and thresholds. |
| `views-manifest.v1` | Vault views consumers resolve to open a file or folder. |
| `repo-memory-index.v1` | Per-repo memory index keyed by repo. |

Materialized manifests live under the consumer's local vault root and are
gitignored; only the schema and a public-safe example are tracked.

## Context contracts

| Contract | Purpose |
| --- | --- |
| `context-pack.v1` | Small task-scoped context bundles for Codex and Claude. |
| `context-card.v1` | Compact per-repo card feeding pack generation. |

## CodeGraph metadata

| Contract | Purpose |
| --- | --- |
| `codegraph-contract-map.v1` | Cross-repo contract map. |
| `codegraph-measurement.v1` | CodeGraph discovery measurement records. |

CodeGraph output is metadata, not truth evidence, and never feeds promotion.

## Rules

- Every stored artifact should have a schema name and timestamp.
- Facts should be separated from interpretation and recommendation.
- Sensitive details must be removed or replaced before export.
- Runtime truth stays in the source repo or tool.
- Root instruction files should stay short.

## Lifecycle

```text
raw signal
  -> memory-observation.v1
  -> memory-score.v1
  -> promotion-event.v1 audit when status changes
  -> promoted memory reused as future context
```

The promotion axis is frozen: `observed -> candidate -> promoted -> deprecated
-> archived`, with the verbs `promote / reject / defer / rollback / deprecate`.
