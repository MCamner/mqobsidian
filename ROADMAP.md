# Roadmap

`mqobsidian` is the single source of truth and durable memory for the MQ stack.
Its job is to own the canonical structure of truth, inbox, promotion, and
memory — and to export stable surfaces that other repos read, rather than each
tool inventing its own partial state.

## Ownership boundary

The stack has one clean responsibility split. `mqobsidian` holds the truth;
other repos read or delegate to it.

- `mqobsidian` — canonical truth schema, inbox/promotion state, durable memory
  model, exported views/manifests, freshness markers.
- `mq-agent` — orchestration: inbox analysis, ranking, review-gated promotion,
  and contract enforcement against mqobsidian exports. Runs the workflow; does
  not own the schema.
- `macos-scripts` / `mqlaunch` — terminal runtime, menus, and UI. A thin
  read-only or delegate-only surface; never a truth owner.

`mqobsidian` does **not** own: terminal UX, shell runtime authority,
orchestration logic, review execution, or menu routing.

## Single Source Of Truth And Promotion Governance

**Status:** Proposed
**Priority:** P1
**Type:** Memory / Truth model / Governance
**Goal:** Make `mqobsidian` the canonical owner of truth structure, inbox
state, promotion state, and durable memory views across the stack.

### Why this matters

Without one canonical truth layer, every tool starts inventing its own partial
memory, ranking, and status model. That produces drift, duplicate state, weak
trust, and manual moderation bottlenecks.

### This repo owns

- canonical truth schema
- inbox structure and promotion queue structure
- durable memory categories and persistence rules
- canonical status/views/manifests consumed by other repos
- freshness/state markers for truth surfaces
- promotion state and memory lifecycle states
- single-source-of-truth rules across the stack

### This repo does not own

- terminal UX
- shell runtime authority
- orchestration logic
- review execution engine
- agent delegation UX
- menu routing

### Target state

- one canonical schema for status, inbox, views, decisions, learn, and reviews
- one canonical promotion queue
- one canonical durable memory model
- one canonical export surface for consumers
- no competing truth plane in shell or agent layers

### Scope

- [ ] define canonical note/schema structure
- [ ] define inbox item model
- [ ] define scoring fields and promotion-state fields
- [ ] define durable memory categories and thresholds
- [ ] define canonical views/manifests for consumers
- [ ] define freshness/version markers for exported truth surfaces
- [ ] define moderator checkpoints where automation stops

### Delivery

#### A. Canonical schema

- [ ] define status manifest
- [ ] define inbox manifest
- [ ] define views manifest
- [ ] define learn/review/decision schemas
- [ ] define promotion-state fields
- [ ] define archival/deprecation lifecycle fields

#### B. Inbox and ranking model

- [ ] define what enters the inbox
- [ ] define recurrence/evidence fields
- [ ] define ranking inputs
- [ ] define review-needed vs auto-promotable states
- [ ] define thresholds and exception paths

#### C. Durable memory governance

- [ ] define what qualifies as durable memory
- [ ] define what remains transient or session-local
- [ ] define promotion approvals and guardrails
- [ ] define the rollback/deprecation path for bad memory
- [ ] define traceability from source evidence to durable note

#### D. Consumer contracts

- [ ] define canonical read surfaces for `mqlaunch`
- [ ] define canonical delegation/contract surfaces for `mq-agent`
- [ ] version exported truth surfaces
- [ ] expose freshness and drift markers

### Exit criteria

- [ ] `mqobsidian` is the undisputed truth owner
- [ ] inbox, ranking, promotion, and durable memory have one canonical model
- [ ] consumers read from exported truth surfaces instead of inventing local truth
- [ ] every promoted durable memory item can be traced back to source evidence

## CodeGraph MQ Integration

**Status:** Proposed
**Priority:** P1
**Type:** Source intelligence / Cross-repo contracts / Measurement
**Goal:** Turn CodeGraph's per-repo source graph into a measured MQ workflow
without making `mqobsidian` a code index or reimplementing CodeGraph.

> **Prior art / governance (verified 2026-07-14).** This block extends, not
> replaces, the shipped `docs/roadmap-token-reduction.md` Phase 4.5 foundation:
> `docs/integrations/codegraph.md`, `scripts/check-codegraph-stack.sh`, stack-wide
> indexing, and recorded discovery measurements already exist. The memory boundary
> is fixed by `decisions/ADR-009-codegraph-memory-boundary.md` (accepted
> 2026-06-27): CodeGraph Core (Project A) may build now; the CodeGraph→memory
> producer (Project B) is **parked and data-gated**. Nothing in this block may
> treat graph data as observation/promotion evidence.

### Problem

CodeGraph already provides symbol search, source-aware exploration,
callers/callees, impact analysis, and affected-test discovery. The remaining MQ
gap is integration:

