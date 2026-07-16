# Truth surfaces — consumer read contract

This is the single list of `mqobsidian`'s canonical exported truth surfaces: what
each one is, the versioned schema it conforms to, and which consumer reads it.
`mqobsidian` is the single owner of current truth; consumers read these surfaces
and never reconstruct current truth from raw evidence.

The **decision** behind this is
`docs/decision-records/DEC-002-truth-surfaces-ownership.md`; this file is the
operational read contract that flows from it. It does not restate the rationale.

## Read order

1. Read `truth-export-index.v1` **first**. It enumerates every exported surface,
   states the schema+version each conforms to, where the materialized surface
   lives, and its freshness/drift.
2. Resolve to the specific manifest by its stable `key`, then read it.
3. Never hardcode a surface path or assume a schema major — discover and
   version-check through the index.

## Current-truth surfaces (manifests)

These answer "what is true right now?" as a read, not a computation.

| Surface | Schema (versioned) | Read by | Freshness / drift |
| --- | --- | --- | --- |
| Export index | `truth-export-index.v1` | all consumers (entry point) | per-surface `generated_at` + `drift` |
| Repo status | `status-manifest.v1` | `mqlaunch` (read-only), `mq-agent` (orchestration) | `freshness_state` + `drift` + `last_verified_at` |
| Promotion inbox | `inbox-manifest.v1` | `mq-agent` (ranking/promotion), moderator review | `generated_at`; items on the pre-promotion axis |
| Promotion scores | `memory-score-manifest.v1` | `mq-agent` (ranking) | `generated_at`; complete records keyed by `memory_id` |
| Promotion evidence | `memory-evidence-manifest.v1` | `mq-agent`, moderator review | `generated_at`; sanitized records keyed by exact evidence ref |
| Promotion policy | `promotion-policy.v1` | `mq-agent` (ranking/freshness) | `generated_at`; versioned weights and thresholds |
| Vault views | `views-manifest.v1` | `mqlaunch` (resolves view keys → vault paths) | resolved against the local vault root |

Materialized manifests live under the consumer's local vault root (e.g.
`MQ_OBSIDIAN_DIR`) and are gitignored; only the schema and a public-safe example
(`examples/*-manifest.example.json`) are tracked (ADR-006). Every path in a
surface is vault-relative — never absolute or machine-specific.

The sole well-known runtime entrypoint is
`$MQ_OBSIDIAN_DIR/exports/truth-export-index.json`. Inbox evidence is
authoritative only when its exact `ref` resolves in the
evidence manifest. Consumers must not fall back to private observation files.

## Records vs manifests

Per DEC-002, two layers are kept distinct:

- **records / events** = source evidence and history (`learn-record.v1`,
  `repo-review.v1`, `decision-record.v1`, `promotion-event.v1`,
  `memory-observation.v1`, `memory-score.v1`, …). Consumers do **not** rebuild
  current truth from these.
- **manifests / views** = the current-truth surfaces above.

Ownership of the memory/promotion record contracts (producers and consumers per
contract) is the table in
`decisions/ADR-008-evidence-based-memory-architecture.md`; it is not duplicated
here.

## No competing truth plane

- `mqobsidian` owns the truth surfaces. Shell and agent layers **read or
  delegate, never own** (DEC-002; mirrors ADR-005 P6 local-only rule).
- `mqlaunch` is a thin read-only consumer: it resolves views and reads status,
  and must not reconstruct status or inbox state itself.
- `mq-agent` orchestrates against these stable contracts (ranking, promotion
  routing) but does not invent a parallel current-truth store.
- CodeGraph output is not truth evidence and never feeds promotion (ADR-009).

## Related

- `docs/decision-records/DEC-002-truth-surfaces-ownership.md` — the owning decision.
- `decisions/ADR-006-mq-context-export-tracked-vs-local.md` — tracked schema/example vs local materialized output.
- `decisions/ADR-008-evidence-based-memory-architecture.md` — frozen memory/promotion model + record ownership table.
- `decisions/ADR-009-codegraph-memory-boundary.md` — graph data ≠ observation evidence.
