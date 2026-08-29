# Changelog

## [Unreleased]

### Added

- `schemas/mq.model-route-outcome.v1.json` — the routing-outcome contract is now
  canonical here rather than resolved from a sibling mq-agent checkout. Its
  example is validated by `validate-export.py` like every other contract.

### Changed

- `mq.execution-outcome.v1` reconciled with the copy mq-agent ships: the newer
  top-level description and the `model` field's documentation (primary execution
  model, not the verifier's). Contract identity stays this repo's convention —
  `title: mq.execution-outcome.v1`, no `$id`. mq-agent vendors both contracts and
  gates its copies against these (mq-agent #216).
- `record-routing-outcome.py` validates against the canonical schema in this repo.
  Resolution no longer walks to `MQ_AGENT_DIR`, so validation no longer depends on
  a machine-local path or on whichever revision that checkout was on.
  `MQ_AGENT_ROUTE_OUTCOME_SCHEMA` and `--schema` still override.

### Fixed

- `tests/test_record_routing_outcome.py` validated against a hand-written inline
  copy of the routing schema — a third source of truth that had silently drifted,
  missing both `run_id` and `verification.grounding`. The tests now exercise the
  canonical contract, so a schema change reaches them.

## [0.3.0] - 2026-08-28

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

- Experimental `notebook-pack.v1` contract, canonical source template,
  sanitized manifest example, validation coverage, and a deny-by-default
  NotebookLM bridge policy. mq-agent remains the generator and routing owner;
  generated packs and provider state stay local-only.
- `.mq/notebooks.json` consumer profile declaring one narrow, public-safe
  `mq-stack` selection. Materialized output is isolated under ignored
  `.notebooklm/`; mqobsidian still contains no provider exporter or adapter.
- Five-question `MQ Stack Intelligence` evaluation with explicit local
  baselines, provenance/abstention scoring, and separate reviewed mqobsidian
  versus deferred, revision-bound CodeGraph source lanes.
- `notebook-pack.v1` revisions now require a `dirty` flag, so a manifest can no
  longer imply that a source is commit-bound when its SHA-256 describes
  uncommitted working-tree content.
- NotebookLM one-notebook proof executed against all three baselines: 34/40
  against 36 (compact MQ) and 37 (MQ + CodeGraph). The decision gate fails, so
  the provider stays optional and roadmap 12f is debt that should not be paid.
  A fair retest on undistilled material is specified as 12g.
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
- `mq.execution-outcome.v1` — the execution observation contract, a public-safe
  example, export validation, and a contract test. One record per agent run;
  routing is a field on the record rather than its subject, so route, skill and
  tool evaluation read one contract instead of growing separate telemetry
  formats. A counter the runtime does not measure is absent, not zero.
- `context-budget.v1` — the schema the artifact already declared but that never
  existed. `.mq/context-budgets.json` is now validated against it and declared
  among the repo's contracts (25 -> 26), with semantic invariants a schema
  cannot express: a rendered or consumed file without a budget is rejected
  instead of failing later as a `KeyError`.
- `.mq/context-selection-vocabulary.json` — the context-selection heuristic
  published as a declarative contract, with DEC-005 recording the boundary:
  mqobsidian publishes the vocabulary, mq-agent keeps every runtime selection
  decision. Replaces a duplicated selection vocabulary maintained in two repos.
- A contract test requiring every `.mq` artifact to be schema-backed and
  declared, so an artifact can no longer ship validated-by-nothing.
- A verified learn note recording repo-signal's uv tool installation.

### Changed

- `docs/wiki/` retired as a content surface. Contract truth moved into `docs/`
  and the freshness gate now targets it, so the consumed page is the gated one.
- CodeGraph guidance states intentions rather than tool names, and the docs no
  longer claim mq-agent generates surfaces it does not.
- Phase 12 closed. The 12g NotebookLM run scored 17/40 against a gate of 38 on
  21x the material; 12d and 12e are closed with it. NotebookLM stays optional.
- The roadmap now records execution-intelligence delivery against what mq-agent
  actually ships, with `systems/mqobsidian/{hot,index}.md` and the generated
  agent view rebuilt to match.
- The linted surface is the repo's decision rather than the editor's, and local
  validation is reproducible against the CI-pinned toolchain.

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
- `--clean` in `scripts/generate-repo-context-export.py` called
  `shutil.rmtree` on the whole context directory. Aimed at a live repo with
  `--output-dir`, it would have deleted `task-pack.md` and any unknown file —
  the opposite of what the vault documents. It now unlinks only the names it
  owns, covered by a test that fails against the old behaviour.
- `roadmap/ROADMAP_NOTES.md` was tracked despite declaring itself local-only
  and being covered by `.gitignore`. Untracked without deleting the local file.
- The routing evidence seam: validated outcomes accumulated in
  `~/.mq-agent/route-outcomes.jsonl` but never reached `routing/outcomes.jsonl`,
  so the evidence surface read empty while the data existed.

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
