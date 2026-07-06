---
schema: decision-record.v1
decision_id: DEC-002
created_at: 2026-07-06T00:00:00Z
title: mqobsidian owns current truth surfaces as canonical exported manifests
status: accepted
---

# Decision

## Context

Roadmap Delivery A ("Canonical schema") has moved past codifying contracts that
already exist. The `views manifest` (`views-manifest.v1`, PR #29) simply
formalized a shape `mqlaunch` already consumed — zero design. The remaining
Delivery-A gaps are different: **status manifest**, **inbox manifest**, and
**archival/deprecation lifecycle fields**. These are first-order model
decisions, not missing files.

The load-bearing fork is: does `mqobsidian` own **current truth surfaces**
(canonical, materialized, directly consumable), or only **historical
evidence** (records/events), leaving `status` and `inbox` as state derived by
consumers?

- Derived-only pushes state-reconstruction logic into `mq-agent` and makes
  `mqlaunch` unable to answer "what is true right now?" from a file. "What is
  the truth?" becomes a computation, not a read.
- Manifest-only risks duplicated/stale truth if exports drift from evidence.

## Decision

`mqobsidian` **owns current truth surfaces**, exported as canonical manifests
that are the consumer-facing contract. The clean split:

- **records / events** = source evidence and history
  (`learn-record.v1`, `repo-review.v1`, `decision-record.v1`,
  `promotion-event.v1`, `memory-observation.v1`, …).
- **manifests / views** = current canonical exported truth
  (`views-manifest.v1`, and — to be added — `status-manifest.v1`,
  `inbox-manifest.v1`).

Consumers (`mqlaunch` read-only, `mq-agent` delegate/orchestrate) read the
manifests. They never reconstruct current truth from raw evidence themselves.

### Lifecycle is reuse, not new vocabulary

The lifecycle axis is **already canonical** and MUST be reused, not
reinvented. Two dimensions coexist (per `memory-score.v1` /
`promotion-event.v1`):

- **Promotion axis:** `observed → candidate → promoted → deprecated → archived`
- **Freshness axis:** `experimental → active → stale → deprecated`

`inbox-manifest.v1` items therefore live on the pre-promotion end of the
promotion axis (`observed` / `candidate`); "review-needed vs auto-promotable"
is an **orchestration** concern owned by `mq-agent` (Delivery B), not a manifest
state. Archival/deprecation "lifecycle fields" are these existing states
expressed on durable records, optionally backed by a `promotion-event.v1`
trail for traceability — no new enum.

## Consequences

- **Positive:** `mqlaunch` stays a thin reader; `mq-agent` validates against
  stable contracts instead of inventing truth; SSOT ownership is explicit; every
  current-truth surface is a diffable file.
- **Cost:** `mqobsidian` is now responsible for keeping exports current and
  non-duplicative of the evidence they summarize. Freshness/drift markers
  (Delivery D) become load-bearing, not optional.
- **Follow-up (Delivery A remainder):** add `status-manifest.v1` and
  `inbox-manifest.v1` aligned to the axes above; represent lifecycle as fields
  on durable records. Shapes to be ratified before merge.

## Notes — public/private boundary and naming (flagged, not resolved here)

- **This record is public governance**, so it lives in the tracked `docs/`
  tree. The raw vault `decisions/` folder (like `inbox/` and `memory/*`) is
  `.gitignore`d — private, unsanitized truth that never enters the public-safe
  repo. The consumer views manifest points `decisions` at that private folder;
  consumers resolve it against the local vault, not this repo. Public,
  sanitized decisions belong here under `docs/decision-records/` (the folder
  name `decisions/` is itself `.gitignore`d, so the public home cannot reuse
  it).
- **Naming drift:** schema descriptions cite `ADR-007` / `ADR-008`, but the
  decision-record convention is `DEC-NNN` (`templates/decision.md`,
  `examples/sanitized-decision.md`). Recommend consolidating on one prefix and
  backfilling the referenced decisions as a separate hygiene task.
