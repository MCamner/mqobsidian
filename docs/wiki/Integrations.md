# Integrations

`mqobsidian` is a memory layer in the MQ stack.

## Stack Boundary

```text
mqlaunch    -> starts commands and menus
mq-agent    -> orchestrates workflows and exports truth
mq-mcp      -> bounded runtime and review tools
repo-signal -> repo health and readiness
mq-hal      -> operator-facing summaries
mqobsidian  -> durable memory and compact context
```

## mq-agent

`mq-agent` should export high-value, durable state into `mqobsidian`, such as:

- stack summaries
- release readiness snapshots
- reviewed action outcomes
- dashboard-ready truth summaries

## mq-mcp

`mq-mcp` provides bounded review, learn, and brain tools. `mqobsidian` stores only
sanitized durable summaries, not raw runtime output.

Current brain-facing tools:

- `brain_status` reports vault availability and top-level folders.
- `brain_preview_memory_scores` previews `memory-score.v1` from real observations without writes.
- `brain_apply_memory_scores` writes `memory-score.v1` records and appends `promotion-event.v1` audit when status changes.
- `brain_record_*` writes decisions, reviews, sessions, and learned patterns.
- `brain_promote_learning` moves verified learning notes into `learn/verified/`.

## repo-signal

`repo-signal` can provide readiness, docs quality, and repo intelligence
signals. When configured for memory export, real inspect runs may emit
`memory-observation.v1` records into `memory/observations/`. Exported records
should stay compact and public-safe.

## mq-hal

`mq-hal` should show operator status and route next actions. It should not own
context-pack generation or write durable memory directly.
