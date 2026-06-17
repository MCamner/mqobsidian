---
type: reference
system: mq-mcp
status: active
tags: [reference, commands, system]
updated: 2026-06-17
links_to: [index, overview]
---

# mq-mcp Commands v2

Token-snål kommandoreferens för `mq-mcp`.

Den här versionen är uppdelad i korta sektioner så att Codex och Claude Code kan läsa **bara rätt del** i stället för hela filen.

> Källbas: verifierad mot `README.md`, `docs/demo.md`, `docs/install.md` och `docs/upgrade.md` i `mq-mcp`.

---

# 1. Core Commands

## `mq-mcp doctor`
**Vad det gör**
Kontrollerar att installationen verkar frisk.

**När det används**
Efter installation eller vid felsökning.

**1 exempel**
```bash
mq-mcp doctor
```

---

## `mq-mcp health`
**Vad det gör**
Visar hälsoläge för installationen.

**När det används**
För snabb statuskontroll.

**1 exempel**
```bash
mq-mcp health
```

---

## `mq-mcp tools`
**Vad det gör**
Visar tillgängliga verktyg.

**När det används**
När du vill se den exponerade verktygsytan.

**1 exempel**
```bash
mq-mcp tools
```

---

## `mq-mcp serve`
**Vad det gör**
Startar den lokala MCP-servern.

**När det används**
När du vill köra servern lokalt.

**1 exempel**
```bash
mq-mcp serve
```

---

## `mq-mcp validate`
**Vad det gör**
Kör projektvalidering.

**När det används**
Efter ändringar, efter installation eller inför release.

**1 exempel**
```bash
mq-mcp validate
```

---

## `mq-mcp config path`
**Vad det gör**
Visar konfigurationssökvägen.

**När det används**
När du behöver hitta lokal konfiguration.

**1 exempel**
```bash
mq-mcp config path
```

---

## `mq-mcp report --json`
**Vad det gör**
Skapar en strukturerad diagnostikrapport i JSON-format.

**När det används**
Vid felsökning eller observability.

**1 exempel**
```bash
mq-mcp report --json
```

---

## `mq-mcp bundle --validate`
**Vad det gör**
Validerar bundle-/diagnostikflödet.

**När det används**
När du vill samla eller kontrollera diagnostikflödet.

**1 exempel**
```bash
mq-mcp bundle --validate
```

---

## `mq-mcp version`
**Vad det gör**
Visar aktuell installerad version.

**När det används**
Efter uppgradering eller vid versionskontroll.

**1 exempel**
```bash
mq-mcp version
```

---

# 2. Install / Upgrade / Reinstall

## `./scripts/install.sh`
**Vad det gör**
Installerar lokal miljö, skapar `.env` vid behov, kör `uv sync`, installerar `mq-mcp`-kommandot och kör `mq-mcp doctor`.

**När det används**
Standardvägen för första installation.

**1 exempel**
```bash
./scripts/install.sh
```

---

## `./scripts/upgrade.sh`
**Vad det gör**
Pullar `main`, synkar beroenden, installerar om kommandot och kör validering.

**När det används**
Standardvägen för att uppdatera lokal installation.

**1 exempel**
```bash
./scripts/upgrade.sh
```

---

## `git pull origin main`
**Vad det gör**
Hämtar senaste ändringar manuellt från `main`.

**När det används**
När du vill uppgradera steg för steg.

**1 exempel**
```bash
git pull origin main
```

---

## `cd mq-mcp && uv sync`
**Vad det gör**
Synkar Python-beroenden.

**När det används**
Vid manuell uppgradering eller miljöfix.

**1 exempel**
```bash
cd mq-mcp
uv sync
```

---

## `diff mq-mcp/.env mq-mcp/.env.example`
**Vad det gör**
Jämför lokal `.env` med `.env.example`.

**När det används**
Efter uppgradering när nya miljövariabler kan ha tillkommit.

**1 exempel**
```bash
diff mq-mcp/.env mq-mcp/.env.example
```

---

## `cd mq-mcp && rm -rf .venv && uv sync`
**Vad det gör**
Tar bort virtuell miljö och bygger upp den igen.

**När det används**
När beroenden eller miljön blivit trasig eller stale.

**1 exempel**
```bash
cd mq-mcp
rm -rf .venv
uv sync
```

---

## `./scripts/uninstall.sh`
**Vad det gör**
Tar bort `mq-mcp`-kommandot men lämnar `.env` kvar.

**När det används**
När du vill avinstallera CLI:t utan att förlora miljöfilen.

**1 exempel**
```bash
./scripts/uninstall.sh
```

---

## `./scripts/uninstall.sh --remove-env`
**Vad det gör**
Tar bort CLI:t och låter dig även ta bort `.env`.

**När det används**
När du vill göra en mer fullständig uninstall.

**1 exempel**
```bash
./scripts/uninstall.sh --remove-env
```

---

## Clean reinstall
**Vad det gör**
Gör full rensning och ren nyinstallation.

