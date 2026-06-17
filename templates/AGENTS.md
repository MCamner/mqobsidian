# AGENTS.md

This repo is part of the MQ stack.

These instructions add MQ memory read-order rules. They do not replace
repo-specific build, test, safety, or release instructions.

## Read First

For work related to `<REPO_NAME>`:

1. Read `.mq/context/task-pack.md` if it exists and matches the task.
2. Read `.mq/context/repo-card.md` if it exists.
3. Read `.mq/context/integration-map.md` if it exists.
4. Read `<MQOBSIDIAN_VAULT_PATH>/memory/learn/agent/<REPO_NAME>.md` if it exists.
5. Read `<MQOBSIDIAN_VAULT_PATH>/systems/<REPO_NAME>/hot.md` if it exists.
6. Read `<MQOBSIDIAN_VAULT_PATH>/systems/<REPO_NAME>/index.md` if it exists.

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
