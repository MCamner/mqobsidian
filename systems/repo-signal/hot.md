---
type: hot-cache
system: repo-signal
status: active
max_words: 500
tags: [hot, cache, active-context]
updated: 2026-06-17
owner:
links_to: [index]
---

# repo-signal Hot

## Purpose

Systemets lilla arbetsminne. Bara det viktigaste.

## Current mission

Ge MQ-stacken strukturerade repo-signaler för readiness, inspection och AI-agent workflows.

## Current status

`repo-signal` är en Python CLI på version 1.4.0. Den producerar analysrapporter, publish-readiness signaler och maskinläsbara JSON-kontrakt för downstream-konsumenter som `mq-agent`, `mq-mcp` och `mqobsidian`.

## Active blockers

- Inga bekräftade blockers i mqobsidian-minnet.

## Most important facts

- Stabil command surface inkluderar `analyze`, `inspect`, `doctor`, `publish-checklist`, `report`, `suggest` och `repoaware`.
- Stabil JSON-yta inkluderar `inspect.v1`, `doctor.v1`, `report.v1` och `suggest.v1`.
- Export packs inkluderar `symbol_index.v1`, `callgraph.v1`, `repo_summary.v1` och `risk_map.v1`.
- `repo-signal` äger scoring/readiness-signaler; `mq-agent` äger orchestration.
- Bevara schema-provenance när signaler exporteras till `mqobsidian`.

## Immediate next actions

1. Använd [[../../memory/context-cards/repo-signal-card]] som första kort för repo-boundary.
2. Håll [[index]] liten och fri från full README-dubbling.
3. Lägg till task packs först när en konkret repo-signal-task kräver det.

## Critical links

- [[index]]
- [[../../docs/repo-signal-integration]]
- [[../../memory/context-cards/repo-signal-card]]

## Update rule

Behåll bara det som behövs för nästa analys/beslut. Rensa aggressivt.