- each MQ repo has an independent graph; cross-repo contracts are joined by hand
- task packs recommend CodeGraph generically instead of emitting focused queries
- schema producer/consumer/test relationships are not represented explicitly
- CodeGraph use and verification outcomes are not measured consistently
- Bash, Zsh, Fish, and PowerShell are not supported upstream, leaving important
  MQ command surfaces outside structural analysis
- Markdown and Obsidian wikilinks are not CodeGraph source relationships and
  must remain owned by the vault memory model

### Architecture boundary

- **CodeGraph upstream** owns language parsers, symbol extraction, graph edges,
  impact analysis, and affected-test discovery.
- **mqobsidian** owns durable contract metadata, query recipes, context-pack
  hints, measurement records, and public-safe examples.
- **mq-agent** owns orchestration: selecting repos, executing bounded CodeGraph
  queries, running tests, and recording verified outcomes.
- **repo-signal** may report index readiness and coverage signals; it does not
  become a second graph engine.
- **Source repos** own their `.codegraph/` indexes and runtime/test truth.

### Non-goals

- do not store `.codegraph/codegraph.db` in mqobsidian or Git
- do not build a second symbol index, parser, or call-graph engine
- do not infer runtime correctness from static graph edges
- do not auto-promote CodeGraph output into durable memory
- do not claim cross-repo calls unless a declared contract connects them
- do not implement shell or PowerShell parsing inside mqobsidian

### Delivery

#### A. Capability and coverage baseline

**Owner:** `mqobsidian`
**Files:**

