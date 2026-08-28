# Roadmap

**Current version:** 0.3.0
**Current direction:** v0.3.0 release candidate — the truth/memory contract
implementation and local release metadata are complete. Tagging and publishing
remain explicit release actions. The delivered scope
declares the contracts this repo already owns explicitly in
`.mq/repo-contract.json` and makes those surfaces
safe and predictable for consumers to read. The goal is better selection and
clearer contracts, not more memory. The `v0.3.0` plan is stated below; the SSOT
& Promotion Governance and CodeGraph MQ Integration blocks further down are
**completed** and kept as history.

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

### Open divergence: context selection lives on both sides

Surfaced by the CodeGraph baseline during the 12g evaluation and verified
directly in source afterwards. Tracked here rather than in Phase 12: this is an
ownership question, and it outlived the phase that found it.

The reviewed rule is that `mq-agent` owns context selection, pack generation and
export (`systems/mqobsidian/hot.md:29`), and that this repo "kor inte workflows"
(`systems/mqobsidian/index.md:17`). Three things in the code do not match that
as written:

1. **Selection logic runs here.** `scripts/generate-context-pack.py` classifies
   a task against `CODEGRAPH_TASK_HINTS`/`CODEGRAPH_TASK_SUPPRESS`
   (`task_is_source_heavy`, :135), builds bounded per-task queries
   (`build_codegraph_queries`, :153, capped by `MAX_CODEGRAPH_QUERIES`, :132)
   and renders the pack (`render_pack`, :276). The same task-pack query logic is
   mirrored in mq-agent's `context_pack.py`, so the two must be edited together.
2. **A second exporter exists here.** `scripts/generate-repo-context-export.py`
   writes to `output_root/<repo>/.mq/context` (`export_repo`, :147). Its default
   `--output-dir` is `examples/repo-context-exports`, so by default it stays
   inside this repo; it reaches a live sibling repo only when `--output-dir` is
   passed explicitly.
3. **The two exporters have different `--clean` semantics, and only the safe one
   is documented.** `hot.md:32` states that `--clean` removes the export's five
   owned files and preserves `task-pack.md` and unknown files. That describes
   mq-agent's exporter, which removes only names in its owned list. This repo's
   script instead calls `shutil.rmtree(context_dir)` on the whole directory.
   Aimed at a live repo with `--output-dir`, it would delete `task-pack.md` and
   any unknown file -- the opposite of what the vault documents.

Finding 3 is fixed; 1 and 2 are a migration that was never finished
(`index.md:68` records that export landed in mq-agent, and ADR-006 makes local
regeneration a working method).

CodeGraph's blast radius flagged these symbols as having no covering tests.
That was accurate for `export_repo` and wrong for `render_pack`, which is
exercised from `tests/test_context_pack_queries.py` and
`tests/test_context_pack_exclusions.py`. Treat that signal as a lead, not a
finding -- the same rule ADR-009 states for CodeGraph output generally.

- [x] Decide whether the reference generators stay here or move to mq-agent.
  Neither: `DEC-005` splits vocabulary from execution. mqobsidian publishes the
  selection heuristic as a declarative contract and keeps the export freshness
  gate, which guards a surface this repo publishes; mq-agent consumes the
  contract and keeps every runtime selection decision. Implementation follows
  the record.
- [x] Align this repo's `--clean` with the owned-files semantics. It now
  unlinks only the names in `EXPORTED_CONTEXT_FILES` instead of calling
  `shutil.rmtree` on the directory, so `task-pack.md` and unknown files in a
  target repo survive. Covered by `tests/test_repo_context_export.py`, which
  fails against the old behaviour.
- [x] Amend `hot.md:29` and `:32` to describe what is actually true, whichever
  way the first two land. Both sentences turned out to be correct and were left
  alone: `:29` is true under DEC-005, and `:32` accurately described mq-agent's
  exporter all along -- this repo's script was the one that disagreed, fixed in
  the `--clean` work. What the implementation did add is a new published
  surface, so `hot.md` gained one line naming
  `.mq/context-selection-vocabulary.json` and the rule that consumers may not
  copy it.

**The ownership track is closed.** Findings 1 and 3 are resolved; finding 2
needed no change. Two adjacent issues were found while working on it and are
tracked below rather than folded in, so this track stays a bounded piece of
work.

### Follow-up: `context-budget.v1` contract integrity

Non-blocking. Found while implementing DEC-005: `.mq/context-budgets.json`
declares `"schema": "context-budget.v1"`, but that schema does not exist, the
artifact is not validated, and the contract is not among the declared 25. The
new vocabulary contract is now held to a higher standard than the older one it
was modelled on. Harden the older one to the new standard rather than treating
the gap as licence to lower it.

