# Read Discipline

How an agent should *read* `mqobsidian` — the low-token contract that sits in
front of every other doc here. The [context export contract](context-export-contract.md)
defines the *format* of `.mq/context` files; this defines the *reading order and
stopping rule* an agent applies to the vault as a whole.

## Read order

Start with the smallest surface that can answer the task and stop there:

1. `.mq/context/task-pack.md` — generated per task; if it matches, often enough on its own
2. `memory/learn/agent/<repo>.md` — compressed repo agent view (local, may be absent)
3. `systems/<repo>/hot.md` — current working memory
4. `systems/<repo>/index.md` — nav page (state, priorities, risks)
5. relevant context cards or `docs/` only when the surfaces above are insufficient

## Smallest useful surface

- Read the smallest view first and **stop once the answer is grounded**.
- Do not scan whole directories. Do not open more than ~3 full pattern notes
  without a clear reason.
- Prefer a context card or `hot.md` over re-reading the underlying long note.
- **Do not scan the vault by default.** Broad fan-out reads are the failure mode
  this contract exists to prevent — the measured baseline is ~20x more lines than
  a task pack plus cards (see [context-effect.md](context-effect.md)).

## Source-of-truth map

The vault records what was true **when written**. It is not the runtime.

| Question is about… | Authoritative source |
| --- | --- |
| current code, tests, CLI, contracts, release state | the source repo, verified there |
| live tool execution and runtime contracts | `mq-mcp` |
| workflow orchestration and context export | `mq-agent` |
| repo health / readiness scoring | `repo-signal` |
| durable, public-safe memory and schemas | `mqobsidian` (this repo) |

Before claiming current behavior, verify in the source repo — not from a vault
note. If evidence is still weak, capture the open question as a research node
rather than stating a conclusion.

## Stopping rule

You are done reading when the task is grounded, not when the directory is
exhausted. If you find yourself opening a fourth full note, stop and ask whether
a smaller surface (task pack, card, `hot.md`) already answers the question.
