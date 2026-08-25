# Changelog

## [Unreleased]

### Added

- Experimental `notebook-pack.v1` contract, canonical source template,
  sanitized manifest example, validation coverage, and a deny-by-default
  NotebookLM bridge policy. mq-agent remains the generator and routing owner;
  generated packs and provider state stay local-only.
- `scripts/eval-retrieval.py` — selection-quality measurement. Everything the
  repo measured until now answered "how little context did we send?"; nothing
  answered "did we send the right context?". It scores `feedback-signal.v1`
  records as a gold label set (`useful` = true positive, `noise` = false
  positive, `missing` = false negative) and reports precision, recall, F1, pack
  sufficiency, and per-block `keep`/`downgrade`/`widen-or-create`/`refresh`
  verdicts. No new contract: the existing feedback vocabulary is the label set.
  `stale` is kept out of precision and recall — it is a freshness verdict on a
  correctly selected block, and the two axes stay separate. Rank metrics
  (Recall@K, MRR) are deliberately not reported: the contract records judgments
  as an unordered set, so any rank number would measure list order.
- `memory-query.v1` extended additively with optional `repositories`, so one
  query can span the stack (routing evidence lives in mq-agent decisions,
  mq-mcp contracts, and mq-hal feedback at once). `repository` still names the
  asking repo; concern-scoped questions still use `tags`.
- `memory-query.v1` and its example are now covered by `validate-export.py`,
  which never validated them before.

## [0.3.0] - 2026-08-05

### Added

- Explicit ownership metadata for all 23 truth and memory contracts in
  `.mq/repo-contract.json`.
- Structured context-pack exclusion proof with kind, item, and reason.
- A file-locked, append-only writer for schema-valid model-routing outcomes,
  including negative escalation evidence without raw model output.
- Shared Codex and Claude guidance for consuming model-routing contracts.
- `release-check.sh` — canonical read-only releasability entrypoint conforming
  to `repo_release_check.v1`. `--json` emits the machine-readable verdict
  (`schema`, `repo`, `status`, `blockers`, `warnings`, `evidence`) and exits 0;
  human mode prints per-check PASS/FAIL. Runs the Public Safe Check assertions
  (sensitive-content, export scaffolding, token budget, agent entrypoints, unit
  tests) minus the mutating context-export regeneration. Lets mq-agent's
  `stack release --all --preflight` read mqobsidian's release verdict.
- Atomic promotion transitions with a write-ahead journal: five locked verbs
  (promote/reject/defer/rollback/deprecate), fsynced intent journal with
  hash-verified snapshots, deterministic recovery, and append-only compensation.
  Exposed as bounded commands in the local-only memory CLI; preview by default.
- `promotion-event.v1` extended additively with `source_evidence_refs`,
  `journal_id`, `verb`, and `compensates`, and wired into `validate-export.py` —
  it was never validated before.
- `jsonschema` dependency for real schema enforcement (DEC-003), installed in CI.
- DEC-003 (strict schema enforcement) and DEC-004 (evidence producer contract
  before a generalized adapter) decision records.

### Fixed

- The export builder read `memory/scores`, a dead 2026-06-29 snapshot on an
  obsolete scoring scale, instead of the live engine output. The published
  bundle carried stale truth and omitted two memories while validating cleanly.
- Published score records violated `memory-score.v1` by carrying `ebms_state`,
  internal engine state undeclared in the schema. Records are now projected onto
  the fields the schema declares, read from the schema itself.
- `validate-export.py` recursed only through `properties`, so records declared
  under `additionalProperties: {<subschema>}` — every keyed manifest's payload —
  were never inspected at all. A score record of pure garbage produced zero
  errors. Replaced with a real JSON-Schema engine.
- The existing jsonschema-based test skipped itself whenever the library was
  absent, which was always, in CI.

## [0.2.2] - 2026-07-16

### Added

- Release metadata refreshed for the current mqobsidian branch work.
- Added the first repo-local `.mq/context/` export generated through `mq-agent context export`.
- Published `.mq/context-budgets.json` as the cross-repo context-export budget contract, with `docs/context-export-contract.md` declaring mqobsidian as owner and mq-agent as the designated consumer.
- Added a CI drift guard that regenerates `.mq/context` exports and fails when the committed `examples/repo-context-exports` are stale.

### Changed

- Updated version metadata to reflect the latest mqobsidian release state.
- Updated the Phase 4 roadmap with the verified nine-repo local rollout and safe managed-file cleanup contract.
- Made `.mq/context` line budgets a single source of truth (`scripts/context_budgets.py`), read by both the export generator and the token-budget checker instead of three hardcoded copies.

### Fixed

## [0.2.1] - 2026-06-17

### Added

- Seeded mqobsidian, mq-agent, and mq-mcp context cards for the token reduction layer.
- Added tracked mqobsidian system hot/index surfaces for agent read-order grounding.
- Added VERSION and CHANGELOG release metadata.

### Changed

- Expanded token budget checks to cover system hot/index notes, context cards, and agent views.
- Expanded export validation to check context-pack frontmatter and required context-card sections.
- Documented Phase 2 context-card seed status in the token-reduction roadmap.
