# Token Budget

## Purpose

This document defines size budgets for agent-readable context surfaces in the MQ
stack. The goal is to stop slow context sprawl. These are not style preferences —
they are operational limits.

## Core rule

A context surface should always be smaller than the thing it helps avoid reading.
If a note grows large enough that agents stop benefiting from it, it has failed
its purpose.

## Source of truth

The **hard limits** below are the ones enforced by
[`scripts/check-token-budget.py`](../scripts/check-token-budget.py) — that script,
not this prose, is the gate. Budgets for the `.mq/context` export files live in
[`.mq/context-budgets.json`](../.mq/context-budgets.json)
(see [context-export-contract.md](context-export-contract.md)); they are not
restated here. Change a number in the script or the JSON, not only in this table.

## Authoring-surface budgets

| Surface | Target | Soft (review) | Hard (enforced) |
| --- | --- | --- | --- |
| `AGENTS.md` | 40–80 | 100 | 120 |
| `CLAUDE.md` | 40–80 | 100 | 120 |
| `README.md` | — | 140 | 160 |
| `systems/*/hot.md` | 15–30 | 50 | 80 |
| `systems/*/index.md` | 30–60 | 90 | 120 |
| `memory/learn/agent/*.md` | 40–90 | 100 | 120 |
| context card (`memory/context-cards/*.md`) | 20–40 | 50 | 60 |
| `templates/context-pack.md` | — | 70 | 80 |

`.mq/context/*` export files (including `task-pack.md`) follow
[`.mq/context-budgets.json`](../.mq/context-budgets.json), not this table.

## Budget meanings

- **Target** — the normal expected size.
- **Soft** — allowed temporarily, but should trigger review.
- **Hard** — the enforced limit; treat as overgrown and refactor.

## Refactor rules

When a surface crosses the soft limit: trim duplicated text, move detail into
smaller linked docs, replace prose with structure, split out context cards if
needed.

When a surface crosses the hard limit: do not keep growing it — split or compress,
move low-frequency material elsewhere, keep the front-door surface small.

## Hot note rule

`hot.md` is the first place that must stay small. If `hot.md` starts to look like
history, it is wrong. Use it only for current state, current priority, current
risk, and the immediate next action.

## Agent view rule

Agent views exist to prevent broad scans. They should answer: what should I read
first, what should I avoid, what is the boundary, what next file matters. If they
become long summaries of whole systems, they are too large.

## Task pack rule

A task pack should be specific to the current task, short-lived, smaller than the
combined source notes it replaces, and explicit about what not to read. It should
not become a second index or a mini repo manual.

## Enforcement model

Three levels, tightening over time:

1. human review
2. lint warning
3. hard failure once the stack is ready for strict enforcement

This repo prefers warnings before hard failures, then tightens later. The current
gate (`check-token-budget.py`) already hard-fails on the enforced limits above.

## Compression principle

The right response to a large surface is not "add more summary text." It is:
improve selection, split frequency bands, move detail behind links, and keep the
front door small.
