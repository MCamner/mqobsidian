---
type: agent-view
repo: mqobsidian
status: active
tags: [agent, context, durable-memory]
updated: 2026-07-30
---

# mqobsidian Agent View

## Role

Durable memory layer and compact context-contract surface for the MQ stack.

## Read first

1. Use `.mq/context/task-pack.md` only when its `task` and `repo` match the current work.
2. Read `systems/mqobsidian/hot.md` for current high-value context.
3. Read `systems/mqobsidian/index.md` for the stable system map.
4. Expand to a context card or focused durable note only when needed.

## Owns

- reviewed durable memory
- context schemas, templates, cards, and public-safe examples
- token-budget and context-export contracts
- compact routing surfaces for agents

## Does not own

- live runtime, CLI, test, or implementation truth
- orchestration and context selection
- bounded tool execution
- raw logs or unsanitized enterprise data

## Avoid reading first

- the full README
- old release notes
- the complete roadmap
- unrelated reviews or source-repo documentation

## Truth boundary

Use this repo for durable memory, routing, schemas, templates, and reusable
lessons. Verify current behavior in the owning source repo or tool before making
runtime, CLI, test, or implementation claims.

## Next useful files

- `docs/CONTEXT_CONTRACT.md`
- `docs/TOKEN_BUDGET.md`
- `.mq/context-budgets.json`
- `schemas/context-pack.v1.json`
- `templates/context-pack.md`