- [x] modify `docs/integrations/codegraph.md` (added "Coverage and unsupported
  surfaces" section + upstream boundary)
- [x] modify `scripts/check-codegraph-stack.sh` (added `--coverage` public-safe
  JSON mode; default human report unchanged)
- [x] create `examples/codegraph/stack-coverage.example.json`

Tasks:

- [x] record installed version, index freshness, file/node/edge counts, and
  indexed languages per MQ repo
- [~] distinguish supported source, unsupported source, generated files, and
  intentionally excluded memory/docs — supported vs unsupported source is
  reported; generated-file / excluded-memory-doc classification is deferred (not
  needed for the exit gate, add when a real case requires it)
- [x] report shell and PowerShell coverage as unsupported instead of silently
  treating those repos as fully indexed
- [x] keep all machine paths and `.codegraph/` databases out of exported output
- [x] document the upstream feature request boundary for shell/PowerShell

Exit gate:

- [x] every indexed MQ repo has an explicit, public-safe coverage status
- [x] a green index status cannot hide unsupported command surfaces (verified:
  all 8 repos report `partial`; `macos-scripts` surfaces 219 unindexed shell files)

#### B. Cross-repo contract map

**Owner:** `mqobsidian`
**Secondary repos:** `mq-agent`, `repo-signal`, `mq-mcp`, `mq-ums`
**Files:**

- [x] create `schemas/codegraph-contract-map.v1.json`
- [x] create `templates/codegraph-contract-map.md`
- [x] create `examples/codegraph-contract-map.example.json`
- [x] create `docs/CODEGRAPH_CONTRACT_MAP.md`
- [x] modify `scripts/validate-export.py`

Tasks:

- [x] define a small contract record with producer repo, consumer repo, schema,
  entrypoint, implementation symbol, validation command, and evidence timestamp
- [x] map `repo-review.v1`, `context-pack.v1`, `endpoint-truth.v1`, and
  `feedback-signal.v1` first (context-pack + repo-review verified against real
  symbols; endpoint-truth `planned` (no mq-ums producer yet); feedback-signal
  `unverified` (mq-agent emitter not wired) — recorded honestly)
- [x] use CodeGraph only for repo-local symbol evidence; join repos through the
  declared contract record
- [x] require source schema provenance and reject absolute private paths
  (`schema_source` required; validator rejects absolute/private paths — negative-
  tested)
- [x] validate examples without requiring a local CodeGraph installation in CI
  (`validate-export.py` is pure JSON validation)

Exit gate:

- [x] one queryable record can trace a contract from producer through consumer to
  its verification command without pretending there is a federated code graph

#### C. Focused task-pack queries

**Owner:** `mqobsidian` for the contract; `mq-agent` for execution
**Files:**

- [x] modify `scripts/generate-context-pack.py` (concrete `## CodeGraph queries`
  section; `--symbol` flag)
- [x] modify `templates/context-pack.md` (added the optional queries section —
  a bullet `notes` list is insufficient for copy-pasteable command blocks)
- [x] modify `mq-agent/mq_agent/tools/context_pack.py` (mirrors the generator;
  `--symbol` wired through the CLI)
- [x] add focused tests in both owner repos (mqobsidian `tests/test_context_pack_queries.py`
  wired into CI; mq-agent `tests/test_context_pack_cmd.py` — full suite 846 passed)

Tasks:

- [x] generate concrete queries from named symbols, files, and contract records
  instead of only saying “use CodeGraph” (symbols via `--symbol`; source files
  from `relevant_files`; contract-map symbols feed in via `--symbol`)
- [x] keep `--codegraph auto|on|off` and preserve non-source suppression
- [x] cap query count and context size so CodeGraph cannot become a token sink
  (`MAX_CODEGRAPH_QUERIES = 5`; a real source pack is 57 lines vs the 200 budget)
- [x] pass an explicit repo/project path for every query (`-p <repo>` on each)
- [x] fall back cleanly to targeted source reads when an index is missing,
  unsupported, locked, or stale (stated in the section guidance)
- [x] never let CodeGraph replace source tests or CLI verification (stated in the
  section guidance)

Exit gate:

- [x] a source-heavy task pack contains bounded, copy-pasteable queries
- [x] a documentation-only task pack contains no CodeGraph noise (verified: doc
  task emits no `## CodeGraph queries` section; test-covered both ends)

#### D. Measurement and verification loop

**Owner:** `mq-agent` for execution; `mqobsidian` for durable measurement format
**Files:**

- [x] create `schemas/codegraph-measurement.v1.json`
- [x] create `templates/codegraph-measurement.md`
- [x] create `examples/codegraph-measurement.example.json`
- [x] modify `docs/context-effect.md`
- [ ] add an `mq-agent` measurement command only after the record contract is
  stable (deferred by design — the record contract just landed; wire the command
  once it has settled in use)

Tasks:

- [x] record task, repos, queries, returned symbols, source reads, selected
  tests, executed tests, result, and fallback reason
- [x] separate measured facts from inferred token savings (`measured` vs
  `inferred` blocks in the schema)
- [x] compare CodeGraph-assisted discovery with a defined broad-read baseline
- [x] measure at least one Python task, one cross-repo contract task, and one
  unsupported shell task with explicit fallback (all three in the example, run for
  real)
- [x] keep measurement records as durable *measurement* format only; per
  ADR-009 (Principle 12, graph data ≠ observation evidence) CodeGraph output does
  **not** feed the observation → scoring → curated-learn pipeline until Project B
  is unblocked by the real-data Slice 2 readiness gate

Exit gate:

- [x] three reproducible MQ measurements exist with commands and verification
  output (render_pack 66/321 → tests pass; export_repo_review 35/103 → tests
  pass; shell `log` → CodeGraph miss + grep fallback)
- [x] no measurement claims correctness unless the relevant source tests pass
  (enforced by `validate-export.py`; negative-tested)

### Test gates

Run in `mqobsidian`:

```bash
python3 scripts/validate-export.py
python3 scripts/check-sensitive-content.py
python3 scripts/check-token-budget.py
bash scripts/check-codegraph-stack.sh
git diff --check
```

Run focused tests in every secondary repo changed by a delivery. Full repo tests
remain required before merge when CLI behavior or a public contract changes.

### Approval and rollout gates

- contract/schema changes require review before consumer implementation
- writes to sibling repos require explicit task scope
- commit, push, and merge remain separate approval gates
- no CodeGraph database, machine path, raw query dump, or unverified conclusion
  crosses the public boundary

### Rollback

- revert each delivery independently; no delivery may require deleting an index
- keep existing generic `notes` guidance as the fallback if focused-query
  generation is reverted
- consumers must ignore unknown contract/measurement schema versions

### Overall exit criteria

- [x] MQ has an honest coverage view, including unsupported shell/PowerShell surfaces (Delivery A)
- [x] cross-repo contracts are traceable without a fake federated graph (Delivery B)
- [x] task packs emit bounded, concrete queries with deterministic fallback (Delivery C)
- [x] measurements connect discovery to actual test evidence (Delivery D)
- [x] mqobsidian remains durable memory and contract owner, not a source-code engine

*CodeGraph MQ Integration block complete (A–D) on 2026-07-14; the only deferred
item is the gated `mq-agent` measurement command (Delivery D).*

## Related

- `mq-agent` orchestration milestone: `v1.22.0 — Inbox ranking and promotion
  orchestration` (consumes the exports defined here).
- `macos-scripts` runtime governance: `Phase 12 / v2.0.0 — Runtime Authority
  And Shell Governance` (delegates to the surfaces defined here).
- `docs/integrations/codegraph.md` — current local CodeGraph operating guide.
- `docs/roadmap-token-reduction.md` — Phase 4.5 baseline and recorded source
  discovery measurements.
- `decisions/ADR-009-codegraph-memory-boundary.md` — CodeGraph Core vs. parked,
  data-gated memory producer; graph data ≠ observation evidence.

---

*Roadmap aligned with verified reality on 2026-07-14: both blocks confirmed
`Proposed` (no delivery files exist yet); CodeGraph block reconciled with the
shipped Phase 4.5 foundation and ADR-009's memory boundary.*
