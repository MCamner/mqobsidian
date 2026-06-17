---
schema: context-card.v1
repo: mq-mcp
role: MCP execution and validation runtime for the MQ stack
updated_at: 2026-06-17T00:00:00Z
---

# Context Card: mq-mcp

## Role

MCP execution and validation runtime for the MQ stack.

## Owns

* bounded MCP tool execution
* runtime contracts and safety classes
* review, learn, decision, and memory tool surfaces
* deterministic release-readiness validation
* runtime truth for exposed MCP behavior

## Does not own

* workflow orchestration
* durable Obsidian curation
* repo-signal scoring internals
* context-pack selection or export orchestration
* ungated shell execution

## Reads from

* local mq-mcp source files and contracts
* `.env` configuration when explicitly loaded
* mqobsidian schemas for durable-memory contracts
* mq-agent calls through the MCP bridge

## Writes to

* review memory through brain writer tools
* learn memory and learn inbox outputs
* decision and session memory records
* structured runtime diagnostics

## Use this card when

* task involves MCP tools or contracts
* task involves brain writer paths
* task involves runtime safety gates
* task involves deterministic release readiness

## Avoid reading unless needed

* unrelated UMS docs
* old release notes
* full repo README files
* raw or unsanitized logs
