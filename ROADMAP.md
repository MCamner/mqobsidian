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

- [ ] modify `docs/integrations/codegraph.md`
- [ ] modify `scripts/check-codegraph-stack.sh`
- [ ] create `examples/codegraph/stack-coverage.example.json`

Tasks:

- [ ] record installed version, index freshness, file/node/edge counts, and
  indexed languages per MQ repo
- [ ] distinguish supported source, unsupported source, generated files, and
  intentionally excluded memory/docs
- [ ] report shell and PowerShell coverage as unsupported instead of silently
  treating those repos as fully indexed
- [ ] keep all machine paths and `.codegraph/` databases out of exported output
- [ ] document the upstream feature request boundary for shell/PowerShell

Exit gate:

- [ ] every indexed MQ repo has an explicit, public-safe coverage status
- [ ] a green index status cannot hide unsupported command surfaces

#### B. Cross-repo contract map

**Owner:** `mqobsidian`
**Secondary repos:** `mq-agent`, `repo-signal`, `mq-mcp`, `mq-ums`
**Files:**

- [ ] create `schemas/codegraph-contract-map.v1.json`
- [ ] create `templates/codegraph-contract-map.md`
- [ ] create `examples/codegraph-contract-map.example.json`
- [ ] create `docs/CODEGRAPH_CONTRACT_MAP.md`
- [ ] modify `scripts/validate-export.py`

Tasks:

- [ ] define a small contract record with producer repo, consumer repo, schema,
  entrypoint, implementation symbol, validation command, and evidence timestamp
- [ ] map `repo-review.v1`, `context-pack.v1`, `endpoint-truth.v1`, and
  `feedback-signal.v1` first
- [ ] use CodeGraph only for repo-local symbol evidence; join repos through the
  declared contract record
- [ ] require source schema provenance and reject absolute private paths
- [ ] validate examples without requiring a local CodeGraph installation in CI

Exit gate:

- [ ] one queryable record can trace a contract from producer through consumer to
  its verification command without pretending there is a federated code graph

#### C. Focused task-pack queries

**Owner:** `mqobsidian` for the contract; `mq-agent` for execution
**Files:**

- [ ] modify `scripts/generate-context-pack.py`
- [ ] modify `templates/context-pack.md` only if the existing `notes` field is
  insufficient
- [ ] modify `mq-agent/mq_agent/tools/context_pack.py`
- [ ] add focused tests in both owner repos

Tasks:

- [ ] generate concrete queries from named symbols, files, and contract records
  instead of only saying “use CodeGraph”
- [ ] keep `--codegraph auto|on|off` and preserve non-source suppression
- [ ] cap query count and context size so CodeGraph cannot become a token sink
- [ ] pass an explicit repo/project path for every query
- [ ] fall back cleanly to targeted source reads when an index is missing,
  unsupported, locked, or stale
- [ ] never let CodeGraph replace source tests or CLI verification

Exit gate:

- [ ] a source-heavy task pack contains bounded, copy-pasteable queries
- [ ] a documentation-only task pack contains no CodeGraph noise

#### D. Measurement and verification loop

**Owner:** `mq-agent` for execution; `mqobsidian` for durable measurement format
**Files:**

- [ ] create `schemas/codegraph-measurement.v1.json`
- [ ] create `templates/codegraph-measurement.md`
- [ ] create `examples/codegraph-measurement.example.json`
- [ ] modify `docs/context-effect.md`
- [ ] add an `mq-agent` measurement command only after the record contract is stable

Tasks:

- [ ] record task, repos, queries, returned symbols, source reads, selected
  tests, executed tests, result, and fallback reason
- [ ] separate measured facts from inferred token savings
- [ ] compare CodeGraph-assisted discovery with a defined broad-read baseline
- [ ] measure at least one Python task, one cross-repo contract task, and one
  unsupported shell task with explicit fallback
- [ ] feed only verified reusable conclusions into the existing observation →
  scoring → curated-learn pipeline

Exit gate:

- [ ] three reproducible MQ measurements exist with commands and verification output
- [ ] no measurement claims correctness unless the relevant source tests pass

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

- [ ] MQ has an honest coverage view, including unsupported shell/PowerShell surfaces
- [ ] cross-repo contracts are traceable without a fake federated graph
- [ ] task packs emit bounded, concrete queries with deterministic fallback
- [ ] measurements connect discovery to actual test evidence
- [ ] mqobsidian remains durable memory and contract owner, not a source-code engine

## Related

- `mq-agent` orchestration milestone: `v1.22.0 — Inbox ranking and promotion
  orchestration` (consumes the exports defined here).
- `macos-scripts` runtime governance: `Phase 12 / v2.0.0 — Runtime Authority
  And Shell Governance` (delegates to the surfaces defined here).
- `docs/integrations/codegraph.md` — current local CodeGraph operating guide.
- `docs/roadmap-token-reduction.md` — Phase 4.5 baseline and recorded source
  discovery measurements.
