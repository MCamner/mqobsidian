---
type: hot-cache
system: mqobsidian
status: active
max_words: 500
tags: [hot, cache, active-context]
updated: 2026-06-17
owner:
links_to: [index]
---

# mqobsidian Hot

## Purpose
Systemets lilla arbetsminne. Bara det viktigaste.

## Current mission
Hålla MQ-stackens durable memory tunn, public-safe och billig för agenter att läsa.

## Current status
`mqobsidian` är kunskapslagret, inte exekverings- eller orchestrationlagret. Token-reduction MVP är verifierad med `.mq/context/task-pack.md` för `fix mq-mcp brain writer paths`; nästa nytta är bättre agent-routing, små context cards och hård budgetkontroll.

## Active blockers
- Inga bekräftade blockers.

## Most important facts
- Läs först [[../../memory/learn/agent/mqobsidian]] för repo-specifik agentkontext.
- Längre riktning finns i [[../../docs/roadmap-token-reduction]].
- `mq-agent` ska äga context selection, pack-generation och export.
- `mqobsidian` ska äga durable notes, schemas, templates och public-safe examples.
- Runtime truth hör hemma i källrepo eller verktyg, inte i vault-notes.

## Immediate next actions
1. Håll [[index]] och denna hot-note små.
2. Lägg små context cards för återkommande agentfrågor.
3. Stärk budget- och schema-validering för agent-read surfaces.

## Critical links
- [[index]]
- [[../../memory/learn/agent/mqobsidian]]
- [[../../docs/roadmap-token-reduction]]

## Update rule
Behåll bara det som behövs för nästa analys/beslut. Rensa aggressivt.
