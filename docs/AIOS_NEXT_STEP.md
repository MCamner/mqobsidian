---
type: index
title: AIOS nästa steg för mqobsidian
status: active
tags: [docs, aios, process, mq-mcp]
updated: 2026-06-16
links_to: [agent-mcp-layer, ../skills/index]
---

# AIOS nästa steg för mqobsidian

Tar valvet från **struktur** till **första operativa körning**: bygg en rådata-yta, kör ett skill-recept mot en verklig MQ-logg, och håll `hot.md` kort och sant.

## Steg 1 — bygg grunden

`raw_logs/` är en kontrollerad plats för MQ-loggar, incidentutdrag, felspår och rådiagnostik. Lägg in **ett verkligt felspår**, inte tio.

## Steg 2 — kör receptet

Använd `mq-analysis`-skillen. Den ska:

1. läsa aktuell logg / råinput
2. läsa `systems/mq-mcp/hot.md`
3. läsa `systems/mq-mcp/index.md`
4. avgöra om problemet är känt eller okänt
5. skriva en strukturerad summary (känt) eller en research-node (okänt)

Det viktiga är inte att AI svarar — det viktiga är att AI svarar **via valvets struktur**.

## Steg 3 — optimera snabbminnet

När analysen är gjord, uppdatera `systems/mq-mcp/hot.md` med nuvarande fokus, senaste verifierade läge, aktiva blockerare, viktigaste länkar och vad agenten ska läsa först. Mål: 150–300 ord, max ~500.

## Beslutsregel

- Loggen matchar känd kunskap → skriv summary, länka till system/index, uppdatera hot vid behov.
- Loggen matchar **inte** känd kunskap → skapa research-node, gissa inte, förorena inte hot.md med osäker information.

## Definition av klart

- en riktig logg i `raw_logs/`
- `mq-analysis` tillgänglig för Claude och Codex
- en första verifierad analys
- ett uppdaterat `systems/mq-mcp/hot.md`

## Relaterat

- [[agent-mcp-layer]] — hur agenter och MCP är kopplade
- [[../skills/index]] — skill-katalogen
- [[../decisions/ADR-002-note-creation-and-ingest]] — note-creation + ingest-regler
