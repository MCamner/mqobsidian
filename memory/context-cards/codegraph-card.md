---
schema: context-card.v1
repo: codegraph
role: Local source-code intelligence layer for MQ repos
updated_at: 2026-06-21T00:00:00Z
freshness: current
scope: repo
publishability: public-safe
---

# Context Card: codegraph

## Role

Local source-code intelligence layer for MQ repos.

## Owns

* source-code symbol index
* code search across local source
* callers and callees lookup
* source impact and blast-radius analysis
* local `.codegraph/` database

## Does not own

* MQ durable memory
* context-pack generation
* repo responsibility map
* runtime truth
* review execution
* public-safe exports

## Reads from

* local source files in an initialized repo
* the `.codegraph/` index for that repo

## Writes to

* the local `.codegraph/` database only
* nothing committed or exported

## Use this card when

* the task asks how code flows
* the task needs callers or callees
* the task asks impact or blast radius
* the agent would otherwise grep or read many files
* a context pack names exact files or symbols to inspect

## Avoid reading unless needed

* an uninitialized repo with no `.codegraph/`
* durable architecture memory questions
* historical decision questions
* questions needing current test execution
* any CodeGraph result showing a staleness warning
