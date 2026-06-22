---
schema: context-card.v1
repo: mq-image-analyze
role: Visual perception layer that turns images into structured MQ context
updated_at: 2026-06-19T00:00:00Z
freshness: current
scope: repo
publishability: public-safe
---

# Context Card: mq-image-analyze

## Role

Visual perception layer that turns images into structured MQ context.

## Owns

* screenshot and diagram analysis
* structured visual context output
* vision backend mode selection
* perception-focused schemas and validation
* optional image generation as a secondary capability

## Does not own

* autonomous code or system changes
* MQ workflow orchestration
* durable memory storage
* MCP tool execution
* release or repo readiness decisions

## Reads from

* screenshots and visual artifacts
* local or cloud vision model outputs
* schema and validation inputs
* mq-agent or mq-mcp requests for visual context

## Writes to

* structured perception results
* visual analysis reports
* validated JSON context
* no source-repo changes by default

## Use this card when

* task involves screenshots, diagrams, or UI states
* task needs visual context for mq-agent or mq-mcp
* task must preserve the analyze-only boundary
* task compares local and cloud vision modes

## Avoid reading unless needed

* unrelated release notes
* non-visual repo docs
* raw images with sensitive content
* full MQ-stack architecture docs
