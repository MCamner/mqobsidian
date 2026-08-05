---
type: hot-cache
system: mqobsidian
status: active
max_words: 500
tags: [hot, cache, active-context]
updated: 2026-08-04
owner:
links_to: [index]
---

# mqobsidian Hot

## Purpose
Systemets lilla arbetsminne. Bara det viktigaste.

## Current mission
Hålla MQ-stackens durable memory tunn, public-safe och billig för agenter att läsa.

## Current status
`mqobsidian` är kunskapslagret, inte exekverings- eller orchestrationlagret. Budgetkontraktet och CI-vakten mot stale exempel är mergade till `main`. En lokal writer kan nu lagra schema-giltiga routingutfall i append-only JSONL utan rå modelloutput; negativa utfall bevaras som evidence.

## Active blockers
- Inga bekräftade blockers.

## Most important facts
- Läs först [[../../memory/learn/agent/mqobsidian]] för repo-specifik agentkontext.
- Längre riktning finns i [[../../docs/roadmap-token-reduction]].
- `mq-agent` ska äga context selection, pack-generation och export.
- `mqobsidian` ska äga durable notes, schemas, templates och public-safe examples.
- `.mq/context-budgets.json` är publicerad budgetkälla och CI regenererar exemplen för att upptäcka drift.
- `--clean` tar nu bara bort exportens fem ägda filer och bevarar `task-pack.md` samt okända filer.
- Senaste effektmätningen visar 213 kontextrader mot 4114 breda baseline-rader (94,8 % minskning).
- Runtime truth hör hemma i källrepo eller verktyg, inte i vault-notes.
- `routing/outcomes.jsonl` är gitignorad durable evidence och behåller mq-agents outcome-kontrakt oförändrat.

## Immediate next actions
1. Håll [[index]] och denna hot-note små.
2. Håll repo-kortens `Current blockers` aktuella när blockerare är kända.
3. Samla verifierade routingutfall per task class utan att aktivera automatisk routing.

## Critical links
- [[index]]
- [[../../memory/learn/agent/mqobsidian]]
- [[../../docs/roadmap-token-reduction]]

## Update rule
Behåll bara det som behövs för nästa analys/beslut. Rensa aggressivt.
