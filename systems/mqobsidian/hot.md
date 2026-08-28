---
type: hot-cache
system: mqobsidian
status: active
max_words: 500
tags: [hot, cache, active-context]
updated: 2026-08-28
owner:
links_to: [index]
---

# mqobsidian Hot

## Purpose
Systemets lilla arbetsminne. Bara det viktigaste.

## Current mission
Hålla MQ-stackens durable memory tunn och public-safe, samt ge execution
intelligence en stabil kontraktsgrund utan att flytta runtime till vaulten.

## Current status
Phase 12 och dess ownership-, CodeGraph mismatch- och contract-integrity-spår är
stängda. `mq.execution-outcome.v1` är kontrakterat och validerat. mq-agent PR
#206 är mergead med writer, execution report/compare, route readiness och
storleksrotation. Aktiv-vs-shadow-divergens och verklig observationsperiod
återstår. NotebookLM och automatisk routing är fortsatt stängda.

## Active blockers
- Inga bekräftade blockers.

## Most important facts
- Läs först [[../../memory/learn/agent/mqobsidian]] för repo-specifik agentkontext.
- `mq-agent` äger context selection, pack-generation, runtime-writer och CLI.
- `mqobsidian` äger durable notes, schemas, templates och public-safe examples.
- `mq.execution-outcome.v1` beskriver route/model/context, duration, status,
  fallback och retries. Quality samt usage är valfria när signalerna saknas.
- `.mq/context-budgets.json` är publicerad budgetkälla och CI regenererar exemplen för att upptäcka drift.
- `.mq/context-selection-vocabulary.json` är publicerad selection-vokabulär (DEC-005). Konsumenter läser den; ingen får hålla en egen kopia, och det finns medvetet ingen fallback.
- `--clean` tar nu bara bort exportens fem ägda filer och bevarar `task-pack.md` samt okända filer.
- Aktuell orienteringsmätning visar 222 kontextrader mot 4797 breda baseline-rader (95,4 % minskning); CodeGraph-mätningar redovisas separat i [[../../docs/context-effect]].
- `scripts/eval-retrieval.py` mäter precision, recall och F1 från lokala feedback-signaler utan att ändra kontrakt eller publicera rådata.
- `memory-query.v1` kan ange flera `repositories`; `repository` är fortsatt det frågande repot.
- `.mq/notebooks.json` deklarerar en smal `mq-stack-intelligence`-allowlist; materialiserad output hör hemma i gitignorerade `.notebooklm/`.
- `notebook-pack.v1` kräver `revision.dirty`; consumer-repon får validera kontraktet men inte omdefiniera det (mq-agent vendorar en kopia).
- **Phase 12 är stängd.** NotebookLM är *optional export capability*, inte
  provider; kontrakt och grindar behålls som exportinfrastruktur.
- `mq-agent` äger eventuell NotebookLM selection, pack-generation, routing och sync; se [[../../docs/notebooklm-bridge]]. Gitignorerad varaktig minnesyta exporteras aldrig — publiceringsgränsen är exportgränsen.
- Runtime truth hör hemma i källrepo eller verktyg, inte i vault-notes.
- `routing/outcomes.jsonl` är gitignorad durable evidence och behåller mq-agents outcome-kontrakt oförändrat. Ytan fylls inte automatiskt: `mq-agent` skriver till `~/.mq-agent/route-outcomes.jsonl`, och `scripts/record-routing-outcome.py` måste köras för att föra över posterna hit.

## Immediate next actions
1. Samla verkliga execution outcomes och kontrollera vilka runtimes som faktiskt
   mäter route, context, retries och fallbacks utan påhittade nollor.
2. Lägg till aktiv-vs-shadow-divergens först när samma task class kan jämföras.
3. Behandla 30 körningar, 2 routes och 14 dagar som en
   hypotes, inte som automatisk aktiveringsregel.

## Critical links
- [[index]]
- [[../../memory/learn/agent/mqobsidian]]
- [[../../docs/roadmap-token-reduction]]
- [[../../docs/notebooklm-bridge]]

## Update rule
Behåll bara det som behövs för nästa analys/beslut. Rensa aggressivt.
