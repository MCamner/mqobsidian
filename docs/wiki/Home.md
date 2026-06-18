# mqobsidian Wiki

`mqobsidian` is the local-first durable memory layer for the MQ stack.

This wiki is synced from the current repository docs and compact stack truth
notes. The repository remains the source of truth for schemas, templates,
examples, and validation scripts.

## Core Pages

- [Roadmap](Roadmap)
- [Memory Model](Memory-Model)
- [Truth Export](Truth-Export)
- [Context Packs](Context-Packs)
- [Integrations](Integrations)
- [MQ Wiki Status](MQ-Wiki-Status)
- [Changelog](Changelog)

## Role in the MQ Stack

```text
signal -> review -> decision -> memory -> next action
```

Responsibility split:

- `mq-agent` orchestrates workflows and exports stack truth.
- `mq-mcp` executes bounded tools and owns runtime/review contracts.
- `repo-signal` scores repo health and readiness.
- `mq-hal` presents operator-facing summaries.
- `mqobsidian` stores durable memory, schemas, templates, and compact context.

## Source of Truth

The repository docs remain authoritative:

- `README.md` for product status and public-safe scope.
- `docs/memory-model.md` for durable memory layers.
- `docs/truth-export.md` for export rules.
- `docs/roadmap-token-reduction.md` for the context-pack roadmap.
- `schemas/` and `templates/` for portable contracts.

## Boundary

`mqobsidian` does not execute workflows, own runtime gates, publish releases, or
replace `mq-agent`, `mq-mcp`, or `mq-hal`.
