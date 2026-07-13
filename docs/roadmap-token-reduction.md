# Roadmap: mqobsidian Token Reduction Layer

**Goal**

Turn `mqobsidian` into a real MQ-stack function that reduces token usage for
Codex and Claude Code by generating small, task-specific context packs instead
of forcing agents to read full READMEs, long docs, old reviews, release notes,
or the whole vault.

`mqobsidian` should become the MQ-stack context compressor:

```text
durable memory -> relevant context cards -> task context pack -> Codex / Claude Code
```

## Core idea

`mqobsidian` stores durable architecture memory.

`mq-agent` queries and exports only the relevant parts.

Each MQ repo receives a small `.mq/context/` snapshot.

Codex and Claude Code read short, generated files instead of large project
history.

```text
mqobsidian
  |- schemas
  |- templates
  |- context cards
  |- decisions
  |- reviews
  |- stack truth
  `- learned patterns

mq-agent
  |- memory query
  |- context pack generation
  |- repo context export
  `- token budget checks

target MQ repo
  |- AGENTS.md
  |- CLAUDE.md
  `- .mq/context/
       |- repo-card.md
       |- active-contract.md
       |- current-blockers.md
       |- integration-map.md
       `- task-pack.md
```

## Problem this solves

Without a memory/context layer, Codex and Claude Code waste tokens on:

* full README files
* duplicated architecture docs
* old release notes
* unrelated review history
* repeated explanations of MQ repo boundaries
* large Obsidian notes
* context that is useful historically but irrelevant to the current task

The desired behavior is:

```text
current task
  -> local memory query
  -> select relevant memory
  -> generate compact context
  -> agent reads only the pack
  -> agent edits with less drift and fewer tokens
```

## Design principles

1. `mqobsidian` owns durable memory, schemas, templates, and public-safe examples.
2. `mq-agent` owns context selection, generation, and export.
3. Individual MQ repos should not duplicate long MQ-stack documentation.
4. `AGENTS.md` and `CLAUDE.md` should be thin routing files, not knowledge dumps.
5. Every generated context file should have a token or line budget.
6. Context should be task-specific whenever possible.
7. Agents should read full docs only when the generated context says they are relevant.
8. Public-safe checks must run before memory exports become reusable context.

## Target outcome

A developer should be able to run:

```bash
mq-agent context pack "fix mq-mcp brain writer paths" --target codex
mq-agent context pack "add endpoint-truth export to mq-ums" --target claude
mq-agent context export --repo mq-agent --target both
mq-agent context export --all --target both
```

And get:

```text
AGENTS.md
CLAUDE.md
.mq/context/repo-card.md
.mq/context/active-contract.md
.mq/context/current-blockers.md
.mq/context/integration-map.md
.mq/context/task-pack.md
```

The result should be a small, relevant context layer that reduces repeated
token cost and improves consistency across Codex and Claude Code sessions.

## Phase 1 - Context budget foundation (done)

**Version target**

`mqobsidian v0.2.0`

**Goal**

Define what "small enough context" means for the MQ stack.

**Add files**

```text
docs/context-budget.md
schemas/context-pack.v1.json
schemas/context-card.v1.json
schemas/repo-memory-index.v1.json
templates/context-pack.md
templates/context-card.md
examples/sanitized-context-pack.md
scripts/check-token-budget.py
```

**Token budget rules**

Initial budgets:

| File                              |        Budget |
| --------------------------------- | ------------: |
| `AGENTS.md`                       | max 120 lines |
| `CLAUDE.md`                       | max 120 lines |
| `.mq/context/repo-card.md`        |  max 60 lines |
| `.mq/context/active-contract.md`  |  max 80 lines |
| `.mq/context/current-blockers.md` |  max 80 lines |
| `.mq/context/integration-map.md`  | max 120 lines |
| `.mq/context/task-pack.md`        | max 200 lines |
| `context-card.md`                 |  max 60 lines |

**Acceptance criteria**

* [x] `scripts/check-token-budget.py` exists.
* [x] CI fails if generated context files exceed budget.
* [x] `docs/context-budget.md` explains why context should be compressed.
* [x] `examples/sanitized-context-pack.md` shows a realistic small pack.
* [x] No generated context file imports a full README by default.

**Token reduction value**

This phase prevents `AGENTS.md` and `CLAUDE.md` from becoming large permanent
token sinks.

## v0.2.0 - Token Reduction MVP

**Goal**

Prove the roadmap with one real MQ task before building every later phase.

The MVP flow is:

```text
mqobsidian memory/context
  -> context-pack.v1
  -> .mq/context/task-pack.md
  -> Codex / Claude Code reads only the pack
```

**MVP task**

Use one concrete task first:

```text
fix mq-mcp brain writer paths
```

The generated pack should identify only the relevant repos, docs, and boundaries:

