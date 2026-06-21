# AGENTS.md

This repo is part of the MQ stack.

These instructions add MQ memory read-order rules. They do not replace
repo-specific build, test, safety, or release instructions.

## Read First

For work related to `repo-signal`:

1. Read `.mq/context/task-pack.md` if it exists and matches the task.
2. Read `.mq/context/repo-card.md` if it exists.
3. Read `.mq/context/integration-map.md` if it exists.
4. Read `$MQ_OBSIDIAN_DIR/memory/learn/agent/repo-signal.md` if it exists.
5. Read `$MQ_OBSIDIAN_DIR/systems/repo-signal/hot.md` if it exists.
6. Read `$MQ_OBSIDIAN_DIR/systems/repo-signal/index.md` if it exists.

Stop reading as soon as the task is grounded.

## Rules

- Do not duplicate logic owned by another MQ repo.
- Prefer JSON contracts over free-text coupling.
- Keep repo boundaries explicit.
- Use `mqobsidian` only as durable memory, not runtime truth.
- Verify current code behavior, tests, contracts, and CLI behavior in this repo.

## Durable Memory

MQ-stack memory lives in `mqobsidian`.

Use generated context packs before reading large docs.

## Source Intelligence

If `.codegraph/` exists, prefer CodeGraph for source-structure questions before
broad file scans: symbol lookup, callers/callees, impact analysis, code-flow.

Do not use CodeGraph as durable MQ memory. Use `mqobsidian` context packs and
cards for memory, repo boundaries, and prior verified work.
