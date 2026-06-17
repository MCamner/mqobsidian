# mqobsidian Obsidian Pack

Detta paket innehåller fem färdiga mallar för `mqobsidian`:

- `summary-template.md`
- `research-node-template.md`
- `skill-template.md`
- `index-template.md`
- `hot-template.md`
- `agent-memory-block.md`

## Rekommenderad placering i vaulten

```text
mqobsidian/
├─ templates/
│  ├─ summary-template.md
│  ├─ research-node-template.md
│  ├─ skill-template.md
│  ├─ index-template.md
│  ├─ hot-template.md
│  └─ agent-memory-block.md
├─ 02_summaries/
├─ 03_systems/
├─ 04_skills/
├─ 05_research/
└─ 07_dashboards/
```

## Designprinciper

Paketet följer samma kärnlogik som roadmapen:

1. **Ingest först** – rådata ska kondenseras till tydliga sammanfattningar.
2. **Hot cache** – aktuell, liten och billig kontext nära till hands.
3. **Deep wiki** – långsiktig struktur i länkar, index och systemsidor.
4. **Skills/SOP** – standardiserad exekvering för AI och människa.
5. **Research nodes** – okända saker ska isoleras, inte gissas fram.

## Rekommenderad ordning

1. Lägg mallarna i `templates/`
2. Skapa en första `hot.md` för varje kärnsystem
3. Skapa en `index.md` per system
4. Börja skriva nya notes utifrån summary/research/skill-mallarna
5. Lägg `agent-memory-block.md` i MQ-repons `AGENTS.md`/`CLAUDE.md` när de ska läsa mqobsidian först

## Förslag på första notes

- `03_systems/mq-mcp/index.md`
- `03_systems/mq-agent/index.md`
- `03_systems/mq-ums/index.md`
- `03_systems/mq-mcp/hot.md`
- `03_systems/mq-agent/hot.md`
- `03_systems/mq-ums/hot.md`
