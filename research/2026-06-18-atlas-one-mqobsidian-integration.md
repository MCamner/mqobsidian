---
type: research
system: atlas-one
status: open
priority: medium
confidence: high
research_tag: research-node
source: atlas-one/src/AtlasServer.java, mq-agent/mq_agent/main.py, atlas-one/CHANGELOG.md
tags: [research-node, integration, token-reduction]
updated: 2026-06-18
links_to: [systems/atlas-one/index, systems/mqobsidian/index, docs/roadmap-token-reduction]
owner:
validation_state: validated
---

# Research Node: Grunda atlas-one i mqobsidian-minnet (läs, inte bara skriv)

## Problem

atlas-one (Atlas Studio) **skriver** redan till mqobsidian (`Save to brain` → `decisions/`)
och exekverar via mq-agent, men **läser inte** från durable memory innan den genererar
prompts eller exekverar. Frågan: hur kopplar vi atlas-one som *konsument* av mqobsidian
(agent-views, hot/index, context-pack.v1) på minsta, mest bevisande sätt — och vad måste
verifieras i mq-agent/atlas-one innan write-back utökas?

## Why this exists

Fångar integrationsdesignen utan att gissa om mq-agent-kontrakt som inte är verifierade.

## Observed signals (verifierat 2026-06-18)

- `AtlasServer.java:217–228` — `/api/execute` mappar mode → `mq-agent` (`review repo`,
  `audit`, `signal`, `plan`, alla `--json`); ohanterade modes → `plan` (fallback).
- `AtlasServer.java:233–265` — `/api/decide` ("Save to brain") kör `mq-agent decide <title>
  --decision …`.
- `CHANGELOG.md` — `Save to brain` routar reasoning-outputs till `decisions/` i second brain;
  runtime portabel via `MQ_ROOT`.
- Prompt-generering läser statiskt bibliotek (`web/prompts.json`, `docs/prompts/`), inte vaulten.
- Packs ("mq-mcp Safety", "Release Readiness") är handskrivna markdown, inte vault-härledda.

## Verified findings (2026-06-18)

- **`decide`-kontrakt:** `mq-agent decide <title>` kräver `--context` + `--decision` +
  `--rationale` (alla icke-tomma) **och `--approve`** (Class C write); utan `--approve`
  blockeras och exit:ar 1 (`mq-agent/mq_agent/main.py:1293–1316`). Skriver via MCP-verktyget
  `brain_record_decision` → `mqobsidian/decisions/` (main.py:1318–1327).
- **BUG — "Save to brain" är blockerad:** atlas-ones DecideHandler bygger kommandot med
  `--context/--decision/--rationale/--tag/--json` men **utan `--approve`**
  (`atlas-one/src/AtlasServer.java:262–269`). Varje sparning träffar safety-gaten och
  misslyckas. Trolig drift: `decide` fick `--approve`-gate efter att anropet skrevs.
- **Execute-path är read-only/dry-run:** `review`/`signal`/`plan` (`--json`) och `audit`
  (`--dry-run --json`) kräver inte `--approve` (AtlasServer.java:217–228) → den vajern är inte blockerad.

## Known facts

- decide-vajern *finns* men är funktionellt bruten (saknar `--approve`); execute-vajern fungerar.
- mqobsidian har nu steg-0-agentvyer + hot/index för 10 system och en `context-pack.v1`-generator.
- atlas-one läser i dag ingen vault-yta före generering/exekvering.

## Unknowns

- Om `mq-agent` redan grundar `review/audit/signal/plan` i vault-minne, eller om grundning
  måste ske i atlas-one före anrop.
- Om `generate-context-pack.py` kan anropas headless av atlas-one (in/utdata-kontrakt).
- Repo-namn-derivation: är basename av repo-path alltid == `systems/<repo>`-namnet?

## Hypotheses