- [x] Create the schema the artifact already declares.
- [x] Validate `.mq/context-budgets.json` against it in `validate-export.py`,
  and declare `context_budget.v1` among the repo's contracts (25 -> 26).
- [x] Add semantic invariants, not only structural checks. Every consumer
  indexes the map as `CONTEXT_BUDGETS[name]`, so a rendered or consumed name
  without a budget is a run-time `KeyError` rather than a readable failure;
  `validate-export` now rejects that, which a schema cannot express.
- [x] Test that the declared schema id and the published artifact cannot drift.

Four mutations, each caught by the validator and by
`tests/test_context_budget_contract.py`: `rendered_order` naming a file with no
budget, a consumed file losing its budget, a budget of 0, and the schema id
drifting from the schema file. All four passed silently before.

**Both follow-ups are now closed.** The older contract meets the standard
DEC-005 set for the newer one, and that standard is now enforced rather than
observed.

## Next: Execution Intelligence

Phase 12 is closed. This track collects runtime evidence before any adaptive
routing is considered. NotebookLM remains closed unless a material capability
or use-case change invalidates the earlier evaluation.

### v2.4 — Observation foundation

- [x] `mq.execution-outcome.v1` contract, example and validation
- [x] runtime writer in mq-agent
- [x] optional measured provenance for route/model/context
- [ ] fallback recording remains absent until a runtime measures it
- [x] failure recording, fixtures and mutation tests in mq-agent

### v2.5 — Execution inspection

- [x] `mq-agent route inspect`
- [x] `mq-agent execution report`
- [x] `mq-agent execution compare` with task-class filtering
- [x] latency, context and fallback statistics; unknown values stay absent

### v2.6 — Shadow routing

- [x] shadow decision contract
- [ ] active-versus-shadow divergence reporting
- [x] zero-effect guarantee
- [x] machine-checked evidence threshold before policy experiments

### v2.7 — Evidence-based routing

- [ ] define promotion criteria from accumulated outcomes
- [ ] evaluate a candidate policy in shadow mode
- [ ] require human approval before activation
- [ ] provide rollback or supersede mechanism

The provisional observation threshold is 30 runs across 2 alternative routes
over 14 days per relevant task class. It is a hypothesis to evaluate, not an
activation rule. Until then, reporting is descriptive and routing remains
unchanged.

### What makes something a contract here

A file carrying a `schema` field is not a contract on its own -- that is exactly
what `.mq/context-budgets.json` was for months. A contract must be:

```text
artifact -> schema exists -> contract declared -> documented
```

- a real schema in `schemas/`, matching the id the artifact names;
- declared in `.mq/repo-contract.json` (hyphens in the schema file become
  underscores in the declaration);
- documented in `docs/memory-model.md`;
- validated in `validate-export.py`, with explicit semantic invariants wherever
  JSON Schema cannot reach -- coverage of keys other code will index by, for
  instance.

`tests/test_contract_artifact_invariant.py` enforces the first three links;
`test_docs_freshness` already enforced the last. Before that test, only the last
link was checked, which is why an artifact could name a schema nobody had
written and nothing noticed.

### Follow-up: CodeGraph tool names in the reference generator

Not stale documentation -- a contract/runtime mismatch. `generate-context-pack.py`
emits guidance naming `codegraph_callers`, `codegraph_impact` and
`codegraph_node`. The CodeGraph MCP server exposes a single tool,
`codegraph_explore`, and mq-agent's generator emits that one. Verified at
runtime: a pack built through `mq-agent context pack` against this vault names
the tool that exists, while this repo's reference generator names three that do
not. Packs from the reference generator can therefore steer an agent toward
tools it cannot call.

The finding came from the 12g CodeGraph baseline as a signal, was confirmed
against source, and was then verified against the live MCP surface. Only after
that third step is it strong enough to act on -- the same discipline ADR-009
requires of CodeGraph output.

- [x] Reconcile the emitted tool names against the shipped MCP surface. The
  investigation changed the finding: every intent *does* exist, as a CLI command
  (`explore`, `node`, `query`, `callers`, `callees`, `impact`, `status`). Only
  the MCP transport has consolidated -- CodeGraph 1.5.0 exposes one tool,
  `codegraph_explore`, and the CLI's own help still refers to a
  `codegraph_node` MCP tool. So the MCP surface varies by installed version, and
  hardcoding any tool name here is wrong regardless of which names are current.
