---
schema: context-card.v1
repo: mq-agent
role: MQ-stack orchestrator
updated_at: 2026-01-01T00:00:00Z
freshness: current
scope: repo
publishability: public-safe
---

<!--
Block-level metadata (Phase 11b), optional but validated when present:
  freshness:      current | stale | archived
  scope:          repo | system | cross-repo | local-only
  publishability: public-safe | sanitized-example | local-rich | generated-target-artifact
mq-agent uses these to bound and rank selection; they never widen the publish
boundary (a public-safe target must not pull a local-rich/local-only block).
-->


# Context Card: mq-agent

## Role

MQ-stack orchestrator.

## Owns

* stack gates and release orchestration
* memory query and context export commands
* operator dashboard truth production

## Does not own

* low-level MCP tool execution
* repo scoring internals
* durable Obsidian storage format

## Reads from

* repo-signal
* mq-mcp
* mqobsidian

## Writes to

* `.mq/context/`
* `mqobsidian/memory/stack-truth/`

## Use this card when

* task involves orchestration or stack gates
* task needs MQ repo responsibility boundaries

## Avoid reading unless needed

* old release notes
* unrelated dashboard history