* `mq-mcp` brain writer paths
* `mq-agent` vault structure docs
* `mqobsidian` schemas and context-pack format

It should explicitly avoid broad first reads such as full READMEs, old release
notes, and unrelated UMS docs.

**Command**

```bash
python3 scripts/generate-context-pack.py \
  --task "fix mq-mcp brain writer paths" \
  --repo mq-mcp \
  --target codex \
  --out .mq/context/task-pack.md
```

**Acceptance criteria**

* [x] The generator can write `.mq/context/task-pack.md`.
* [x] The pack stays under the task-pack line budget.
* [x] The pack lists relevant repos, files, decisions, notes, and do-not-read
  surfaces.
* [x] A Codex or Claude Code run can use the pack without broad repo reads.
* [x] Manual notes compare behavior with and without the pack.

**MVP proof note — 2026-06-17**

The first real run used `.mq/context/task-pack.md` as the first read for
`fix mq-mcp brain writer paths`. It was enough to avoid full README, release
note, and unrelated UMS reads. The pack initially named "mq-mcp runtime memory
writer tools" too vaguely, so the generator was tightened to list the exact
writer, wrapper, test, and contract-doc files. The actual mq-mcp fix moved
review writes to `memory/reviews/`, learn writes and verified promotions to
`memory/learn/`, and kept legacy `learn/` readable during promotion.

Validation:

```bash
python3 scripts/check-token-budget.py
python3 scripts/validate-export.py
python3 scripts/check-sensitive-content.py
uv run pytest tests/test_obsidian_writer.py tests/test_tool_contracts.py tests/test_orchestration_boundary_docs.py
```

**Do not build yet**

Do not attempt all repo cards, generated `AGENTS.md`, or full `mq-agent`
integration until this single-task loop proves useful.

## Phase 2 - MQ Context Cards

**Version target**

`mqobsidian v0.3.0`

**Goal**

Create compact memory cards for each MQ repo.

**Seed status — 2026-06-17**

Phase 2 is mostly seeded, not complete. The first public-safe cards are
`memory/context-cards/mqobsidian-card.md`,
`memory/context-cards/mq-agent-card.md`, and
`memory/context-cards/mq-mcp-card.md`, plus
`memory/context-cards/repo-signal-card.md`. The next batch added
`memory/context-cards/mq-hal-card.md`,
`memory/context-cards/mq-ums-card.md`,
`memory/context-cards/mq-image-analyze-card.md`,
`memory/context-cards/macos-scripts-card.md`,
`memory/context-cards/mq-stack-overview.md`,
`memory/context-cards/active-decisions-card.md`,
`memory/context-cards/current-blockers-card.md`, and
`memory/context-cards/release-state-card.md`. `validate-export.py` now checks
context-card frontmatter plus required card sections. Keep tightening cards
from verified repo boundaries rather than expanding them into mini-READMEs.

**Effect check — 2026-06-18**

`scripts/measure-context-effect.py` compares the task pack plus available
context cards against a broad first-read baseline of README, changelog, roadmap,
and roadmap docs in the relevant repos. The first measurement for the
`fix mq-mcp brain writer paths` task shows 213 compact context lines versus
4114 broad baseline lines, a 94.8% first-read reduction. See
`docs/context-effect.md`.

**Add structure**

```text
memory/context-cards/
  mq-stack-overview.md
  mq-agent-card.md
  mq-mcp-card.md
  repo-signal-card.md
  mqobsidian-card.md
  mq-hal-card.md
  mq-ums-card.md
  mq-image-analyze-card.md
  macos-scripts-card.md
  active-decisions-card.md
  current-blockers-card.md
  release-state-card.md
```

**Card format**

Each card should follow this structure:

```md
# Repo card: mq-agent

## Role

MQ-stack orchestrator.

## Owns

- stack cockpit
- stack truth export
- memory query
- context pack generation
- release and contract gates

## Does not own

- low-level MCP tool execution
- repo scoring internals
- endpoint execution
- Obsidian storage format

## Reads from

- repo-signal
- mq-mcp
- mqobsidian
- mq-ums
- mq-image-analyze

## Writes to

- `.mq/context/`
- `mqobsidian/memory/stack-truth/`
- `~/.mq-agent/`

## Use this card when

- task involves orchestration
- task involves stack gates
- task involves memory export
- task involves context-pack generation

## Avoid reading unless needed

- old release notes
- unrelated dashboard docs
- archived experiment notes
```

**Acceptance criteria**

* Every core MQ repo has one card.
* Each card defines `Role`, `Owns`, `Does not own`, `Reads from`, `Writes to`.
* Cards are short enough to fit inside generated context packs.
* Cards can be validated by `validate-export.py`.

**Token reduction value**

Agents no longer need to infer repo boundaries from full README files.

## Phase 3 - Generated `AGENTS.md` and `CLAUDE.md`

**Version target**

