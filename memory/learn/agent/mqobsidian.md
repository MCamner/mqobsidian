---
type: agent-view
system: mqobsidian
generated: 2026-11-02
generator: mq-agent agent-views rebuild
sources: [systems/mqobsidian/hot.md, systems/mqobsidian/index.md]
---

# mqobsidian — agent view

Compressed first-stop for agents (read-order step 0). Generated — do not
edit by hand; re-run `mq-agent agent-views rebuild`.

## Current state

Hålla MQ-stackens durable memory tunn och public-safe, och äga de execution- och routingkontrakt senare lager läser. `v0.5.0` (2026-10-24): mätt `completeness`, task class `repo-review`, versionerad agent view. Divergensrapporten finns i mq-agent; policylagret (v2.7) är öppet. Execution- och routingkontrakten är kanoniska här och registret hålls mot `schemas/`…

## Active priorities

- Regenerera steg 0 när hot eller index ändras; read-order-kedjan ska vara liten och sann.
- Operatörsbeslut om `docs-review`-readiness (32 applied, ett beslut); fler task classes saknas fortfarande.
- Samla execution outcomes per task class och route; underlaget domineras i dag av task class `docs`.
- Divergensrapporten finns i mq-agent; aktuell era saknar fullständiga lyckade körningar att jämföra.

## Current blockers

- Inga bekräftade blockers.
- Överföringen till `routing/outcomes.jsonl` är manuell, så vault och runtime-store glider isär tyst mellan körningar.
- Ett underlag dominerat av en task class ser ut som routingevidens utan att kunna jämföra routes.
- Kontrakt kan vara kompletta i båda ändar utan att sömmen körs; en tom yta bevisar ingenting.

## Read next

- [[systems/mqobsidian/hot]]
- [[systems/mqobsidian/index]]