- [x] Decide whether the reference generator should name tools at all: it should
  not. It now emits intentions ("Inspect the callers of `x`", "Assess the blast
  radius of changing `x`") and leaves transport to the consumer, which knows
  what it has installed. `docs/integrations/codegraph.md` keeps the intent table
  but adds a CLI column and marks the MCP column as an observation about one
  installation rather than a contract. `tests/test_codegraph_intentions.py`
  fails if any `codegraph_*` tool name reappears in the guidance or the rendered
  section.
- [x] Apply the same treatment to mq-agent's generator (mq-agent #212). It was
  **broken the same way**, not latent -- correcting the claim recorded here
  earlier. The end-to-end check behind that claim passed no `--symbol` and no
  relevant files, so only the first line was emitted; with them the generator
  named `codegraph_callers`, `codegraph_impact` and `codegraph_node` exactly as
  this repo's did. Both now emit the same intentions, so a pack reads the same
  whichever produced it.

The tests were why the defect survived on both sides. Five assertions in
mq-agent and three here pinned the exact tool names in place, which made
correcting them look like a test failure. A test that mirrors the implementation
rather than the requirement protects the bug, not the code -- both sets now
assert the intention.

- [x] Add covering tests for `export_repo`, including an explicit ownership
  invariant: an export run may only create, modify or delete names in
  `EXPORTED_CONTEXT_FILES`. Asserted over the whole directory before and after a
  run, so the entire export surface is protected against a recurrence, not just
  `--clean`, and files added to a target repo later are covered without anyone
  updating the test. A third test pins the written set to the contract list,
  which kills the duplicated truth that caused the defect. All three fail under
  mutation. `render_pack` already had coverage.

## v0.3.0 — Explicit Truth Contracts and Consumer Readiness

**Status:** Release candidate; tag and publication pending
**Priority:** P1
**Type:** Contracts / Consumer readiness
**Goal:** Make the contracts this repo owns explicit and predictable to consume.
Better selection and clearer contracts — **not** more memory categories.

### Landed

- [x] `.mq/repo-contract.json` declares the 23 owned contracts, each backed by a
  `schemas/<name>.v1.json` file (#53).
- [x] Roadmap states current version + direction and marks the shipped blocks
  completed (#52).

### Already satisfied — do not rebuild

This is the important honesty gate: most of the proposed v0.3.0 work already
exists. Re-implementing it would repeat the exact drift this repo exists to
prevent.

- **Consumer read contract** — `docs/TRUTH_SURFACES.md` already enumerates every
  canonical surface, its version, and its consumer (Delivery C / DEC-002).
- **mq-agent consumption model** — `docs/mq-agent-integration.md` already exists.
- **Public-safe guard** — `scripts/check-sensitive-content.py` already blocks
  secrets/private paths in the public surface and runs in CI.
- **Memory lifecycle states** — the canonical promotion axis
  (`observed → candidate → promoted → deprecated → archived`, with the
  `promote/reject/defer/rollback/deprecate` verbs) is already frozen in
  `memory-score.v1`, `promotion-event.v1`, and `learn-record.v1` under
  ADR-008 / DEC-002. v0.3.0 does **not** introduce a second state vocabulary.
- **Freshness/drift** — `status-manifest.v1` and `inbox-manifest.v1` carry
  `freshness_state` + `drift`; `truth-export-index.v1` exposes them per surface.

### Remaining implementation work

None open — the one gap that survived the honesty gate is closed below.

### Release gate

- [x] Bump `VERSION`, README badge, changelog, and release metadata together.
- [x] Run the complete public-safe validation suite against the release candidate.
- [ ] Tag and publish `v0.3.0` only after CI is green.

#### A. Context-pack proof metadata — Completed

**Owner:** `mqobsidian` (generator parity).

Corrected on implementation: the proof surface already existed. `context-pack.v1`
carries `exclusions` (`{item, kind, reason}`, kind `forbidden|fallback|irrelevant`)
plus the legacy flat `do_not_read`, and the template, the example, and the
`mq-agent` generator already emit a structured `## Exclusions` section. The one
lagging producer was this repo's own `scripts/generate-context-pack.py`, which
still rendered a flat `## Do not read first` list — so mqobsidian could not emit
the exclusion proof its own contract defines. No new schema fields were needed.

- [x] `scripts/generate-context-pack.py` emits `## Exclusions` at parity with the
  schema, template, example, and mq-agent mirror; `--exclude KIND:ITEM[:REASON]`
  adds structured entries, legacy `--do-not-read` folds in as `irrelevant`
- [x] severity ordering + dedupe by kind+item; an unknown kind degrades to
  `irrelevant` so a producer typo stays on-contract
- [x] `tests/test_context_pack_exclusions.py` (stdlib unittest, runs in the
  public-safe CI via `unittest discover`)
- [~] no schema/example change — the `exclusions` proof already existed in
  `context-pack.v1`; the gap was generator parity, not contract surface

Exit gate:

- [x] this repo's generator explains what it excluded, with a kind + reason per
  entry, within the existing token budget

### Non-goals

- do not fork the frozen `observed/candidate/promoted/deprecated/archived`
  promotion axis or add a parallel scorer/queue (ADR-008 / DEC-002)
- do not rebuild the consumer read contract, the mq-agent consumption doc, or
  the public-safe guard — they exist
- do not add memory categories without a declared consumer need
- do not move orchestration, review execution, or terminal UX into this repo

## Single Source Of Truth And Promotion Governance

**Status:** Completed (A–C landed 2026-07-14; deferred: optional manifest
templates, local live-vault materializer)
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

> **Prior art / what already exists (verified 2026-07-14).** Most of the
> canonical vocabulary is already built and frozen — this block is **not**
> "define the model". `schemas/` already holds `status-manifest.v1`,
> `inbox-manifest.v1`, `views-manifest.v1`, `truth-export-index.v1`,
> `repo-memory-index.v1`, `memory-observation.v1`, `memory-score.v1`,
> `memory-query.v1`, `promotion-event.v1`, plus `decision-record.v1`,
> `learn-record.v1`, `repo-review.v1`, `endpoint-truth.v1`, `stack-truth.v1`,
> `feedback-signal.v1`. `decisions/ADR-008-evidence-based-memory-architecture.md`
> froze the durable-memory + promotion model and names mqobsidian the owner of the
> memory/promotion contracts; `ADR-006` fixes the publish boundary; `ADR-007`
> guarantees no-auto-publish; `roadmap/ROADMAP_NOTES.md` records that the real
> bottleneck is observation volume, not more schema. **Correction (2026-07-14):**
> the manifest *contracts* are already fully built too — `views-manifest.v1`
> (#29), `status-manifest.v1` + `inbox-manifest.v1` (#31) and
> `truth-export-index.v1` (#32) all have complete, documented shapes; status/inbox
> carry `freshness_state` + `drift`, and `truth-export-index` already versions and
> exposes freshness/drift for every surface. An earlier survey wrongly read
> `views-manifest.v1` (a top-level array) as an "empty stub"; it is not. The
> remaining real gaps are narrow: (1) no examples or validation exist for the
> manifest surfaces; (2) there is no single consumer-read contract that ties the
> existing surfaces together. The CodeGraph `codegraph-contract-map.v1` (block
> above) traces one contract producer→consumer; this block is the stack-wide
> truth-surface index consumers read.

### Delivery A — Complete the manifest contracts — ALREADY DONE (#29/#31/#32)

**Owner:** `mqobsidian`

Reconciled 2026-07-14: the manifest contracts already shipped and satisfy this
delivery. No work remains beyond optional templates.

- [x] `schemas/views-manifest.v1.json` has a full shape (top-level array of
  `key`/`label`/`type`/`relative_path` view records) — #29
- [x] `schemas/status-manifest.v1.json` + `schemas/inbox-manifest.v1.json` carry
  `freshness_state`, `drift`, `generated_at`, evidence traceability — #31
- [x] `schemas/truth-export-index.v1.json` versions every surface (via its
  `schema` id) and exposes per-surface `generated_at` + `drift` — #32
- [ ] optional `templates/*-manifest.md` for the four surfaces (deferred — docs
  only; the schemas are self-documenting)

Exit gate:

- [x] no manifest schema is an empty stub; each has a documented shape
- [x] every exported truth surface carries a version (schema id) + freshness marker

### Delivery B — Public-safe examples + validation

**Owner:** `mqobsidian`
**Files:**

- [x] create `examples/status-manifest.example.json`,
  `examples/inbox-manifest.example.json`, `examples/views-manifest.example.json`,
  `examples/truth-export-index.example.json`
- [x] modify `scripts/validate-export.py` (validate each example against its
  schema; reject absolute private paths via `_abs_path_hits`)

Tasks:

- [x] commit one public-safe example per manifest surface
- [x] validate examples in CI as pure JSON with no runtime deps, via a small
  schema-lite checker (required/const/enum/unknown-keys), mirroring the CodeGraph
  contract-map/measurement validators

Scope note: **materializing** manifests from live vault state is a *local* export
concern — the materialized surfaces are gitignored (ADR-006: tracked schema +
public-safe examples, local materialized output). A `generate-truth-manifests.py`
that reads live `systems/`/`inbox/` state is therefore deferred and does not
commit generated truth here; the committed, CI-enforced public surface is the
schema + example + validation.

Exit gate:

- [x] each manifest surface has a public-safe example that validates in CI
- [x] examples reject absolute machine paths (negative-tested)

### Delivery C — SSOT statement + consumer read contract

**Owner:** `mqobsidian`; **consumers:** `mq-agent`, `macos-scripts` / `mqlaunch`
**Files:**

- [x] the SSOT decision already exists as `docs/decision-records/DEC-002-truth-surfaces-ownership.md`
  (public `DEC-NNN` convention — NOT a local `ADR-010`; the raw `decisions/`
  folder is gitignored, public sanitized decisions live under `docs/decision-records/`)
- [x] create `docs/TRUTH_SURFACES.md` (public-safe consumer read contract)

Tasks:

- [x] state mqobsidian as the single truth owner (recorded in DEC-002); enumerate
  every canonical exported truth surface with its version and intended consumer
- [x] define "no competing truth plane": shell/agent layers read or delegate,
  never own (per DEC-002; mirrors the ownership boundary above and ADR-005 P6)
- [x] cross-reference DEC-002, ADR-006 (publish boundary), ADR-008 (memory/promotion
  ownership), ADR-009 (graph ≠ evidence) instead of duplicating them

Exit gate:

- [x] one doc lists every canonical truth surface, its version, and its consumer
- [x] consumers read from exported surfaces instead of inventing local truth

### Non-goals

- do not re-open the ADR-008 frozen memory/promotion model or add a parallel
  scorer/queue
- do not build a ranking or promotion engine here — `mq-agent` owns orchestration
- do not move terminal UX, shell runtime authority, or menu routing into mqobsidian
- do not fabricate data volume to advance Slice 2 readiness (ROADMAP_NOTES)

### Overall exit criteria

- [x] no manifest schema is an empty stub; each has an example that validates in CI (A + B)
- [x] every exported truth surface is versioned and carries a freshness/drift marker (A)
- [x] one consumer-read contract doc enumerates the canonical surfaces and consumers
  (C — `docs/TRUTH_SURFACES.md`)
- [x] mqobsidian is the documented single truth owner (C — recorded in DEC-002,
  not a new ADR-010)
- [x] promotion / durable-memory traceability still runs through the ADR-008
  pipeline, not a new truth plane

*SSOT & Promotion Governance block complete (A–C) on 2026-07-14: contracts
already existed (#29/#31/#32); this track added public-safe examples + validation
(#39) and the `docs/TRUTH_SURFACES.md` consumer contract on top of the DEC-002
ownership decision. Deferred: optional manifest templates, and the local
live-vault materializer (ADR-006 keeps materialized output local).*

## CodeGraph MQ Integration

**Status:** Completed (A–D landed 2026-07-14; deferred: gated `mq-agent`
measurement command)
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
  MCP-tool guidance section; `--symbol` flag)
- [x] modify `templates/context-pack.md` (added the optional queries section —
  a bullet `notes` list is insufficient for bounded tool-intent guidance)
- [x] modify `mq-agent/mq_agent/tools/context_pack.py` (mirrors the generator;
  `--symbol` wired through the CLI)
- [x] add focused tests in both owner repos (mqobsidian `tests/test_context_pack_queries.py`
  wired into CI; mq-agent `tests/test_context_pack_cmd.py` — full suite 846 passed)

Tasks:

- [x] generate concrete MCP tool intentions from named symbols, files, and contract
  records instead of shell commands (symbols via `--symbol`; source files from
  `relevant_files`; contract-map symbols feed in via `--symbol`)
- [x] keep `--codegraph auto|on|off` and preserve non-source suppression
- [x] cap query count and context size so CodeGraph cannot become a token sink
  (`MAX_CODEGRAPH_QUERIES = 5`; a real source pack is 57 lines vs the 200 budget)
- [x] name the target repo in the primary `codegraph_explore` intention
- [x] fall back cleanly to targeted source reads when an index is missing,
  unsupported, locked, or stale (stated in the section guidance)
- [x] never let CodeGraph replace source tests or CLI verification (stated in the
  section guidance)

Exit gate:

- [x] a source-heavy task pack contains bounded MCP tool intentions
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

*Roadmap aligned with verified reality: both blocks are **Completed** — their
delivery files (schemas, examples, validation) all exist under `schemas/`,
`examples/`, and `scripts/validate-export.py`. Current direction is v0.3.0
(explicit owned contracts), stated at the top.*
