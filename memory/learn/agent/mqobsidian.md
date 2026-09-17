---
type: agent-view
system: mqobsidian
generated: 2026-09-17
generator: mq-agent agent-views rebuild
sources: [systems/mqobsidian/hot.md, systems/mqobsidian/index.md, memory/learn/repos/mqobsidian.md]
---

# mqobsidian — agent view

Compressed first-stop for agents (read-order step 0). Generated — do not
edit by hand; re-run `mq-agent agent-views rebuild`.

## Current state

Hålla MQ-stackens durable memory tunn och public-safe, och äga de execution- och routingkontrakt senare lager läser — utan att flytta runtime till vaulten. `v0.4.0` släppt 2026-09-11: execution- och routingkontrakten är kompletta, kanoniska och grindade, och kontraktsregistret hålls mot `schemas/` i båda riktningar. Det är en…

## Active priorities

- Hålla read-order-kedjan liten och sann: agent view -> hot -> index -> små cards, och regenerera steg 0…
- Skaffa applied-evidens från fler än en task; de 14 överförda posterna är alla samma `docs-review`-beslut.
- Samla execution outcomes per task class och route; omätta räknare är okända, inte noll, och underlaget domineras i…
- Rapportera aktiv-vs-shadow-divergens innan någon kandidatpolicy bedöms.

## Current blockers

- Inga bekräftade blockers.
- Överföringen till `routing/outcomes.jsonl` är manuell, så vault och runtime-store glider isär tyst mellan körningar; 130 -> 144 den…
- Ett underlag som domineras av en task class kan se ut som routingevidens utan att kunna jämföra routes.
- Kontrakt kan vara kompletta i båda ändar utan att sömmen körs; en tom yta betyder inte att inget…

## Relevant lessons

- Document and verify CodeGraph CLI query patterns for mqobsidian

## Read next

- [[systems/mqobsidian/hot]]
- [[systems/mqobsidian/index]]
