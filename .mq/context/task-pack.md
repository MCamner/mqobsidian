---
schema: context-pack.v1
target: codex
task: fix mq-mcp brain writer paths
generated_at: 2026-06-16T22:19:40+00:00
repo: mq-mcp
summary: Minimum context needed for: fix mq-mcp brain writer paths
---

# Task Context Pack

## Relevant repos

* mq-mcp
* mqobsidian
* mq-agent

## Relevant files

* mqobsidian/schemas/repo-review.v1.json
* mqobsidian/schemas/learn-record.v1.json
* mq-agent/docs/VAULT_STRUCTURE.md
* mq-mcp/mq-mcp/runtime/memory/obsidian_writer.py
* mq-mcp/mq-mcp/server.py brain_* wrappers
* mq-mcp/tests/test_obsidian_writer.py
* mq-mcp/docs/TOOL_SAFETY.md
* mq-mcp/docs/ORCHESTRATION_CONTRACT.md
* mq-mcp/docs/tool_contracts.json

## Relevant decisions

* Durable review memory should use `memory/reviews/`.
* Durable learn memory should use `memory/learn/`.
* Legacy root-level `reviews/` and `learn/` paths should remain readable during migration.

## Notes

* Keep mq-mcp as the writer/runtime owner.
* Use mqobsidian schemas as durable-memory contracts, not live execution logic.

## Do not read first

* full README files
* old release notes
* unrelated UMS docs
