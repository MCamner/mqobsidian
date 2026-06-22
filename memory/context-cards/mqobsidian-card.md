---
schema: context-card.v1
repo: mqobsidian
role: Durable memory layer and context compressor for the MQ stack
updated_at: 2026-06-17T00:00:00Z
freshness: current
scope: repo
publishability: public-safe
---

# Context Card: mqobsidian

## Role

Durable memory layer and context compressor for the MQ stack.

## Owns

* reviewed durable memory notes
* public-safe schemas, templates, and examples
* context-pack and context-card contracts
* agent-readable routing surfaces
* token-budget guardrails for context surfaces

## Does not own

* live runtime truth
* workflow orchestration
* MCP tool execution
* source-repo tests or CLI behavior
* generated agent-view orchestration

## Reads from

* MQ source repos when verified code truth is needed
* `systems/*/hot.md`
* `systems/*/index.md`
* `memory/learn/agent/*.md`

## Writes to

* durable vault notes
* schemas and templates
* public-safe examples
* `.mq/context/task-pack.md`

## Use this card when

* task involves durable MQ memory
* task involves context-pack or context-card format
* task involves token reduction for Codex or Claude
* task needs MQ repo responsibility boundaries

## Avoid reading unless needed

* full repo README files
* old release notes
* unrelated UMS docs
* raw logs or unsanitized exports
