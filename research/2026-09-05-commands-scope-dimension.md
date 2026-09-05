---
type: research
system: mqobsidian
status: open
priority: low
confidence: medium
research_tag: research-node
source: memory/commands/MODEL.md, memory/commands/CURATION.md, memory/commands/patterns/patterns.jsonl, memory/commands/build_views.py
tags: [research-node, command-pattern-library, model, scope]
updated: 2026-09-05
links_to: [systems/mqobsidian/index, memory/commands/MODEL, memory/commands/CURATION]
owner:
validation_state: unverified
---

# Research Node: Är `repo_scope` rätt dimension i command-pattern-modellen?

## Problem

Ett kandidatmönster från mq-agent-evidensarbetet (`evidence-baseline-check`) har inget
ärligt värde i `repo_scope`. Dess verkliga objekt är mq-agent-runtimen och dess
evidenslager — inte vaulten, och inte något portabelt repo-mönster. Frågan är om
modellen saknar ett enum-värde eller en **dimension**.

## Why this exists

Ett enda kandidatmönster är inte evidens för en modelländring. Noden håller frågan
öppen i stället för att antingen tvinga in mönstret som `generic` eller vidga enumet
på tunn grund.

## Observed signals (verifierat 2026-09-05)

- `MODEL.md:107` — `repo_scope` dokumenteras som enum `mqobsidian | generic`.
- `patterns.jsonl` — 15 mönster fördelade 13 `mqobsidian` / 2 `generic`. Inget tredje värde.
- Inget JSON-schema validerar `repo_scope`; `schemas/` saknar en command-pattern-kontrakt.
- `build_views.py:187,236` grupperar dynamiskt på `repo_scope`, så ett nytt värde bryter
  inget — men `build_views.py:55` ger `generic` +1.0 i rankningen, så ett verktygsspecifikt
  mönster hamnar systematiskt under.
- `CURATION.md` kräver en portabel `command_template` som golv. Två närliggande kandidater
  (`semantic-observation-triage`, `quality-era-boundary-check`) är resonemangsmönster utan
  kommando och avvisas därför av modellen — de ligger nu i `learn/` i stället.

## Known facts

- Biblioteket beskriver sig självt som "14 patterns for `mqobsidian`" (LIBRARY.md) — det är
  byggt som ett vault-verktyg, inte som ett stack-brett register.
- `evidence-baseline-check` har ett användningstillfälle. CURATION kräver ≥2 sessioner
  eller ≥2 tasks för "high reuse", och ett authored-only mönster går ändå bara in som
  `experimental`.

## Unknowns

- Är behovet "ett enum-värde till" eller "en separat dimension"? Kandidater:
  `target_scope` (vad kommandot verkar på) skilt från `tool_scope` (vilket verktyg som krävs).
- Om `generic` betyder "portabelt mellan repon", vad betyder då ett kommando som är
  portabelt mellan *sessioner* men bundet till ett verktyg?
- Ska rankningsbonusen för `generic` finnas kvar om biblioteket blir stack-brett?

## Hypotheses

1. `repo_scope` är rätt dimension och saknar bara värden — billigast, men löser inte
   fallet där ett mönster kräver ett installerat verktyg snarare än ett visst repo.
2. Modellen behöver skilja på *var kommandot körs* och *vad det kräver installerat*.
3. Behovet är inbillat: verktygsspecifika driftsekvenser hör hemma i respektive repos
   egen dokumentation, inte i vaultens command-bibliotek.

## Evidence to collect

- [ ] Ett andra naturligt användningstillfälle av `evidence-baseline-check` i en riktig session
- [ ] Om fler mq-stack-kandidater dyker upp (mq-mcp, repo-signal) — en enda kandidat är brus
- [ ] Om någon konsument (mqlaunch, FAS 7) faktiskt frågar efter verktygsspecifika mönster
- [ ] Om rankningen straffar icke-generic mönster på ett sätt som gör dem osynliga

## Validation path

1. Vänta på verklig upprepad användning. Ingen modelländring på ett kandidatmönster.
2. Vid andra tillfället: avgör om det är ett värde eller en dimension som saknas.
3. Först då: MODEL.md + patterns.jsonl + views rebuild i en PR.

## Decision rule

Öppnas igen när ett verktygsspecifikt kommandomönster har **två oberoende**
användningstillfällen loggade, eller när en andra mq-stack-kandidat uppstår. Utan det
förblir noden `open` och modellen orörd.

## Related notes

- [[memory/commands/MODEL]]
- [[memory/commands/CURATION]]

## Final resolution

Lämnas tom tills problemet är verifierat.