**När det används**
När lokala tool shims eller beroenden är trasiga.

**1 exempel**
```bash
./scripts/uninstall.sh
cd mq-mcp
rm -rf .venv
cd ..
./scripts/install.sh
mq-mcp validate
```

---

# 3. Profiles

## `mq-mcp profiles list`
**Vad det gör**
Listar tillgängliga profiler.

**När det används**
När du vill se vilka klient-/workflow-profiler som finns.

**1 exempel**
```bash
mq-mcp profiles list
```

---

## `mq-mcp profiles show read-only`
**Vad det gör**
Visar profilen `read-only`.

**När det används**
När du vill se en säker läsprofil.

**1 exempel**
```bash
mq-mcp profiles show read-only
```

---

## `mq-mcp profiles show claude-desktop`
**Vad det gör**
Visar profilen för Claude Desktop.

**När det används**
När du vill koppla `mq-mcp` till Claude Desktop.

**1 exempel**
```bash
mq-mcp profiles show claude-desktop
```

---

## `mq-mcp profiles validate`
**Vad det gör**
Validerar profilkonfigurationer.

**När det används**
Efter ändringar i profiler.

**1 exempel**
```bash
mq-mcp profiles validate
```

---

# 4. Stability / Release

## `mq-mcp stability show`
**Vad det gör**
Visar stabilitetsläge för projektet.

**När det används**
När du snabbt vill se stabilitetsstatus.

**1 exempel**
```bash
mq-mcp stability show
```

---

## `mq-mcp stability validate`
**Vad det gör**
Validerar stabilitetsbaslinjen.

**När det används**
Inför release eller efter större ändringar.

**1 exempel**
```bash
mq-mcp stability validate
```

---

## `./scripts/release-check.sh`
**Vad det gör**
Kör release readiness-kontroll utanför CLI:t.

**När det används**
Inför release eller taggning.

**1 exempel**
```bash
./scripts/release-check.sh
```

---

# 5. Bridge Prompts

## `uv --directory mq-mcp run python bridge.py "List the available MCP tools."`
**Vad det gör**
Låter bridge lista tillgängliga MCP-verktyg.

**När det används**
När du vill testa bridge + tool discovery.

**1 exempel**
```bash
uv --directory mq-mcp run python bridge.py "List the available MCP tools."
```

---

## `uv --directory mq-mcp run python bridge.py "Check local system resources."`
**Vad det gör**
Ber bridge läsa lokala systemresurser.

**När det används**
När du vill testa systemread-ytan.

**1 exempel**
```bash
uv --directory mq-mcp run python bridge.py "Check local system resources."
```

---

## `uv --directory mq-mcp run python bridge.py "Read README.md and summarize the project."`
**Vad det gör**
Läser repo-kontext och sammanfattar projektet.

**När det används**
När du vill testa repo-läsning via bridge.

**1 exempel**
```bash
uv --directory mq-mcp run python bridge.py "Read README.md and summarize the project."
```

---

## `uv --directory mq-mcp run python bridge.py "Show git status and recent commits."`
**Vad det gör**
Läser git-status och senaste commits via bridge.

**När det används**
Vid snabb repo-kontroll via naturligt språk.

**1 exempel**
```bash
uv --directory mq-mcp run python bridge.py "Show git status and recent commits."
```

---

## `uv --directory mq-mcp run python bridge.py "Run project validation."`
**Vad det gör**
Ber bridge köra projektvalidering.

**När det används**
När du vill trigga validation via språkgränssnittet.

**1 exempel**
```bash
uv --directory mq-mcp run python bridge.py "Run project validation."
```

---

# 6. Safety / Classification Prompts

## `uv --directory mq-mcp run python bridge.py "Use tool_safety_report and summarize the MCP tool safety map."`
**Vad det gör**
Läser säkerhetskartan via read-only tool och sammanfattar den.

**När det används**
När du vill förstå safety-klasserna utan att ändra något.

**1 exempel**
```bash
uv --directory mq-mcp run python bridge.py "Use tool_safety_report and summarize the MCP tool safety map."
```

---

## `uv --directory mq-mcp run python bridge.py "Which MCP tools are read-only?"`
**Vad det gör**
Frågar bridge vilka verktyg som är read-only.

**När det används**
När du vill skilja säkra läsytor från skriv- eller subprocess-ytor.

**1 exempel**
```bash
uv --directory mq-mcp run python bridge.py "Which MCP tools are read-only?"
```

---

## `uv --directory mq-mcp run python bridge.py "Which MCP tools can write files?"`
**Vad det gör**
Frågar bridge vilka verktyg som kan skriva filer.

**När det används**
När du vill identifiera Class C-verktyg.

**1 exempel**
```bash
uv --directory mq-mcp run python bridge.py "Which MCP tools can write files?"
```

---

## `uv --directory mq-mcp run python bridge.py "Which MCP tools run subprocesses?"`
**Vad det gör**
Frågar bridge vilka verktyg som kör subprocesser.

