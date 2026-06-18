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
4111 broad baseline lines, a 94.8% first-read reduction. See
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

**Add files**

```text
templates/agent-memory-block.md
scripts/generate-agents-md.py
scripts/generate-claude-md.py
templates/AGENTS.md
templates/CLAUDE.md
```

`templates/agent-memory-block.md` is the manual rollout bridge before full
generation exists. Add it to target repos as an additive block, not as a
replacement for repo-specific build, test, safety, or release rules.

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

* `templates/agent-memory-block.md` exists and starts read order with
  `.mq/context/task-pack.md`.
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

| Phase | Name                        | Main output                  |
| ----: | --------------------------- | ---------------------------- |
|     1 | Context budget foundation   | token budget docs and checks |
|     2 | MQ Context Cards            | short cards per repo         |
|     3 | Generated AGENTS / CLAUDE   | thin agent entrypoints       |
|     4 | Per-repo `.mq/context/`     | local context snapshots      |
|     5 | Task-specific context packs | main token-saving feature    |
|     6 | Local memory query first    | retrieval before AI context  |
|     7 | Repo responsibility map     | less duplicated explanation  |
|     8 | CI token gates              | enforce small context        |
|     9 | Cross-repo integration      | real MQ-stack function       |
|    10 | Measurement                 | prove reduction              |

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

At that point, `mqobsidian` is no longer just an Obsidian-compatible note
layer.

It becomes:

```text
MQ-stack context compressor and durable architecture memory layer.
```
