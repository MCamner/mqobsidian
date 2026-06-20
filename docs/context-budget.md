# mqobsidian Context Budget

`mqobsidian` should reduce context load, not become a new source of prompt bloat.

## Budget targets

The full budget table for authoring surfaces (`AGENTS.md`, `CLAUDE.md`, `hot.md`,
`index.md`, agent views, cards) lives in [TOKEN_BUDGET.md](TOKEN_BUDGET.md), and
the `.mq/context/*` export files follow
[`.mq/context-budgets.json`](../.mq/context-budgets.json), the single source of
truth (see [context-export-contract.md](context-export-contract.md)). Do not
restate the numbers here.

These are governance limits, not exact tokenizer measurements. They are meant
to keep the first-pass context compact enough that Codex and Claude Code can
load rules first and only expand when needed.

## Practical rules

* Root instruction files are index surfaces, not knowledge dumps.
* Durable memory stays in schemas, examples, decisions, learn notes, and stack
  truth records.
* Context packs should point to source files or note paths instead of copying
  long passages.
* If a context pack grows too large, split it into repo cards plus a smaller
  task pack.

## Suggested flow

```text
task
-> local memory query
-> choose relevant notes
-> summarize to context-pack.v1
-> feed only that pack to the coding agent
```

## Current check

`scripts/check-token-budget.py` validates a conservative line-budget baseline for
tracked instruction and context surfaces in this repo. Other MQ repos can adopt
the same thresholds or tune them for their own `.mq/context/` layout.
