---
type: hot-cache
system: mqobsidian
status: active
max_words: 500
tags: [hot, cache, active-context]
updated: 2026-08-25
owner:
links_to: [index]
---

# mqobsidian Hot

## Purpose
Systemets lilla arbetsminne. Bara det viktigaste.

## Current mission
Hålla MQ-stackens durable memory tunn, public-safe och billig för agenter att läsa.

## Current status
`mqobsidian` är kunskapslagret, inte exekverings- eller orchestrationlagret. En experimentell, read-only NotebookLM consumer profile och `notebook-pack.v1` finns nu som public-safe kontraktsyta. Ingen adapter, export, sync eller automatisk routing är aktiverad.

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
- `.mq/notebooks.json` deklarerar en smal `mq-stack-intelligence`-allowlist; materialiserad output hör hemma i gitignorerade `.notebooklm/`.
- `notebook-pack.v1` kräver `revision.dirty`; consumer-repon får validera kontraktet men inte omdefiniera det (mq-agent vendorar en kopia — skuld 12f).
- `mq-agent` äger eventuell NotebookLM selection, pack-generation, routing och sync; se [[../../docs/notebooklm-bridge]].
- Runtime truth hör hemma i källrepo eller verktyg, inte i vault-notes.
- `routing/outcomes.jsonl` är gitignorad durable evidence och behåller mq-agents outcome-kontrakt oförändrat.

## Immediate next actions
1. Håll [[index]] och denna hot-note små.
2. Samla verkliga `feedback-signal.v1`-utfall innan selection quality används för beslut.
3. Samla verifierade routingutfall per task class utan att aktivera automatisk routing.
4. Verifiera NotebookLM-adapter och dataapproval innan någon verklig MQ-källa lämnar den lokala miljön.

## Critical links
- [[index]]
- [[../../memory/learn/agent/mqobsidian]]
- [[../../docs/roadmap-token-reduction]]
- [[../../docs/notebooklm-bridge]]

## Update rule
Behåll bara det som behövs för nästa analys/beslut. Rensa aggressivt.
