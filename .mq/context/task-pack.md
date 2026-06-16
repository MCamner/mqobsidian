---
schema: context-pack.v1
target: codex
task: fix mq-mcp brain writer paths
generated_at: 2026-06-16T18:13:16+00:00
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
* mq-mcp runtime memory writer tools

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
