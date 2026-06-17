---
type: reference
system: mq-agent
status: active
tags: [reference, commands, system]
updated: 2026-06-17
links_to: [index, overview]
---

# mq-agent Commands v2

Token-snål kommandoreferens för `mq-agent`.

> Källbas: verifierad mot `README.md` och `docs/COMMANDS.md` i `mq-agent`.

## 1. Core Commands

### `mq-agent doctor`
**Vad det gör**
Kontrollerar miljö och beroenden.

**När det används**
Efter installation eller vid felsökning.

**1 exempel**
```bash
mq-agent doctor
```

### `mq-agent score .`
**Vad det gör**
Kör README-score och publish-checklist utan API-nyckel.

**När det används**
När du snabbt vill få en repo-kvalitetsbedömning.

**1 exempel**
```bash
mq-agent score .
```

### `mq-agent repo-summary .`
**Vad det gör**
Ger en kort repoöversikt.

**När det används**
När du vill förstå repot snabbt utan full audit.

**1 exempel**
```bash
mq-agent repo-summary .
```

### `mq-agent tools`
**Vad det gör**
Listar registrerade verktyg.

**När det används**
När du vill se den lokala verktygsytan.

**1 exempel**
```bash
mq-agent tools
```

### `mq-agent tools --describe <name>`
**Vad det gör**
Visar metadata och safety class för ett verktyg.

**När det används**
När du vill förstå exakt vad ett visst tool gör.

**1 exempel**
```bash
mq-agent tools --describe read_repo_file
```

### `mq-agent tools --mcp`
**Vad det gör**
Listar även upptäckta MCP-verktyg.

**När det används**
När du vill se både lokala tools och MCP-surface.

**1 exempel**
```bash
mq-agent tools --mcp
```

## 2. Audit / Signal / Plan

### `mq-agent audit .`
**Vad det gör**
Kör full repo-audit med AI-verifiering.

**När det används**
När du vill få en djupare read-only repoanalys.

**1 exempel**
```bash
mq-agent audit .
```

### `mq-agent signal .`
**Vad det gör**
Kör repo-signal-bedömning plus AI-förbättringsplan.

**När det används**
När du vill få en AI-stödd repoanalys utöver score.

**1 exempel**
```bash
mq-agent signal .
```

### `mq-agent plan "goal"`
**Vad det gör**
Genererar en plan för ett mål.

**När det används**
När du vill få en strukturerad plan innan exekvering.

**1 exempel**
```bash
mq-agent plan "prepare release"
```

### `mq-agent release-plan`
**Vad det gör**
Visar standardiserad releaseplan.

**När det används**
När du vill se vad releaseflödet innehåller innan du kör checks.

**1 exempel**
```bash
mq-agent release-plan
```

### `mq-agent release-check`
**Vad det gör**
Validerar release readiness.

**När det används**
Inför release eller större merge.

**1 exempel**
```bash
mq-agent release-check
```

### `mq-agent release-check --approve`
**Vad det gör**
Kör release-check med exekvering där approval krävs.

**När det används**
När du vill gå från suggest till execute.

**1 exempel**
```bash
mq-agent release-check --approve
```

### `mq-agent fix-ci`
**Vad det gör**
Diagnostiserar CI-fel.

**När det används**
När pipeline eller testjobb har gått sönder.

**1 exempel**
```bash
mq-agent fix-ci
```

## 3. Safe Execution

### `mq-agent run "cmd" --approve`
**Vad det gör**
Kör ett shell-kommando genom safety gates.

**När det används**
När du vill exekvera något kontrollerat via mq-agent.

**1 exempel**
```bash
mq-agent run "pytest" --approve
```

### `mq-agent run "git status"`
**Vad det gör**
Kör ett läskommando via mq-agent.

**När det används**
När du vill köra säkra shell-kommandon utan approval för destruktiv handling.

**1 exempel**
```bash
mq-agent run "git status"
```

## 4. MCP Bridge

### `mq-agent mcp status`
**Vad det gör**
Kontrollerar mq-mcp reachability och tool counts.

**När det används**
När du vill veta om mcp-lagret lever.

**1 exempel**
```bash
mq-agent mcp status
```

### `mq-agent mcp tools`
**Vad det gör**
Listar MCP-verktyg med safety class och beskrivning.

**När det används**
När du vill inspektera mcp-ytan.

**1 exempel**
```bash
mq-agent mcp tools
```

### `mq-agent run-tool <name>`
**Vad det gör**
Kör ett specifikt MCP-verktyg genom safety gates.

**När det används**
När du vill använda ett verktyg utan att gå via fri prompt.

**1 exempel**
```bash
mq-agent run-tool read_repo_file --arg path=README.md
```

### `mq-agent run-tool <name> --dry-run`
**Vad det gör**
Preview av tool call utan kontakt med mq-mcp.

**När det används**
När du vill se vad som skulle hända före exekvering.

**1 exempel**
```bash
mq-agent run-tool read_repo_file --arg path=README.md --dry-run
```

### `mq-agent run-tool <name> --approve`
**Vad det gör**
Tillåter körning av write-capable eller subprocess tool.

**När det används**
När ett verktyg annars blockeras av safety gates.

