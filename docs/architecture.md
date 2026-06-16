# mqobsidian Architecture

`mqobsidian` is the long-term memory layer for the MQ stack.

## Purpose

It stores durable knowledge that should survive beyond a single run, terminal
session, or repo review:

* architectural decisions
* reviewed findings
* truth exports
* learning records
* operational knowledge summaries

## Boundary

`mqobsidian` is not:

* an execution runtime
* a planner
* a shell wrapper
* a live source of truth for repo or endpoint state

Those responsibilities stay with the operating repos:

* `mq-agent` orchestrates
* `mq-mcp` executes and validates
* `repo-signal` scores and inspects
* `mq-hal` summarizes operator state
* `mq-ums` owns enterprise endpoint workflows

## Data flow

```text
repo / endpoint / screenshot / runtime
-> structured signal
-> review or decision
-> sanitized export
-> mqobsidian durable memory
-> future context for operators and agents
```

## Public-safe repo scope

The public repo should contain:

* schemas
* docs
* templates
* sanitized examples
* validation scripts

The live private vault may still contain additional local-only material that is
not committed.
