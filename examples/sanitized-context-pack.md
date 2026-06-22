---
schema: context-pack.v1
target: both
task: Fix mq-mcp brain writer paths
generated_at: 2026-06-16T00:00:00Z
repo: mq-mcp
summary: Focus on vault path standardization between mq-mcp legacy writers and mq-agent standard memory paths.
---

# Task Context Pack

## Relevant repos

* mq-mcp
* mq-agent
* mqobsidian

## Relevant files

* mq-agent/docs/VAULT_STRUCTURE.md
* mq-mcp/docs/KNOWLEDGE_CONTRACT.md
* mq-mcp/runtime/memory/obsidian_writer.py
* mqobsidian/schemas/repo-review.v1.json

## Relevant decisions

* Standard durable review path is `memory/reviews/`.
* Standard durable learn path is `memory/learn/`.
* Legacy root paths must remain readable during migration.

## Notes

* Update writer outputs conservatively.
* Keep source-of-truth ownership in mq-mcp and mq-agent docs aligned.

## Exclusions

* `forbidden` — mq-ums: unrelated repo for this task; never pull into the pack
* `fallback` — archived release notes: read only if the decisions above are insufficient
* `irrelevant` — full repo README
* `irrelevant` — unrelated screenshots
