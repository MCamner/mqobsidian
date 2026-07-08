<!--
mq-template-lineage: superset-v1
Generated from mqobsidian agent-entrypoint templates for mcamner-journal.
Do not hand-edit this file directly; edit the mqobsidian templates and regenerate.

Ownership model:
- mqobsidian owns the contract, templates, schemas, and generators.
- this repo owns this committed agent surface once published.

Paths use the portable ${MQ_OBSIDIAN_DIR:-$HOME/mqobsidian} shell fallback.
Regenerate with:
  MQ_OBSIDIAN_DIR=<path-to-mqobsidian> \
    python3 "$MQ_OBSIDIAN_DIR"/scripts/generate-agents-md.py --repo mcamner-journal --out AGENTS.md
-->

# AGENTS.md

This repo is part of the MQ stack.

These instructions add MQ memory read-order rules. They do not replace
repo-specific build, test, safety, or release instructions.

## mqobsidian Location

Default local vault path: `$HOME/mqobsidian`. If `MQ_OBSIDIAN_DIR` is set,
prefer that value.

## Read First

For work related to `mcamner-journal`:

1. Read `.mq/context/task-pack.md` if it exists and matches the task.
2. Read `.mq/context/repo-card.md` if it exists.
3. Read `.mq/context/integration-map.md` if it exists.
4. Read `${MQ_OBSIDIAN_DIR:-$HOME/mqobsidian}/memory/learn/agent/mcamner-journal.md` if it exists.
5. Read `${MQ_OBSIDIAN_DIR:-$HOME/mqobsidian}/systems/mcamner-journal/hot.md` if it exists.
6. Read `${MQ_OBSIDIAN_DIR:-$HOME/mqobsidian}/systems/mcamner-journal/index.md` if it exists.
7. Read `${MQ_OBSIDIAN_DIR:-$HOME/mqobsidian}/memory/learn/repos/mcamner-journal.md` if it exists.
8. Read individual pattern notes only if the compressed notes are insufficient.

Stop reading as soon as the task is grounded.

## Low-Token Rules

- Prefer task packs and agent views over full notes.
- Prefer hot/index over pattern notes.
- Do not scan the whole vault by default.
- Do not open multiple pattern notes unless clearly needed.
- Summarize instead of replaying long note bodies.

## Rules

- Do not duplicate logic owned by another MQ repo.
- Prefer JSON contracts over free-text coupling.
- Keep repo boundaries explicit.
- Use `mqobsidian` only as durable memory, not runtime truth.
- Verify current code behavior, tests, contracts, and CLI behavior in this repo.

## Durable Memory

MQ-stack memory lives in `mqobsidian`. Use generated context packs before
reading large docs.

`mqobsidian` is durable memory, not live runtime truth. If the task depends on
current code behavior, tests, contracts, CLI behavior, or runtime state, verify
in this repo before making claims.

## Observation Emission

After evidence-backed work reveals a reusable pattern, workflow, convention, or
review finding, emit one observation:

```bash
uv --directory ${MQ_OBSIDIAN_DIR:-$HOME/mqobsidian}/memory run python commands/emit_observation.py \
  --producer codex --repository mcamner-journal --workflow task-work --category pattern --confidence 0.70 \
  --title "Short reusable lesson" --observation "What was learned and when to reuse it" \
  --evidence-source codex --evidence-reference "commit, test run, review, or session reference" \
  --evidence-excerpt "Concrete evidence summary" --tag mcamner-journal
```

Use `--producer claude` from Claude Code. Prefer `--dry-run` when uncertain.
Do not emit secrets, private paths, raw logs, chain-of-thought, or unevidenced opinions.

## Source Intelligence

If `.codegraph/` exists, prefer CodeGraph for source-structure questions before
broad file scans: symbol lookup, callers/callees, impact analysis, code-flow.

Do not use CodeGraph as durable MQ memory. Use `mqobsidian` context packs and
cards for memory, repo boundaries, and prior verified work.

## Writing Rules

When creating notes, summaries, or exports:

- separate facts, interpretation, and recommendation
- keep outputs compact
- preserve timestamps and provenance when relevant
- prefer links over duplicated prose
- avoid raw dumps

Do not store or copy secrets, tokens, internal hostnames, raw enterprise logs,
or machine-specific private paths.

## MQ Skills

Repo-local skills live under `.agents/skills/` (Codex) and `.claude/skills/`
(Claude Code). Route by each skill's frontmatter `description`. A few are
near-universal across MQ repos:

- `mq-writing-plans` — before multi-step or cross-repo changes.
- `mq-worktree-safe` — before risky branch/worktree flows.
- `mq-secrets-public-safe` — before publishing, commit, or PR.

Use any other installed skill when its description matches the task.

## Fallback Rule

If `mqobsidian` is missing, stale, or too weak for the task, say so and verify
in the repo. Do not invent continuity.
