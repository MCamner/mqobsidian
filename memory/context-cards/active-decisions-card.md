---
schema: context-card.v1
repo: mq-decisions
role: Compact pointer to active MQ architecture decisions
updated_at: 2026-06-19T00:00:00Z
---

# Context Card: active decisions

## Role

Compact pointer to active MQ architecture decisions.

## Owns

* decision lookup hints
* current architecture constraints
* stable boundaries between MQ layers
* reminders to verify decisions before broad changes

## Does not own

* live code behavior
* runtime state
* release readiness
* source-repo tests
* permanent duplication of ADR content

## Reads from

* durable decision notes
* system index pages
* stack truth summaries
* source repos when decisions depend on current behavior

## Writes to

* context packs
* decision summaries
* active constraint lists
* no source repo files directly

## Use this card when

* task may change architecture boundaries
* task needs ADR awareness
* task crosses memory, runtime, signal, and operator layers
* task risks duplicating logic across repos

## Avoid reading unless needed

* full ADR archive
* old design drafts
* stale research notes
* unrelated decision history
