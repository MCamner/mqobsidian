---
type: index
system: repo-signal
status: active
tags: [index, system]
updated: 2026-06-17
owner:
links_to: [hot]
---

# repo-signal Index

## Purpose

Navsidan för `repo-signal`: MQ-stackens strukturerade repo-readiness och inspection-signal.

## Current state

`repo-signal` omvandlar lokal repo-state till analysrapporter, publish-readiness signaler och stabila JSON-kontrakt för AI-agent workflows. Den är en signalproducent, inte workflow-orchestrator eller durable memory store.

## Current priorities

1. Bevara tydlig gräns: scoring/readiness i `repo-signal`, orchestration i `mq-agent`.
2. Bevara schema-provenance när signaler landar i `mqobsidian`.
3. Använd compact context cards före full repo-dokumentation.

## Key links

- [[hot]]
- [[../../docs/repo-signal-integration]]
- [[../../memory/context-cards/repo-signal-card]]
- [[../mq-agent/index]]

## Core notes

- [[../../docs/repo-signal-integration]] — mqobsidian-integrationsregel.
- [[../../memory/context-cards/repo-signal-card]] — compact repo-boundary card.

## Active risks

- Scoring/readiness kan blandas ihop med orchestration om `mq-agent`-gränsen tappas.
- Memory-exporter tappar värde om schema-provenance inte bevaras.
- Full repo-dokumentation kan bli onödig tokenkostnad för enkla signalfrågor.

## Open questions

- Vilka repo-signal outputs ska först bli återanvändbara context-pack-källor?
- Behövs ett separat commands-kort för repo-signal i vaulten?

## Recent changes

- 2026-06-17: `repo-signal-card.md` och `systems/repo-signal/` skapades som Phase 2 seed.

## Related systems

- [[../mq-agent/index]]
- [[../mqobsidian/index]]
- [[../mq-mcp/index]]

## Navigation rules

- Läs [[../../memory/context-cards/repo-signal-card]] först för ansvarsfördelning.
- Gå till källrepo eller `repo-signal` CLI för aktuell runtime/contract truth.
- Stoppa läsning när minsta användbara yta räcker.