**När det används**
När du vill identifiera Class D-verktyg.

**1 exempel**
```bash
uv --directory mq-mcp run python bridge.py "Which MCP tools run subprocesses?"
```

---

# 7. mq-hal / repo-signal via Bridge

## `uv --directory mq-mcp run python bridge.py "Use hal_repo_report with mode audit for repo mq-mcp."`
**Vad det gör**
Kör `hal_repo_report` i läget `audit` för `mq-mcp`.

**När det används**
När du vill få en publish-quality audit via `mq-hal` och `repo-signal`.

**1 exempel**
```bash
uv --directory mq-mcp run python bridge.py "Use hal_repo_report with mode audit for repo mq-mcp."
```

---

## `uv --directory mq-mcp run python bridge.py "Use hal_repo_report with mode release-brief for repo mq-mcp."`
**Vad det gör**
Kör `hal_repo_report` i läget `release-brief`.

**När det används**
När du vill få release readiness-sammanfattning.

**1 exempel**
```bash
uv --directory mq-mcp run python bridge.py "Use hal_repo_report with mode release-brief for repo mq-mcp."
```

---

## `uv --directory mq-mcp run python bridge.py "Use hal_repo_report with mode brief for repo mq-mcp."`
**Vad det gör**
Kör `hal_repo_report` i läget `brief`.

**När det används**
När du vill ha en kort repoöversikt.

**1 exempel**
```bash
uv --directory mq-mcp run python bridge.py "Use hal_repo_report with mode brief for repo mq-mcp."
```

---

## `uv --directory mq-mcp run python bridge.py "Use hal_repo_report with mode repo-status for repo mq-mcp."`
**Vad det gör**
Kör `hal_repo_report` i läget `repo-status`.

**När det används**
När du vill ha statusöversikt för repot.

**1 exempel**
```bash
uv --directory mq-mcp run python bridge.py "Use hal_repo_report with mode repo-status for repo mq-mcp."
```

---

## `uv --directory mq-mcp run python bridge.py "Use hal_repo_report with mode ci for repo mq-mcp."`
**Vad det gör**
Kör `hal_repo_report` i läget `ci`.

**När det används**
När du vill ha CI-orienterad översikt.

**1 exempel**
```bash
uv --directory mq-mcp run python bridge.py "Use hal_repo_report with mode ci for repo mq-mcp."
```

---

# 8. Direct Run Without Installed CLI

## `cd mq-mcp && uv run python bridge.py --tools`
**Vad det gör**
Kör bridge direkt från projektmappen och listar verktyg.

**När det används**
När du vill testa snabbt utan installerat CLI.

**1 exempel**
```bash
cd mq-mcp
uv run python bridge.py --tools
```

---

## `cd mq-mcp && uv run mcp run server.py`
**Vad det gör**
Kör servern direkt via `uv`.

**När det används**
När du vill starta servern från projektmappen.

**1 exempel**
```bash
cd mq-mcp
uv run mcp run server.py
```

---

# 9. Environment

## `OPENAI_API_KEY=your_api_key_here`
**Vad det gör**
Sätter OpenAI-nyckel för bridge-prompts som behöver OpenAI.

**När det används**
När du vill köra bridge-kommandon som använder modellanrop.

**1 exempel**
```bash
OPENAI_API_KEY=your_api_key_here
```

---

## `MQ_MCP_ALLOWED_PATHS=""`
**Vad det gör**
Definierar allowlistade lokala sökvägar.

**När det används**
När du vill styra vilka lokala paths `mq-mcp` får nå.

**1 exempel**
```bash
MQ_MCP_ALLOWED_PATHS=""
```

---

## `MQ_MCP_LOCAL_REPOS=""`
**Vad det gör**
Definierar registrerade lokala repos.

**När det används**
När repo-relaterade verktyg ska känna till lokala repos.

**1 exempel**
```bash
MQ_MCP_LOCAL_REPOS=""
```

---

# 10. Zsh Completion

## `mkdir -p ~/.zsh/completions`
**Vad det gör**
Skapar katalog för zsh-completions.

**När det används**
När du vill aktivera tab-completion.

**1 exempel**
```bash
mkdir -p ~/.zsh/completions
```

---

## `ln -sf "$(pwd)/completions/_mq-mcp" ~/.zsh/completions/_mq-mcp`
**Vad det gör**
Länkar in completion-filen.

**När det används**
När du vill aktivera completion för `mq-mcp`.

**1 exempel**
```bash
ln -sf "$(pwd)/completions/_mq-mcp" ~/.zsh/completions/_mq-mcp
```

---

# 11. Fast Path

## Install
```bash
./scripts/install.sh
```

## Health
```bash
mq-mcp doctor
mq-mcp health
```

## Tools
```bash
mq-mcp tools
```

## Server
```bash
mq-mcp serve
```

## Validate
```bash
mq-mcp validate
./scripts/release-check.sh
```

## Upgrade
```bash
./scripts/upgrade.sh
```
