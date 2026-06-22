---
schema: context-pack.v1
target: codex
task: Short task description
generated_at: 2026-01-01T00:00:00Z
repo: mq-mcp
summary: Short summary of the minimum context needed for this task
---

# Task Context Pack

## Relevant repos

* mq-mcp

## Relevant files

* docs/example.md

## Relevant decisions

* Durable memory lives in mqobsidian; runtime truth stays in source repos.

## Notes

* Prefer local memory query before broad repo scans.

## Exclusions

Each entry is `kind` — `item`: reason. `kind` is one of `forbidden` (never pull
into the pack), `fallback` (read only if the context above is insufficient), or
`irrelevant` (not needed for this task). The legacy flat `do_not_read` list is
still accepted and means `irrelevant`.

* `irrelevant` — full README
* `fallback` — archived release notes: read only if the context above is thin
* `forbidden` — unrelated MQ repos: never pull into this pack