`mqobsidian v0.4.0`

**Goal**

Generate small instruction entrypoints for Codex and Claude Code.

**Seed status — 2026-06-17**

Phase 3 is started, not complete. `templates/AGENTS.md`,
`templates/CLAUDE.md`, `scripts/generate-agents-md.py`, and
`scripts/generate-claude-md.py` now exist. The generator seed only creates small
MQ memory entrypoints; target repo rollout remains manual until per-repo context
exports are stable.

**Generator status — 2026-06-19**

The generators can now write entrypoints for all core MQ repos with `--all` and
`--output-dir`, using the shared repo list in `scripts/mq_repos.py`. This proves
the "generate for every MQ repo" acceptance criterion without mutating sibling
repos before per-repo `.mq/context/` exports are stable.

**Add files**

```text
scripts/generate-agents-md.py
scripts/generate-claude-md.py
templates/AGENTS.md
templates/CLAUDE.md
```

Generation is the rollout path: `generate-agents-md.py` / `generate-claude-md.py`
render portable `AGENTS.md` / `CLAUDE.md` from `templates/AGENTS.md` / `CLAUDE.md`
as additive blocks, not as a replacement for repo-specific build, test, safety, or
release rules. (An earlier `templates/agent-memory-block.md` manual bridge was
retired once generation landed.)

Manual rollout seed — 2026-06-17:

* `mq-agent`
* `mq-mcp`
* `mq-image-analyze`
* `mq-hal`
* `macos-scripts`
* `mcamner-journal`
* `repo-signal`
* `mq-ums`

**Target `AGENTS.md`**

```md
# AGENTS.md

This repo is part of the MQ stack.

## Read first

- `.mq/context/repo-card.md`
- `.mq/context/active-contract.md`
- `.mq/context/current-blockers.md`
- `.mq/context/integration-map.md`

## Rules

- Do not duplicate logic owned by another MQ repo.
- Prefer JSON contracts over free-text coupling.
- Keep repo boundaries explicit.
- Run local tests before release changes.
- Use `mq-agent` stack gates for cross-repo truth.
- Use `mqobsidian` only as durable memory, not as runtime logic.

## Durable memory

MQ-stack memory lives in `mqobsidian`.

Use generated context packs before reading large docs.
```

**Target `CLAUDE.md`**

```md
@AGENTS.md

## Claude Code notes

Use generated context files before reading large docs.

For cross-repo work:
1. Read `.mq/context/repo-card.md`
2. Read `.mq/context/integration-map.md`
3. Read `.mq/context/task-pack.md` if present
4. Only then inspect source files

Do not expand scope unless the task requires it.
```

**Acceptance criteria**

* Generated `AGENTS.md` starts its read order with `.mq/context/task-pack.md`.
* `AGENTS.md` can be generated for every MQ repo.
* `CLAUDE.md` can import or mirror the same rules without duplication.
* Generated files stay inside the token budget.
* Each generated file points to `.mq/context/` instead of embedding long docs.

**Token reduction value**

Codex and Claude Code start from the same compact instruction layer.

## Phase 4 - Per-repo `.mq/context/` exports

**Version target**

`mq-agent v1.x` + `mqobsidian v0.5.0`

**Goal**

Export small repo-local context snapshots into every MQ repo.

**Local rollout status — 2026-06-20**

Phase 4 is locally verified, not shipped. `mq-agent context export` now owns
orchestration from mqobsidian context cards and has written five `.mq/context/`
files to nine repos. A second run reported all 45 managed files unchanged, and
all generated files stayed within their line budgets. `--clean` removes only
the five managed export files, preserving `task-pack.md` and unknown files.
The mqobsidian export is tracked here; the mq-agent implementation and exports
in the other repos remain uncommitted. The next step is to land the command
separately and decide whether the remaining exports are tracked or regenerated
locally.

**Target layout in each MQ repo**

```text
.mq/context/
  repo-card.md
  active-contract.md
  current-blockers.md
  integration-map.md
  token-budget.md
```

**Proposed command**

```bash
mq-agent context export --repo mq-agent --target both
mq-agent context export --repo mq-mcp --target both
mq-agent context export --all --target both
```

**Export source**

`mq-agent` should read from:

```text
mqobsidian/memory/context-cards/
mqobsidian/memory/stack-truth/
mqobsidian/memory/reviews/
mqobsidian/memory/decisions/
mqobsidian/memory/learn/
```

**Acceptance criteria**

* Each MQ repo receives `.mq/context/repo-card.md`.
* Each MQ repo receives `.mq/context/integration-map.md`.
* Exported files are deterministic.
* Exported files are public-safe.
* Exported files pass token budget checks.
* No repo needs to copy large MQ-stack docs into its root.

**Token reduction value**

Agents get local, compressed context without reading the whole stack.

## Phase 4.5 - CodeGraph Source Intelligence Layer

