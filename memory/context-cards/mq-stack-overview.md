---
schema: context-card.v1
repo: mq-stack
role: Compact responsibility map for the MQ stack
updated_at: 2026-06-19T00:00:00Z
freshness: current
scope: cross-repo
publishability: public-safe
---

# Context Card: mq-stack

## Role

Compact responsibility map for the MQ stack.

## Owns

* repo boundary orientation
* cross-repo responsibility hints
* small first-read stack context
* links between runtime, memory, signal, and operator layers

## Does not own

* live runtime truth
* source-repo implementation details
* release decisions
* durable note curation
* tool execution

## Reads from

* individual repo context cards
* stack truth summaries
* current hot and index notes
* verified repo metadata

## Writes to

* generated context packs
* compact stack summaries
* routing hints for agents
* no source repo files directly

## Use this card when

* task crosses more than one MQ repo
* task needs quick owner boundaries
* task should avoid reading every README
* task involves context-pack generation

## Avoid reading unless needed

* full stack history
* old roadmap drafts
* release archives
* raw review dumps
