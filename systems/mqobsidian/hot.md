---
type: hot-cache
system: mqobsidian
status: active
max_words: 500
tags: [hot, cache, active-context]
updated: 2026-08-27
owner:
links_to: [index]
---

# mqobsidian Hot

## Purpose
Systemets lilla arbetsminne. Bara det viktigaste.

## Current mission
Hålla MQ-stackens durable memory tunn, public-safe och billig för agenter att läsa.

## Current status
`mqobsidian` är kunskapslagret, inte exekverings- eller orchestrationlagret. NotebookLM-spåret är stängt efter två mätningar; `notebook-pack.v1` och exportören står kvar som exportinfrastruktur utan konsument. Ingen adapter, sync eller automatisk routing är aktiverad.

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
- `notebook-pack.v1` kräver `revision.dirty`; consumer-repon får validera kontraktet men inte omdefiniera det (mq-agent vendorar en kopia).
- **Phase 12 är stängd.** 12g:s rättvisa omtest gav 17/40 mot 40 (kompakt MQ) och 39 (MQ+CodeGraph) — sämre än 12c trots 21x materialet. NotebookLM är omklassificerad till *optional export capability*, inte provider; 12d och 12e är stängda, 12f betalas inte. Kontrakt, exportör och grindar behålls som exportinfrastruktur.
- `mq-agent` äger eventuell NotebookLM selection, pack-generation, routing och sync; se [[../../docs/notebooklm-bridge]]. Gitignorerad varaktig minnesyta exporteras aldrig — publiceringsgränsen är exportgränsen.
- Runtime truth hör hemma i källrepo eller verktyg, inte i vault-notes.
- `routing/outcomes.jsonl` är gitignorad durable evidence och behåller mq-agents outcome-kontrakt oförändrat. Ytan fylls inte automatiskt: `mq-agent` skriver till `~/.mq-agent/route-outcomes.jsonl`, och `scripts/record-routing-outcome.py` måste köras för att föra över posterna hit.

## Immediate next actions
1. Håll [[index]] och denna hot-note små.
2. Samla verkliga `feedback-signal.v1`-utfall innan selection quality används för beslut.
3. Samla verifierade routingutfall per task class utan att aktivera automatisk routing.
4. Ta ägarskapsdivergensen i [[../../ROADMAP]]: context selection körs i detta repo trots att regeln lägger den hos mq-agent, och repots `--clean` gör `rmtree` medan hot:32 beskriver mq-agents säkra variant.

## Critical links
- [[index]]
- [[../../memory/learn/agent/mqobsidian]]
- [[../../docs/roadmap-token-reduction]]
- [[../../docs/notebooklm-bridge]]

## Update rule
Behåll bara det som behövs för nästa analys/beslut. Rensa aggressivt.