**1 exempel**
```bash
mq-agent run-tool update_repo_file --arg path=f.py --arg old=x --arg new=y --approve
```

## 5. Review Commands

### `mq-agent review file <path>`
**Vad det gör**
Reviewar en fil genom mq-mcp.

**När det används**
När du vill få en filgranskning via review-pipeline.

**1 exempel**
```bash
mq-agent review file README.md
```

### `mq-agent review diff`
**Vad det gör**
Reviewar aktuell diff genom mq-mcp.

**När det används**
När du vill granska ändringar före commit eller PR.

**1 exempel**
```bash
mq-agent review diff
```

### `mq-agent review repo [path]`
**Vad det gör**
Reviewar ett repo genom mq-mcp.

**När det används**
När du vill ha bred repo-review via mcp.

**1 exempel**
```bash
mq-agent review repo .
```

### `mq-agent review file <path> --fast`
**Vad det gör**
Föredrar Class A-tools i review-flödet.

**När det används**
När du vill hålla review snabbare och säkrare.

**1 exempel**
```bash
mq-agent review file README.md --fast
```

## 6. Memory / Models / Dashboard

### `mq-agent memory ingest`
**Vad det gör**
Indexerar mqobsidian Markdown-minne.

**När det används**
När du vill uppdatera agentens minnesindex från vaulten.

**1 exempel**
```bash
mq-agent memory ingest
```

### `mq-agent memory query <query>`
**Vad det gör**
Söker i mqobsidian-minnet.

**När det används**
När du vill hitta relevant tidigare kunskap.

**1 exempel**
```bash
mq-agent memory query "release gate"
```

### `mq-agent memory summarize`
**Vad det gör**
Sammanfattar minnessektioner i mqobsidian.

**När det används**
När du vill få komprimerad läsning av memory-lagret.

**1 exempel**
```bash
mq-agent memory summarize
```

### `mq-agent memory link`
**Vad det gör**
Rapporterar kandidater för länkar mellan notes.

**När det används**
När du vill förbättra vaultens struktur.

**1 exempel**
```bash
mq-agent memory link
```

### `mq-agent models current`
**Vad det gör**
Visar aktiv Ollama-modellprofil.

**När det används**
När du vill se vilken lokal modell som är aktiv.

**1 exempel**
```bash
mq-agent models current
```

### `mq-agent models list`
**Vad det gör**
Listar lokala Ollama-modeller.

**När det används**
När du vill välja eller inspektera tillgängliga modeller.

**1 exempel**
```bash
mq-agent models list
```

### `mq-agent models switch <model> --profile <profile> --approve`
**Vad det gör**
Byter modellprofil och skriver config.

**När det används**
När du vill byta aktiv modellprofil.

**1 exempel**
```bash
mq-agent models switch qwen3:4b --profile local --approve
```

### `mq-agent models bench [model]`
**Vad det gör**
Kör ett litet lokalt Ollama-benchmark.

**När det används**
När du vill jämföra modellprestanda snabbt.

**1 exempel**
```bash
mq-agent models bench
```

### `mq-agent dashboard`
**Vad det gör**
Visar operator snapshot för stack, brain, Ollama och contracts.

**När det används**
När du vill ha en snabb operativ översikt.

**1 exempel**
```bash
mq-agent dashboard
```

### `mq-agent tui`
**Vad det gör**
Startar Textual-dashboard.

**När det används**
När du vill jobba i interaktiv UI.

**1 exempel**
```bash
mq-agent tui
```

## 7. Stack Commands

### `mq-agent run --stack`
**Vad det gör**
Kör den kanoniska stack runtime-pipelinen.

**När det används**
När du vill få en samlad stackkörning.

**1 exempel**
```bash
mq-agent run --stack --dry-run
```

### `mq-agent stack loop`
**Vad det gör**
Planerar den kontrollerade autonoma stack-loopen.

**När det används**
När du vill se nästa steg i stackens loop utan att köra dem.

**1 exempel**
```bash
mq-agent stack loop
```

### `mq-agent stack loop --execute --approve`
**Vad det gör**
Kör en allowlistad stack loop-action.

**När det används**
När du vill exekvera ett steg i den kontrollerade loopen.

**1 exempel**
```bash
mq-agent stack loop --execute --approve
```

## 8. Flags

### `--dry-run`
**Vad det gör**
Visar plan utan exekvering.

**När det används**
Som standard när du vill se vad som skulle hända.

**1 exempel**
```bash
mq-agent audit . --dry-run
```

### `--json`
**Vad det gör**
Ger machine-readable JSON-output.

**När det används**
För scripting eller vidare bearbetning.

**1 exempel**
```bash
mq-agent mcp status --json
```

### `--approve`
**Vad det gör**
Godkänner write-/execute-flöden.

**När det används**
När ett kommando annars stoppas av safety gates.

**1 exempel**
```bash
mq-agent run "pytest" --approve
```

## 9. Fast Path

### Health
```bash
mq-agent doctor
```

### Quick repo score
```bash
mq-agent score .
```

### Audit
```bash
mq-agent audit . --dry-run
```

### Release
```bash
mq-agent release-check --dry-run
```

### MCP
```bash
mq-agent mcp status
mq-agent mcp tools
```

### Memory
```bash
mq-agent memory ingest
mq-agent memory query "release gate"
```