0. **Fixa den brutna vajern först (minst, mest bevisande):** lägg `--approve` i atlas-ones
   DecideHandler-kommando → "Save to brain" skriver faktiskt till `decisions/`. Verifiera sedan
   att noten landar. Detta gör en *befintlig* loop fungerande innan vi bygger nytt.
1. **Läs-grundning:** läs `$MQ_ROOT/mqobsidian/memory/learn/agent/<repo>.md` i `/api/execute`
   och prependa till goal-kontexten → grundad execution för en filläsning.
2. **Pack-konsument:** för analysis/architecture-modes, generera `context-pack.v1` och injicera
   i ChatGPT-handoff → atlas-one blir proof #2 för token-reduktions-MVP:n.
3. **Vault-härledda packs:** generera Release Readiness / `<repo>` Safety-packs från
   `systems/<repo>/index.md` + repo-signal istället för handskrivet → aldrig stale.
4. **Rikare write-back:** `/api/decide` → rätt note-typ (summary/research) via templates, och
   `agent-views rebuild --system <repo>` efter skrivning (annars bryts steg-0-invariansen).

## Evidence to collect

- [ ] Kodreferenser: `mq-agent decide`-implementation i mq-agent-repot
- [ ] Kodreferenser: hur `review/audit/signal/plan` ev. läser vault i mq-agent
- [ ] `generate-context-pack.py` in/utdata-kontrakt för headless-anrop
- [ ] Verifiering i drift: kör `/api/execute` mot ett repo med och utan steg-0-prepend, jämför
- [ ] Bekräfta repo-path-basename ↔ `systems/<repo>`-namn-mappning

## Validation path

1. ~~Verifiera `mq-agent decide`- och execute-kontrakten i mq-agent-källan.~~ **Klart 2026-06-18** — se Verified findings.
2. ~~**Fixa hypotes 0:** lägg `--approve` i AtlasServer DecideHandler, kör "Save to brain", bekräfta att en note skapas i `decisions/`.~~ **Klart 2026-06-18** — `--approve` tillagt (`AtlasServer.java:268`), omkompilerat, server omstartad (PID 54858), `POST /api/decide` → `{"ok":true}` skrev `decision.v1`-note via `brain_record_decision`; test-note bekräftad och borttagen.
3. ~~Bygg hypotes 1 (steg-0-prepend) som minsta läs-diff.~~ **Klart 2026-06-18** — `groundGoal`/`readAgentView` i `AtlasServer.java`; bara `plan`-grenen grundas (review/audit/signal läser repot direkt). Verifierat: `plan` mot mq-mcp injicerar agentvyn i kommandot (`ok:true`); `path:"."` utan vy → oförändrat mål (fail-safe, ingen regression). Bekräftat att `mq-agent plan` (main.py:128–148) annars är helt ogrundad.
4. Om #3 bär: bygg hypotes 2 (context-pack i handoff) och dokumentera token-skillnad i roadmapen.
5. Adressera rikare write-back sist — kräver agent-view-rebuild-trigger efter skrivning.

## Decision rule

När hypotes 0 (fungerande write) och hypotes 1 (läs-grundning) är verifierade i drift →
markera `validated`. Markera `discarded` om mq-agent redan grundar internt och atlas-side-grundning visar sig onödig.

## Related notes

- [[systems/atlas-one/index]]
- [[systems/mqobsidian/index]]
- [[docs/roadmap-token-reduction]]

## Final resolution

**Validerat 2026-06-18.** Två vajrar landade i drift:
(1) "Save to brain" fixad — `decide` saknade `--approve`, nu tillagt; POST skriver `decision.v1` till `decisions/`.
(2) `plan`-grundning — atlas-one läser nu `memory/learn/agent/<repo>.md` och prependar till goal innan `mq-agent plan`, fail-safe vid miss.
Kvar som framtida arbete (egna noder vid behov): hypotes 2 (context-pack i ChatGPT-handoff, token-mätning) och hypotes 3 (vault-härledda packs). Vault-side-grundning visade sig **inte** redundant — `mq-agent plan` läser inget minne självt.
