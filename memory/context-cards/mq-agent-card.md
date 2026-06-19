---
schema: context-card.v1
repo: mq-agent
role: MQ-stack workflow orchestrator and context-export owner
updated_at: 2026-06-17T00:00:00Z
---

# Context Card: mq-agent

## Role

MQ-stack workflow orchestrator and context-export owner.

## Owns

* CLI workflow orchestration
* stack gates and release checks
* memory query and context export commands
* agent-view rebuild and drift checks
* safe execution routing through approval gates

## Does not own

* durable Obsidian storage format
* low-level MCP tool execution
* repo-signal scoring internals
* mqobsidian note curation
* endpoint runtime execution

## Reads from

* mqobsidian durable memory
* mq-mcp tool surface
* repo-signal repo assessments
* MQ source repos for live code truth

## Writes to

* `.mq/context/`
* `memory/learn/agent/*.md`
* stack truth exports
* operator-facing command output

## Use this card when

* task involves orchestration or stack gates
* task involves memory query or context export
* task involves agent-view rebuild or drift checks
* task involves safe execution through `mq-agent`

## Avoid reading unless needed

* old release notes
* unrelated dashboard docs
* archived experiment notes
* full repo README files
