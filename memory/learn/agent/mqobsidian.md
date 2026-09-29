---
type: agent-view
system: mqobsidian
generated: 2026-09-29
generator: mq-agent agent-views rebuild
sources: [systems/mqobsidian/hot.md, systems/mqobsidian/index.md, memory/learn/repos/mqobsidian.md]
---

# mqobsidian — agent view

Compressed first-stop for agents (read-order step 0). Generated — do not
edit by hand; re-run `mq-agent agent-views rebuild`.

## Current state

Hålla MQ-stackens durable memory tunn och public-safe, och äga de execution- och routingkontrakt senare lager läser. `v0.4.0` (2026-09-11) är en kontraktsgrund, inte levererad Execution Intelligence: kontrakten är kompletta och grindade, men fallback recording och aktiv-vs-shadow-divergens är öppna. Execution- och routingkontrakten är kanoniska här och registret…

## Active priorities

- Regenerera steg 0 när hot eller index ändras; read-order-kedjan ska vara liten och sann.
- Skaffa applied-evidens från fler än en task; de 14 överförda posterna är alla samma `docs-review`-beslut.
- Samla execution outcomes per task class och route; underlaget domineras i dag av task class `docs`.
- Rapportera aktiv-vs-shadow-divergens innan någon kandidatpolicy bedöms.

## Current blockers

- Inga bekräftade blockers.
- Överföringen till `routing/outcomes.jsonl` är manuell, så vault och runtime-store glider isär tyst mellan körningar.
- Ett underlag dominerat av en task class ser ut som routingevidens utan att kunna jämföra routes.
- Kontrakt kan vara kompletta i båda ändar utan att sömmen körs; en tom yta bevisar ingenting.

## Relevant lessons

- assess whether a completed semantic-memory upload proves the retrieval surface is correct
- refresh the OpenAI semantic repository memory after finding the store 20 days stale

## Read next

- [[systems/mqobsidian/hot]]
- [[systems/mqobsidian/index]]