**Version target**

`mqobsidian v0.5.x` + local MQ-stack setup

**Goal**

Add CodeGraph as an optional local source-code intelligence layer for the MQ
stack.

`mqobsidian` remains the durable memory and context-contract layer. CodeGraph
owns local source-code indexing, symbol search, call graphs, callers/callees,
impact analysis, and source-level exploration.

The purpose is to reduce another token sink — the agent grep/read/discover loop —
and replace it with:

```text
task-pack -> CodeGraph query -> focused source edit
```

### Design boundary

`mqobsidian` does **not** become a code graph engine. It should not implement:

* tree-sitter parsing
* symbol extraction
* call graph generation
* source-code full-text search
* impact/blast-radius analysis
* MCP source-code intelligence tools

Those responsibilities belong to CodeGraph. `mqobsidian` should own:

* documented integration rules
* CodeGraph read-order hints for agents
* optional context-card guidance
* install/check scripts for the MQ stack
* generated task-pack hints that say when to use CodeGraph before broad reads

### Target architecture

```text
Codex / Claude Code / Cursor
        |
        v
AGENTS.md / CLAUDE.md
        |
        v
.mq/context/task-pack.md
        |
        +--> mqobsidian durable memory
        |
        +--> CodeGraph local source intelligence
                 |
                 v
             .codegraph/codegraph.db
                 |
                 v
             source repos
```

```text
mqobsidian = what the agent should read first
CodeGraph  = what the agent should ask when it needs to understand the code
mq-agent   = exports/packs the right context
mq-mcp     = runtime and safety contracts
```

### Target repos to index

Initial MQ-stack target repos:

* `mqobsidian`
* `mq-agent`
* `mq-mcp`
* `mq-hal`
* `repo-signal`
* `mq-ums`
* `mq-image-analyze`
* `macos-scripts` / `mqlaunch` if present locally

### Git ignore rule

Each repo should ignore local CodeGraph indexes:

```gitignore
.codegraph/
```

Acceptance:

* [ ] `.codegraph/` is ignored in every indexed MQ repo.
* [ ] No `.codegraph/` database is committed.
* [ ] Public-safe checks still pass after adding ignore rules.

### Add files to mqobsidian

```text
docs/integrations/codegraph.md
memory/context-cards/codegraph-card.md
scripts/init-codegraph-stack.sh
scripts/check-codegraph-stack.sh
```

The CodeGraph agent hint lives inline in `templates/AGENTS.md` (see below) and
flows through the generators, so it needs no separate template file.

Install, agent-wiring, per-repo init, and query-pattern detail live in
`docs/integrations/codegraph.md` so this roadmap stays a plan, not a manual.

### Update generated `AGENTS.md` / `CLAUDE.md`

Update templates only (`templates/AGENTS.md`, `templates/CLAUDE.md`,
`scripts/generate-agents-md.py`, `scripts/generate-claude-md.py`), not every
repo manually. Add a short optional source-intelligence section inline in
`templates/AGENTS.md` so the generators carry it without a separate file.

**Status — 2026-06-21**

Done. `templates/AGENTS.md` gained a 6-line `## Source Intelligence` section;
the generators substitute the template verbatim, so all nine example
entrypoints under `examples/generated-agent-entrypoints/` were regenerated.
`templates/CLAUDE.md` is unchanged — generated `CLAUDE.md` imports `@AGENTS.md`,
so it inherits the section without duplication. Read order is unchanged
(`.mq/context/task-pack.md` first); budget and export checks pass.

Acceptance:

* [x] Generated `AGENTS.md` still starts with `.mq/context/task-pack.md`.
* [x] Generated `CLAUDE.md` still imports or mirrors the same compact read order.
* [x] Generated files stay under token budget.
* [x] CodeGraph text does not turn entrypoints into long docs.
* [x] `python3 scripts/check-token-budget.py` passes.

### Update task-pack generation

Task packs should optionally include CodeGraph guidance when the task is
source-code-heavy. For now, do **not** break `context-pack.v1`; use existing
`notes`, `relevant_files`, and `do_not_read` fields. Later, consider
`context-pack.v1.1` with an optional `codegraph_queries` array.

**Status — 2026-06-21**

Done. `scripts/generate-context-pack.py` appends CodeGraph guidance to the
existing `notes` field — no schema change. A keyword heuristic
(`task_is_source_heavy`) triggers on source-structure tasks (callers, impact,
refactor, rename, trace, symbol, fix, …) and is suppressed for doc-shaped tasks
(readme, roadmap, release note, changelog, …). A `--codegraph {auto,on,off}`
flag overrides the heuristic. The note is repo-aware when a repo is known.

Acceptance:

* [x] No breaking change to `context-pack.v1`.
* [x] Source-heavy packs can suggest CodeGraph queries.
* [x] Non-source tasks do not mention CodeGraph unnecessarily.
* [x] `python3 scripts/validate-export.py` passes.

