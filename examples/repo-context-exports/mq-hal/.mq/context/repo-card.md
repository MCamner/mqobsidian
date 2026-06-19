---
schema: context-card.v1
repo: mq-hal
role: Operator-facing HAL command router for the MQ stack
updated_at: 2026-06-19T00:00:00Z
---

# Context Card: mq-hal

## Role

Operator-facing HAL command router for the MQ stack.

## Owns

* natural-language operator command routing
* safe JSON-intent handling through a Python allowlist
* operator summaries for stack, release, repo, and CI state
* `mqlaunch hal` command surface integration
* local HAL-style dashboard and brief outputs

## Does not own

* MQ-stack runtime truth production
* uncontrolled shell execution from model output
* durable Obsidian memory
* MCP tool implementation
* repo health scoring internals

## Reads from

* mq-agent stack and release outputs
* repo-signal readiness signals
* local mq-hal config and allowlist
* MQ repo metadata when commands target a repo

## Writes to

* operator-facing terminal output
* local HAL logs or status files
* command routing decisions
* no durable MQ memory by default

## Use this card when

* task involves operator UX or HAL command routing
* task involves `mqlaunch hal`
* task needs the observe/recommend/coordinate boundary
* task checks that models cannot execute shell directly

## Avoid reading unless needed

* old release notes
* full dashboard design history
* unrelated source-repo docs
* raw model transcripts
