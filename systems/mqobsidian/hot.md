---
type: hot-cache
system: mqobsidian
status: active
max_words: 500
tags: [hot, cache, active-context]
updated: 2026-08-21
owner:
links_to: [index]
---

# mqobsidian Hot

## Purpose
Systemets lilla arbetsminne. Bara det viktigaste.

## Current mission
Hålla MQ-stackens durable memory tunn, public-safe och billig för agenter att läsa.

## Current status
`mqobsidian` är kunskapslagret, inte exekverings- eller orchestrationlagret. Release-branchen innehåller nu både stackövergripande `memory-query.v1` och en eval för selection quality från `feedback-signal.v1`. Reduktion och kvalitet mäts separat; automatisk routing eller publicering är inte aktiverad.

## Active blockers
- Inga bekräftade blockers.

## Most important facts
- Läs först [[../../memory/learn/agent/mqobsidian]] för repo-specifik agentkontext.
- Längre riktning finns i [[../../docs/roadmap-token-reduction]].
- `mq-agent` ska äga context selection, pack-generation och export.
- `mqobsidian` ska äga durable notes, schemas, templates och public-safe examples.
- `.mq/context-budgets.json` är publicerad budgetkälla och CI regenererar exemplen för att upptäcka drift.
- `--clean` tar nu bara bort exportens fem ägda filer och bevarar `task-pack.md` samt okända filer.
- Aktuell orienteringsmätning visar 222 kontextrader mot 4797 breda baseline-rader (95,4 % minskning); CodeGraph-mätningar redovisas separat i [[../../docs/context-effect]].
- `scripts/eval-retrieval.py` mäter precision, recall och F1 från lokala feedback-signaler utan att ändra kontrakt eller publicera rådata.
- `memory-query.v1` kan ange flera `repositories`; `repository` är fortsatt det frågande repot.
- Runtime truth hör hemma i källrepo eller verktyg, inte i vault-notes.
- `routing/outcomes.jsonl` är gitignorad durable evidence och behåller mq-agents outcome-kontrakt oförändrat.

## Immediate next actions
1. Håll [[index]] och denna hot-note små.
2. Samla verkliga `feedback-signal.v1`-utfall innan selection quality används för beslut.
3. Samla verifierade routingutfall per task class utan att aktivera automatisk routing.

## Critical links
- [[index]]
- [[../../memory/learn/agent/mqobsidian]]
- [[../../docs/roadmap-token-reduction]]

## Update rule
Behåll bara det som behövs för nästa analys/beslut. Rensa aggressivt.