### Public-safe rules

CodeGraph indexes local source, but `.codegraph/` must remain local.

Acceptance:

* [x] `.codegraph/` is ignored.
* [x] No CodeGraph DB files are exported to examples.
* [x] No local machine paths are added to docs.
* [x] `python3 scripts/check-sensitive-content.py` passes.

### Definition of done

Phase 4.5 is done when:

* [x] CodeGraph install is documented for macOS/Linux, npm, and Windows.
* [x] Claude Code, Cursor, and Codex wiring is documented.
* [x] `docs/integrations/codegraph.md` exists.
* [x] `memory/context-cards/codegraph-card.md` exists.
* [x] CodeGraph agent hint lives inline in `templates/AGENTS.md`.
* [x] `scripts/init-codegraph-stack.sh` exists.
* [x] `scripts/check-codegraph-stack.sh` exists.
* [x] `.codegraph/` is ignored in each initialized MQ repo.
* [x] Generated entrypoints mention CodeGraph only as a compact optional path.
* [x] Task packs can recommend CodeGraph without breaking `context-pack.v1`.
* [x] Token-budget and public-safe checks pass.
* [x] At least one real MQ task is measured with: context pack only,
  context pack + CodeGraph, and broad source scan baseline.

**Status — 2026-06-21:** CodeGraph installed and indexed in `mqobsidian`
(11 files, 116 nodes); measurement recorded in `docs/context-effect.md`
(42 lines via `codegraph node` vs 267 for a broad source scan, ~84% fewer).
`.codegraph/` confirmed git-ignored. Whole stack since indexed (mq-agent,
mq-mcp, mq-hal, repo-signal, mq-ums, mq-image-analyze, macos-scripts); the
first cross-repo task below (`fix mq-mcp brain writer paths`) is now measured
at ~99% fewer source-discovery lines (68 vs 6,922).

### Measurement

Add to `docs/context-effect.md` or a future `docs/token-reduction-metrics.md`:

```text
Task:
Repo:
Without context pack:
With context pack:
With context pack + CodeGraph:
Files read:
Grep/find calls avoided:
Tool calls avoided:
Agent drift observed:
Result:
```

Minimum first tasks to measure:

* [x] `fix mq-mcp brain writer paths` — measured cross-repo (68 vs 6,922 lines,
  ~99% fewer); see `docs/context-effect.md`.
* [ ] Measure `add endpoint-truth export to mq-ums` — blocked: no endpoint-truth
  export implementation exists in `mq-ums` yet.
* [ ] Measure `connect repo-signal review export to mqobsidian` — ready:
  `repo-signal review-export` is implemented locally with `repo-review.v1` and
  `inspect.v1` provenance; focused and full tests pass. Merge and the CodeGraph
  comparison remain.
* [ ] Measure `update mq-agent context export` — ready: the command is implemented
  and its focused test suite passes (7 tests); the CodeGraph comparison remains.
* [ ] Measure `generate AGENTS.md / CLAUDE.md for all MQ repos` — ready: all 9 × 2
  generated examples were refreshed and the canonical contract passes; the
  CodeGraph comparison remains.

**Token reduction value**

This phase reduces token usage at the source-code discovery layer. Before, a
task pack still leaves the agent to grep and read many files; after, the agent
runs a focused CodeGraph source query before a focused file read/edit. The
combination should reduce both broad memory reads and broad source-discovery
reads.

## Phase 5 - Task-specific context packs

**Version target**

`mq-agent context pack`

**Goal**

Generate one small context pack per task.

**Proposed command**

```bash
mq-agent context pack "fix mq-mcp brain writer paths" --target codex
mq-agent context pack "add endpoint-truth export to mq-ums" --target claude
mq-agent context pack "connect repo-signal review export to mqobsidian" --target both
```

**Target output**

```text
.mq/context/task-pack.md
```

**Task pack format**

```md
# Task context pack

## Task

Fix mq-mcp brain writer paths.

## Relevant repos

- mq-mcp
- mqobsidian
- mq-agent

## Relevant memory

- Standard vault path is `memory/reviews/`
- Standard vault path is `memory/learn/`
- Legacy root-level `reviews/` and `learn/` must remain readable during migration

## Relevant files

- `mq-mcp` brain writer tools
- `mq-agent/docs/VAULT_STRUCTURE.md`
- `mqobsidian/schemas/repo-review.v1.json`
- `mqobsidian/schemas/learn-record.v1.json`

## Do not read unless needed

- full README files
- old release notes
- unrelated UMS docs
- visual review examples

## Expected change

- update writer paths
- preserve backward-compatible reads
- add tests
- update docs
```

**Acceptance criteria**

* Context pack is generated from local memory query.
* Context pack lists relevant repos.
* Context pack lists relevant files.
* Context pack lists what not to read.
* Context pack stays under token budget.
* Context pack can be regenerated for the same task.

