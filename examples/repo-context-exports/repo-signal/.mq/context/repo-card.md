---
schema: context-card.v1
repo: repo-signal
role: Structured repo readiness and inspection signal provider
updated_at: 2026-06-17T00:00:00Z
freshness: current
scope: repo
publishability: public-safe
---

# Context Card: repo-signal

## Role

Structured repo readiness and inspection signal provider.

## Owns

* repo health and readiness scoring
* structured inspection reports
* stable signal contracts such as `inspect.v1`
* doctor and report outputs for repo state
* evidence shaped for downstream memory export

## Does not own

* workflow orchestration
* MCP tool execution
* durable Obsidian curation
* context-pack generation
* source-repo release decisions

## Reads from

* target repo files
* repo configuration and metadata
* local project state
* readiness inputs requested by callers

## Writes to

* structured readiness signals
* `inspect.v1` outputs
* `doctor.v1` outputs
* `report.v1` outputs

## Use this card when

* task involves repo readiness or health scoring
* task needs structured inspection provenance
* task involves exporting repo signals into mqobsidian
* task needs to separate scoring from orchestration

## Avoid reading unless needed

* old release notes
* unrelated stack docs
* raw logs
* full repo README files
