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

`mq-mcp` can provide bounded review and learn outputs. `mqobsidian` stores only
sanitized durable summaries, not raw runtime output.

## repo-signal

`repo-signal` can provide readiness, docs quality, and repo intelligence
signals. Exported records should stay compact and public-safe.

## mq-hal

`mq-hal` should show operator status and route next actions. It should not own
context-pack generation or write durable memory directly.