**Token reduction value**

This is the main token-saving feature.

Instead of loading broad project context, the agent receives only what matters
for the current task.

## Phase 6 - Local memory query before AI context

**Version target**

`mq-agent memory query` extension

**Goal**

Use local search before creating AI context.

**Flow**

```text
user task
  -> mq-agent memory query
  -> select top matching notes
  -> compress into context pack
  -> write `.mq/context/task-pack.md`
  -> Codex / Claude Code reads pack
```

**Proposed commands**

```bash
mq-agent memory query "brain writer paths"
mq-agent memory query "endpoint truth"
mq-agent memory query "repo-signal export contract"

mq-agent context pack --from-query "endpoint truth" --target claude
```

**Acceptance criteria**

* Context pack generation can use memory query results.
* Query results are ranked before export.
* Generated context includes source note names.
* Generated context excludes unrelated memory.
* No AI call is required for the initial memory search.

**Token reduction value**

Local retrieval reduces the need to paste large historical context into Codex
or Claude Code.

## Phase 7 - Repo responsibility map

**Version target**

`mqobsidian v0.6.0`

**Goal**

Prevent duplicated logic and repeated explanation across repos.

**Add file**

```text
docs/repo-responsibility-map.md
```

**Responsibility map**

| Repo               | Responsibility                                              |
| ------------------ | ----------------------------------------------------------- |
| `mqobsidian`       | durable memory, schemas, templates, examples, context cards |
| `mq-agent`         | orchestration, memory query, context export, stack gates    |
| `mq-mcp`           | bounded tool execution, review contracts, learning writes   |
| `repo-signal`      | repo health, readiness scoring, release signals             |
| `mq-ums`           | endpoint/UMS truth provider                                 |
| `mq-image-analyze` | visual/OCR review provider                                  |
| `mq-hal`           | operator-facing summaries and command routing               |
| `macos-scripts`    | terminal launcher and workflow entrypoint                   |

**Acceptance criteria**

* Each repo has a clear "owns / does not own" section.
* Context cards reference the responsibility map.
* Generated task packs include relevant boundaries.
* Agents are instructed not to duplicate ownership.

**Token reduction value**

Agents need fewer repeated explanations about repo boundaries.

## Phase 8 - CI token gates

**Version target**

`mqobsidian v0.7.0`

**Goal**

Make token discipline enforceable.

**Add to CI**

```text
scripts/check-token-budget.py
scripts/check-context-links.py
scripts/check-generated-context.py
```

**CI should fail when**

* `AGENTS.md` is too long
* `CLAUDE.md` is too long
* `.mq/context/*.md` exceeds budget
* generated context links to missing files
* context imports full README files by default
* context includes sensitive strings
* context duplicates large sections from another file

**Acceptance criteria**

* GitHub Actions runs token budget checks.
* Context exports are validated on PR.
* Public-safe checks and token checks run together.
* CI output explains which file exceeded budget.

**Token reduction value**

The MQ stack cannot slowly drift back into large permanent context files.

## Phase 9 - Integration into MQ repos

**Version target**

Cross-repo rollout

**Goal**

Make `mqobsidian` a real function across the stack, not just a documentation repo.

**Required integrations**

### `mq-agent`

Add:

```bash
mq-agent context export
mq-agent context pack
mq-agent context budget-check
mq-agent context doctor
```

### `mq-mcp`

Update:

```text
brain_record_decision
brain_record_review
brain_record_learning
brain_record_session
```

So they write to standard `mqobsidian/memory/*` paths.

### `repo-signal`

Add:

```bash
repo-signal export-review --target mqobsidian
```

Or expose JSON for:

```text
repo-review.v1
repo-health.v1
readiness-summary.v1
```

### `mq-ums`

Add:

```bash
mq-ums status --json
mq-ums endpoint-truth --out endpoint-truth.v1.json
```

### `mq-image-analyze`

Add:

```bash
mq-image-analyze visual-review --json
mq-image-analyze visual-review --target mqobsidian
```

### `mq-hal`

Add display support for:

```text
context pack status
memory freshness
current blockers
repo responsibility map
```

### `macos-scripts / mqlaunch`

Add menu items:

```text
Generate MQ context pack
Export repo context
Check token budget
Open mqobsidian memory note
```

**Acceptance criteria**

* Every MQ repo either reads from or writes to the mqobsidian memory model.
* Every MQ repo has `.mq/context/repo-card.md`.
* `mq-agent context export --all --target both` works.
* `mq-agent context pack "<task>" --target both` works.
* Codex and Claude Code can start from generated context.

**Token reduction value**

The entire MQ stack gets a shared low-token operating model.

## Phase 10 - Measurement

**Version target**

`mqobsidian v1.0.0`

**Goal**

Prove that token usage is reduced.

