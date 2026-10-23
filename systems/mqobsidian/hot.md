---
type: hot-cache
system: mqobsidian
status: active
max_words: 500
tags: [hot, cache, active-context]
updated: 2026-10-23
owner:
links_to: [index]
---

# mqobsidian Hot

## Purpose
Systemets lilla arbetsminne. Bara det viktigaste.

## Current mission
Hålla MQ-stackens durable memory tunn och public-safe, och äga de execution-
och routingkontrakt senare lager läser.

## Current status
`v0.4.0` (2026-09-11) är en kontraktsgrund, inte levererad Execution
Intelligence: kontrakten är grindade och fallback recording är stängd (#134),
men aktiv-vs-shadow-divergens och policylagret är öppna.
Execution- och routingkontrakten är kanoniska här och registret hålls mot
`schemas/` i båda riktningar. Phase 12 och ownership-spåret (DEC-005) är
stängda. NotebookLM är fortfarande opt-in och valfri, inte provider.

## Active blockers
- Inga bekräftade blockers.

## Most important facts
- `mq-agent` äger context selection, pack-generation, runtime-writer och CLI.
  `mqobsidian` äger schemas, durable notes, templates och public-safe examples.
- `.mq/repo-contract.json` deklarerar 33 kontrakt. Ett odeklarerat schema äger
  inget (#103) — registret och `schemas/` grindas mot varandra.
- `mq.model-route-outcome.v1` är kanoniskt här, inte löst från ett sibling
  `mq-agent`-checkout; mq-agent vendorar en grindad kopia.
- En route är en exekveringsstrategi, inte en modell (ADR-010). `application`
  (`advisory | shadow | applied`) skiljer råd från tillämpning och route
  readiness räknar bara `applied`. `route` på `mq.execution-outcome.v1` är
  deprekerad; applied-route-fakta hör till routingkontraktet.
- `execution_run_id` korrelerar routingobservation med exekvering, ovillkorligt i v1.
- `runtime_fingerprint` är valfri och additiv (DEC-006). Frånvaro betyder att
  proveniens inte observerades — annan fakta än `identity quality: unknown`.
- `mq.execution-outcome.v1` har mätt fallback (#134), mätt `completeness` (#140)
  och task class `repo-review` (#136), additivt under DEC-006. Frånvaro = omätt.
- Agent view för mqobsidian är versionerad (DEC-007, #139): byggd bara från hot/index.
- `mq.notebook-corpus-index.v1` (#114) är kanoniskt här; NotebookLM är opt-in.
- `mq.semantic-refresh.v1` (#124) är kanoniskt här: identitet är repo +
  artifact_type, och exakt en aktiv generation per identitet i auktoritativa stores.
- Skill selection har kontrakt (`mq.skill-profile.v1`, `mq.skill-route.v1`,
  `skill-selection-vocabulary.v1`); mq-agent äger exekveringen.
- `.mq/context-selection-vocabulary.json` (DEC-005) och `.mq/context-budgets.json`
  (`context-budget.v1`) är publicerade kontraktskällor; ingen håller en egen kopia.
- Evidensläge 2026-10-23: 163 poster, vault synkad med mq-agents store. De 32
  `applied` (09-01 → 10-18) delar ett `decision_id`, alla `docs-review`:
  `deterministic-local` 14 PASS; `local-shadow` 7 PASS / 7 FAIL / 4 UNAVAILABLE.
- `docs-review`: readiness `AWAITING_OPERATOR_APPROVAL` (min 14/route, 48 d);
  divergens i aktuell era 1/route, `INSUFFICIENT_EVIDENCE` (10/route, 14 d krävs).
- Write-gaten är route-medveten: `deterministic-local` kör ingen modellinferens,
  så `model_output_received: false` är enda sanna värdet på en PASS, och `true`
  avvisas för den routen.
- Omätta räknare är okända, inte noll.
- Runtime truth hör hemma i källrepo eller verktyg, inte i vault-notes.

## Immediate next actions
1. Operatörsbeslut om `docs-review`-readiness; eligibility tillåter granskning, aldrig automatisk routing.
2. Divergens kräver fler riktiga körningar i aktuell era; inga körningar för att höja räknaren.
3. Behandla 30 körningar, 2 routes, 14 dagar och 10 per route som hypotes, inte som aktiveringsregel.

## Critical links
- [[index]]
- [[../../memory/learn/agent/mqobsidian]]
- [[../../docs/ROUTING_OUTCOMES]]
- [[../../docs/skill-selection]]
- [[../../docs/roadmap-token-reduction]]

## Update rule
Behåll bara det som behövs för nästa analys/beslut. Rensa aggressivt.
