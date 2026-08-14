# Changelog

Condensed from the repository `CHANGELOG.md`, which stays authoritative.

## v0.3.0 - 2026-08-05

- Declared explicit ownership for all 23 truth and memory contracts in
  `.mq/repo-contract.json`.
- Added `release-check.sh`, a read-only releasability entrypoint conforming to
  `repo_release_check.v1`, so `mq-agent` can read this repo's release verdict.
- Added atomic promotion transitions with a write-ahead journal: five locked
  verbs, hash-verified snapshots, deterministic recovery, and append-only
  compensation, exposed as bounded local-only commands with preview by default.
- Extended `promotion-event.v1` additively with `source_evidence_refs`,
  `journal_id`, `verb`, and `compensates`, and wired it into export validation —
  it was never validated before.
- Added structured context-pack exclusion proof with kind, item, and reason.
- Added a file-locked, append-only writer for schema-valid model-routing
  outcomes, including negative escalation evidence without raw model output.
- Adopted strict schema enforcement (DEC-003) and an evidence producer contract
  before a generalized adapter (DEC-004).
- Fixed: the export builder read a dead score snapshot instead of live engine
  output, so the published bundle carried stale truth while validating cleanly.
- Fixed: published score records violated `memory-score.v1` by carrying internal
  engine state the schema does not declare.

## v0.2.2 - 2026-07-16

- Added the first repo-local `.mq/context/` export generated through
  `mq-agent context export`.
- Published `.mq/context-budgets.json` as the cross-repo context-export budget
  contract, with mqobsidian as owner and mq-agent as designated consumer.
- Added a CI drift guard that regenerates `.mq/context` exports and fails when
  the committed `examples/repo-context-exports` are stale.
- Made `.mq/context` line budgets a single source of truth, read by both the
  export generator and the token-budget checker instead of three hardcoded
  copies.

## 2026-06-18

- Initialized the `mqobsidian` GitHub Wiki.
- Added compact MQ wiki freshness status.
- Added standard MQ wiki navigation pages.

## v0.2.1 - 2026-06-17

- Seeded mqobsidian, mq-agent, and mq-mcp context cards for the token
  reduction layer.
- Added tracked mqobsidian system hot/index surfaces for agent read-order
  grounding.
- Added VERSION and CHANGELOG release metadata.