**Add file**

```text
docs/token-reduction-metrics.md
```

**Suggested metrics**

| Metric                                         |        Before |                 After |
| ---------------------------------------------- | ------------: | --------------------: |
| Lines in root agent instructions               | README + docs | `AGENTS.md` + context |
| Number of files agent must read before editing |          many |                   few |
| Repeated architecture explanation per session  |          high |                   low |
| Context files over budget                      |       unknown |                  zero |
| Task-specific context availability             |        manual |             generated |
| Drift between repos                            |          high |                 lower |

**Manual measurement process**

For each test task:

1. Run once without context pack.
2. Run once with context pack.
3. Compare files read.
4. Compare amount of pasted context.
5. Compare number of clarification steps.
6. Compare whether the agent respected repo boundaries.
7. Record result in `memory/measurements/`.

**Acceptance criteria**

* At least five real MQ tasks measured.
* Each task has before/after notes.
* Token budget checks pass.
* Context packs are useful enough to keep.
* v1.0.0 can be described as "working context compression layer".

**Token reduction value**

This turns the idea into measurable architecture value.

## Roadmap summary

| Phase | Name                          | Main output                           |
| ----: | ----------------------------- | ------------------------------------- |
|     1 | Context budget foundation     | token budget docs and checks          |
|     2 | MQ Context Cards              | short cards per repo                  |
|     3 | Generated AGENTS / CLAUDE     | thin agent entrypoints                |
|     4 | Per-repo `.mq/context/`       | local context snapshots               |
|   4.5 | CodeGraph Source Intelligence | optional local codegraph acceleration |
|     5 | Task-specific context packs   | main token-saving feature             |
|     6 | Local memory query first      | retrieval before AI context           |
|     7 | Repo responsibility map       | less duplicated explanation           |
|     8 | CI token gates                | enforce small context                 |
|     9 | Cross-repo integration        | real MQ-stack function                |
|    10 | Measurement                   | prove reduction                       |

## Definition of done

`mqobsidian` becomes a real MQ-stack function when:

* it stores durable stack memory
* it defines schemas and templates for reusable context
* it generates or supports context cards
* `mq-agent` can export context into MQ repos
* Codex can start from `AGENTS.md` plus `.mq/context/`
* Claude Code can start from `CLAUDE.md` plus `.mq/context/`
* task-specific context packs exist
* token budgets are checked in CI
* every MQ repo has a short repo card
* memory is queried before large docs are read
* token reduction is measured on real MQ tasks
* CodeGraph is documented as an optional local source-intelligence layer
* `.codegraph/` is ignored and never exported as durable memory
* generated agent entrypoints tell agents when to use mqobsidian vs CodeGraph
* source-heavy task packs can recommend CodeGraph before broad grep/read loops
* token reduction is measured separately for memory reads and source discovery reads

At that point, `mqobsidian` is no longer just an Obsidian-compatible note
layer.

It becomes:

```text
MQ-stack context compressor and durable architecture memory layer.
```

## Phase 11 - Next Context-Quality Layer

**Version target**

`mqobsidian v1.x`

**Goal**

Improve selection *quality* on top of the working compression layer (Phases
1-10), without re-implementing anything `mq-agent` already owns. Phases 1-10
proved that small packs work and measured the reduction (94.8% first-read,
~99% source-discovery via CodeGraph). Phase 11 adds the three things those
phases do not yet express: explicit exclusions, block-level metadata, and a
feedback loop.

**Ownership boundary (unchanged, restated for this phase)**

* `mqobsidian` owns the *knowledge*: durable notes, schemas, templates,
  public-safe examples, and the new metadata/exclusion vocabulary below.
* `mq-agent` owns the *mechanism*: context selection, pack generation, and
  export. Any compiler or export script belongs in `mq-agent`, **not** in
  `mqobsidian/scripts/`. Phase 11 must not move selection logic into this repo.

### 11a - Negative context

Make it explicit what must **not** enter a pack, instead of relying on the
generator to omit it by accident.

* [x] Define a format for explicit exclusions in the context-pack contract.
  Optional `exclusions` array in `schemas/context-pack.v1.json`, each entry
  `{ item, kind, reason? }`. Additive and backward-compatible: the legacy flat
  `do_not_read` list is retained and means `kind: irrelevant`.
* [x] Distinguish `irrelevant`, `fallback`, and `forbidden` so historical or
  large blocks become fallback, not default. (`kind` enum.)
* [x] Mark unrelated repos as explicitly excludable per task-type.
  (`forbidden` entry naming the repo; see the example.)
* [x] Add a sanitized example that shows both included and excluded context.
  (`examples/sanitized-context-pack.md` now has a structured `## Exclusions`
  section; `templates/context-pack.md` carries the canonical shape.)

**Definition of done**

