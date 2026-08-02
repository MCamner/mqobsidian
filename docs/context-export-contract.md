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
| `mq-agent` `tools/context_export.py` | **designated consumer** — renders the same files and reads budgets from the vault contract |

`mq-agent` is a consumer of this contract, not a second definition of it. Its
context export reads `.mq/context-budgets.json` from the vault and falls back to
documented defaults when the vault predates the contract.

`current-blockers.md` reads optional `## Current blockers` bullets from the
repo's context card. If the section is absent or empty, the export says that no
blockers are declared in the source card; this is not a claim that the live repo
has no blockers. Runtime-sensitive blockers must still be verified in source.

## Ownership of generated agent surfaces

`mqobsidian` owns the **contract, schemas, templates, generators, and examples**.
It does **not** own the generated files once they are committed inside another
repo.

Each target repo owns its committed agent surfaces:

* `AGENTS.md`
* `CLAUDE.md`
* `.mq/context/*`

`mqobsidian` may generate or validate those files, but the target repo owns their
freshness, CI checks, and publication. Generated output must stay
machine-independent: embed `$MQ_OBSIDIAN_DIR` (resolved by the reader), never a
resolved absolute path. `scripts/generate-agents-md.py` defaults to that
placeholder; pass `--vault-path` only for a throwaway local copy.

## Changing a budget

Edit `.mq/context-budgets.json` only. Regenerate exports and run
`scripts/check-token-budget.py`; both the rendered table and the checker follow
the same numbers.
