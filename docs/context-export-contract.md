# Context Export Contract

`mqobsidian` owns the `.mq/context` export contract. Other repos render it; they
do not redefine it.

## What the contract covers

A per-repo `.mq/context` export is a fixed set of compact files generated from a
repo's context card:

* `repo-card.md` — the card itself
* `active-contract.md` — owns / does-not-own
* `current-blockers.md` — known blockers + check-before-acting
* `integration-map.md` — reads-from / writes-to / use-when / avoid
* `token-budget.md` — the line budgets below
* `task-pack.md` — generated per task, not by the repo export

## Single source of truth

Line budgets and the `token-budget.md` render order live in one published file:

* [`.mq/context-budgets.json`](../.mq/context-budgets.json) (`context-budget.v1`)

Both consumers read it. Do not hardcode budget numbers anywhere else.

## Producers and consumers

| Component | Role |
| --- | --- |
| `.mq/context-budgets.json` | authoritative budget contract (this repo) |
| `scripts/generate-repo-context-export.py` | reference renderer + checker source (this repo) |
| `scripts/check-token-budget.py` | enforces budgets against generated files (this repo) |
| `mq-agent` `tools/context_export.py` | **consumer** — renders the same files, reads budgets from the vault contract |

`mq-agent` is a consumer of this contract, not a second definition of it. When it
renders a repo's `token-budget.md` it reads `.mq/context-budgets.json` from the
vault and falls back to the documented defaults only when the vault predates the
contract.

## Changing a budget

Edit `.mq/context-budgets.json` only. Regenerate exports and run
`scripts/check-token-budget.py`; both the rendered table and the checker follow
the same numbers.
