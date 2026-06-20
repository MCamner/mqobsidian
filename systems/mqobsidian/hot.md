---
type: hot-cache
system: mqobsidian
status: active
max_words: 500
tags: [hot, cache, active-context]
updated: 2026-06-20
owner:
links_to: [index]
---

# mqobsidian Hot

## Purpose
Systemets lilla arbetsminne. Bara det viktigaste.

## Current mission
Hålla MQ-stackens durable memory tunn, public-safe och billig för agenter att läsa.

## Current status
`mqobsidian` är kunskapslagret, inte exekverings- eller orchestrationlagret. Budgetkontraktet för context-export och CI-vakten mot stale exempel är mergade till `main`. `mq-agent context export` är lokalt implementerat och verifierat med 36 tester. Fem budgeterade `.mq/context/`-filer har rullats ut idempotent till nio repo; command-implementationen och övriga repo-exporter är ännu lokala.

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

## Immediate next actions
1. Håll [[index]] och denna hot-note små.
2. Landa `mq-agent context export` som en avgränsad ändring utan orelaterat cockpit-arbete.
3. Bestäm vilka repo-exporter som ska versionshanteras, sedan mät fler verkliga uppgifter.

## Critical links
- [[index]]
- [[../../memory/learn/agent/mqobsidian]]
- [[../../docs/roadmap-token-reduction]]

## Update rule
Behåll bara det som behövs för nästa analys/beslut. Rensa aggressivt.
