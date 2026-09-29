---
type: reference
system: atlas-core
status: active
tags: [reference, commands, atlas-core, loop]
updated: 2026-09-29
links_to: [index, overview]
---

# Atlas Core Commands

Token-snål kommandoreferens för den lokala Atlas Core-loopen.

> `atlas run` är själva loopen: observe → route → plan → execute → verify → evaluate → re-observe/replan eller stop.

## Grundkontroll

```bash
atlas version
atlas routes
```

## Kör en lokal repo-loop

```bash
cd /path/to/repo

atlas run \
  "granska repot och identifiera endast verifierbara fynd" \
  --repo-path . \
  --max-iterations 3
```

`--repo-path .` gör lokala filer till `Observation.v1`-evidens. Utan evidens kan Atlas inte ge deterministiskt verifierade repo-fynd.

## Rekommenderad spårbar körning

```bash
RUN_ID=$(atlas create)

atlas run \
  "granska CI och releaseberedskap" \
  --repo-path . \
  --max-iterations 4 \
  --wall-seconds 90 \
  --max-tool-calls 48 \
  --max-output-bytes 131072 \
  --event-log /tmp/atlas-run.jsonl \
  --run-id "$RUN_ID"

atlas inspect "$RUN_ID" \
  --event-log /tmp/atlas-run.jsonl
```

## Följ en körning

```bash
atlas status "$RUN_ID" --event-log /tmp/atlas-run.jsonl
atlas events "$RUN_ID" --event-log /tmp/atlas-run.jsonl --follow
```

## Avbryt

```bash
atlas cancel "$RUN_ID" --event-log /tmp/atlas-run.jsonl
```

## Maskinläsbar inspect

```bash
atlas inspect "$RUN_ID" \
  --event-log /tmp/atlas-run.jsonl \
  --json
```

## CI/release-gate parity

Efter Atlas Core PR #127 är denna uppgift en egen deterministisk review-yta:

```bash
cd ~/mq-agent

RUN_ID=$(atlas create)

atlas run \
  "Kontrollera om release-check.sh och GitHub Actions har samma release-gates. Identifiera konkret drift mellan release-check.sh, tests.yml, markdownlint.yml och mq-stack-gate.yml. Rapportera endast fynd som kan styrkas med de lästa filerna." \
  --repo-path . \
  --max-iterations 4 \
  --wall-seconds 90 \
  --max-tool-calls 48 \
  --max-output-bytes 131072 \
  --event-log /tmp/mq-agent-atlas-parity.jsonl \
  --run-id "$RUN_ID"

atlas inspect "$RUN_ID" \
  --event-log /tmp/mq-agent-atlas-parity.jsonl
```

Förväntad route/topic efter #127:

```text
route: repo_review
topic: ci_gate_parity
```

Producenten jämför deklarerade checks och targets. Ett resultat utan drift betyder inte automatiskt att CI-körningarna är gröna.

## GitHub-repo som källa

```bash
atlas run \
  "granska MCamner/mqobsidian" \
  --repo MCamner/mqobsidian
```

## Metrics

```bash
atlas metrics --event-log /tmp/atlas-run.jsonl
atlas metrics --event-log /tmp/atlas-run.jsonl --json
```

## Feedback

```bash
atlas feedback record "$RUN_ID" \
  --event-log /tmp/atlas-run.jsonl \
  --outcome confirmed \
  --lesson "kort verifierad lärdom" \
  --store /path/to/learning-store
```

Promotion görs separat och explicit:

```bash
atlas feedback promote <candidate-id> \
  --event-log /tmp/atlas-run.jsonl \
  --store /path/to/learning-store
```

## Diagnostikregel

Om en repo-loop upprepade gånger slutar med:

```text
no_on_topic_finding
```

trots att rätt filer observerats, öka inte iterationerna först. Kontrollera om den valda review-frågan har en producent som kan skapa typed findings för just den relationen.
