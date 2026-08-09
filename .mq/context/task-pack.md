---
schema: context-pack.v1
target: claude
task: fix mq-mcp brain writer paths
generated_at: 2026-08-08T13:59:48+00:00
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

## CodeGraph queries

Use the installed CodeGraph MCP tools directly; these are tool intentions, not shell commands. Treat source returned by CodeGraph as already read and do not repeat it with a broad grep/read loop. Fall back to targeted source reads only when the index is missing, the language is unsupported, or the result reports missing/stale detail. CodeGraph never replaces source tests or CLI verification.

* `codegraph_context` — map task "fix mq-mcp brain writer paths" in `mq-mcp` first.
* `codegraph_node` — inspect `runtime/memory/obsidian_writer.py` only if the context result omitted it.
* `codegraph_node` — inspect `tests/test_obsidian_writer.py` only if the context result omitted it.

## Exclusions

* `irrelevant` — full README files
* `irrelevant` — old release notes
* `irrelevant` — unrelated UMS docs