* [x] Negative context is described, exemplified, and consumable by `mq-agent`.
  The contract + canonical template + example are in place. Producing
  `exclusions` from real packs is mq-agent-side work (it owns generation); the
  contract is now stable for that consumer.
* [x] **Any change to `schemas/context-pack.v*` regenerates the affected
  examples in the same PR** — otherwise the stale-example CI guard fails.
  (Schema + template + example landed together; all five public-safe CI gates
  pass, and `examples/repo-context-exports` shows no regeneration drift.)

### 11b - Block-level metadata

Improve selection quality with structured stand-off data, consumed by
`mq-agent` — not a new compiler here. The *block* is the context-card
(`schemas/context-card.v1.json`): the per-repo unit `mq-agent` assembles into
packs. Metadata lives in card frontmatter.

* [x] `freshness`: `current` / `stale` / `archived`, demoted-not-deleted in
  selection. (Optional enum on `context-card.v1`.)
* [x] `scope`: `repo` / `system` / `cross-repo` / `local-only`, used to bound
  selection and prevent context bloat. (All 14 cards tagged; the four synthesis
  cards are `cross-repo`, repo cards are `repo`.)
* [x] `publishability`: `public-safe` / `sanitized-example` / `local-rich` /
  `generated-target-artifact`. Documented to only *narrow* a target, never widen
  the publish boundary (see `docs/CONTEXT_CARDS.md`).
* [ ] Optional `priority` as supporting metadata only. (Deferred — not needed
  yet; add when a real selection case requires ranking beyond freshness/scope.)
* [x] Update schema + examples; keep backward compatibility where required.
  (Fields are optional; `validate-export.py` enforces the enums from the schema
  only when present, so pre-existing cards and consumers are unaffected.)

**Definition of done**

* [x] Blocks can be tagged consistently and `mq-agent` can use the metadata
  without ownership moving into `mqobsidian`. (All 14 cards tagged; CI validates
  the enums; the metadata propagates into generated `repo-card.md` exports.
  Producing/consuming it in selection is mq-agent-side work.)

### 11c - Feedback loop

Let real usage improve selection over time, with no publish leak.

* [x] Define which usage signals are worth capturing.
  `feedback-signal.v1` (`schemas/feedback-signal.v1.json`): per pack-usage event
  `task` / `generated_at` / `repo` / `outcome` plus per-block `judgments`
  (`useful` / `noise` / `missing` / `stale`). See `docs/FEEDBACK_LOOP.md`.
* [x] Keep signal logs in a local-only, gitignored surface.
  Live records append to `feedback/` (added to `.gitignore`); only the schema and
  one sanitized example (`examples/feedback-signal.example.json`) are public.
* [x] Define how high-value material is promoted into better templates/examples.
  Recurring `useful` / `missing` becomes a *proposal* routed through the existing
  inbox / template-based note-creation path (`docs/FEEDBACK_LOOP.md`).
* [x] Define how stale / low-value material is downgraded.
  Recurring `noise` → demote / add a `fallback`/`forbidden` exclusion for the
  task-type; recurring `stale` → flip the card's `freshness`. Maps onto the 11b
  knobs mq-agent already consumes.
* [x] Guarantee the loop never auto-publishes anything.
  Recorded as a local decision, ADR-007: signal data gitignored and never
  force-added; promotion/downgrade are review-gated proposals, not commits; the
  publish boundary applies to anything the loop suggests.

**Definition of done**

* [x] A safe improvement loop exists whose data never requires committing
  local-rich material. The vocabulary, local-only surface, promotion/downgrade
  policy, and no-auto-publish guarantee are defined and CI-checked
  (`validate-export.py` validates the example against the schema). Emitting
  signals and computing proposals is mq-agent-side work — a separate gated
  producer track, symmetric with 11a/11b → mq-agent PR #102.

### Publishability map for Phase 11 work

* Tracked / public-safe: `docs/`, `schemas/`, `templates/`, `examples/`,
  `scripts/` (knowledge + checks only — **no compiler/export scripts**), `.mq/`.
* Local-only / gitignored: `views/`, `benchmarks/`, raw selection logs,
  unsanitized task snapshots, repo-specific experiments.

### Decision carried into Phase 11 (resolved)

The Phase 4 question — whether per-repo `.mq/context/` exports are tracked in
each target repo or regenerated locally — is **resolved by ADR-006**: public-safe
`.mq/context/` exports are tracked in the target repo, local regen is the build
method (not the publish model), and repos without a decided public agent surface
stay local-only (mirrors ADR-005 P6). The ADR lives in the gitignored
`decisions/` convention, so it is not expected in public history. Phase 11's
publishability map and the CI/regen drift gates inherit this decision.

**Token reduction value**

Phases 1-10 made packs *small*; Phase 11 makes them *right* — fewer wrong
blocks pulled in, explicit exclusions, and a loop that keeps the gains real
instead of cosmetic.
