# Command Learning System

## Problem eller system

MQ-stacken har två närliggande men olika lärsystem:

1. `mqobsidian/memory/commands` samlar faktisk kommandoanvändning för att upptäcka återkommande arbetsmönster.
2. `mq-mcp learn` lagrar verifierade, generaliserade lärdomar från reviews, commits och verkliga resultat.

De två systemen ska utbyta signaler, men får inte konkurrera om samma sanning.

---

## Synligt utfall

Command-systemet ska över tid kunna svara på:

- vilka kommandon används ofta?
- vilka kommandosekvenser återkommer?
- vilka fungerar i flera repo?
- vilka sparar tid?
- vilka orsakar problem?
- vilka bör bli återanvändbara command patterns?

Learn-systemet ska svara på:

- vilken generell princip har bevisats?
- vilken lärdom bör påverka framtida arbete?
- vilken kunskap är verifierad nog att återanvändas?

---

## Underliggande struktur

### Command-systemet

Canonical lokal data:

```text
memory/commands/
├── inbox/
│   └── observations.jsonl
├── patterns/
│   └── patterns.jsonl
├── feedback/
│   ├── feedback.jsonl
│   └── proposals.md
├── views/
└── mqlaunch/
    └── recommended.json
```

Flöde:

```text
kommando används
        ↓
observation registreras
        ↓
återkommande beteende upptäcks
        ↓
command-pattern föreslås
        ↓
mänsklig kurering
        ↓
pattern används via mqlaunch
        ↓
feedback registreras
        ↓
ranking, promotion eller downgrade
```

### Learn-systemet

Canonical data ägs av `mq-mcp`:

```text
review / commit / verifierat arbete
        ↓
learn candidate
        ↓
pending inbox
        ↓
read-only draft
        ↓
mänsklig verifiering
        ↓
curated lesson
        ↓
användning och feedback
```

---

## Ansvar

### mqobsidian

Äger:

- command observations
- command-pattern-schema
- command-pattern-kandidater
- usage-signaler
- feedback-policy
- rankingvyer
- `recommended.json`
- read-only export av learn-lessons

Äger inte:

- review-extraction
- canonical learn-store
- automatisk promotion av learn-lessons
- exekvering av rekommenderade kommandon

### mq-mcp

Äger:

- learn-extraction
- candidate inbox
- evidensvalidering
- riskklassning
- canonical learn-store
- lesson promotion
- hygiene och deduplicering

### mq-agent

Äger:

- orchestration mellan systemen
- repo-path forwarding
- command routing
- approval-flöden
- feedback-emission

### mqlaunch

Äger:

- mänsklig meny
- visning
- kopiering
- preview
- explicit confirmation

`mqlaunch` ska inte innehålla egen ranking, extraction eller learn-logik.

---

## Datatyper

### Observation

En faktisk användningshändelse.

```json
{
  "timestamp": "2026-06-25T20:00:00Z",
  "repo": "macos-scripts",
  "sanitized_command": "git status --short",
  "task_type": "repo-state",
  "outcome": "worked",
  "session_ref": "session-123",
  "pattern_id": "repo-quick-state",
  "note": "Used before safe merge"
}
```

### Command pattern

En återanvändbar kommandotemplate.

```json
{
  "id": "repo-quick-state",
  "name": "Repository quick state",
  "description": "Show branch and working-tree state before changing a repository.",
  "use_when": "Before commits, merges, rebases or branch changes.",
  "avoid_when": "The repository state has already been verified.",
  "command_template": "git status --short && git branch --show-current",
  "risk_class": "read-only",
  "repo_scope": "generic",
  "task_tags": [
    "repo-state",
    "diagnose"
  ],
  "preconditions": [],
  "recovery": "",
  "status": "active"
}
```

### Learn lesson

En generaliserad och verifierad princip.

```json
{
  "id": "learn_safe_mutation_preflight",
  "task": "Safe repository mutation",
  "lesson": "Verify branch and working-tree state before any mutating Git operation.",
  "validation": "Confirmed by regression test and successful repeated use.",
  "risk": "medium",
  "repo": "generic",
  "source": "command-pattern",
  "evidence": [
    "repo-quick-state",
    "gitmerge-safe-smoke"
  ]
}
```

---

## Feedbackloopar

### Förstärkande loop

```text
pattern fungerar
→ används igen
→ får fler positiva observationer
→ rankas högre
→ visas oftare
→ används ännu mer
```

Denna loop måste begränsas så att popularitet inte förväxlas med kvalitet.

### Balanserande loop

```text
not_helped
→ downgrade proposal
→ lägre synlighet
→ mänsklig granskning
→ korrigering eller deprecation
```

### Promotion-loop

```text
flera lyckade observationer
→ stabilt command pattern
→ generell lesson candidate
→ mq-mcp-verifiering
→ curated learn lesson
```

Command-systemet får föreslå en lesson, men aldrig skriva den direkt till canonical learn-store.

---

## Regler

1. Ett enskilt kommando skapar inte ett pattern.
2. Ett pattern kräver återkommande observationer eller tydlig manuell kurering.
3. Frequency betyder inte automatiskt kvalitet.
4. Muterande patterns är dolda som standard.
5. Promotion till learn kräver evidens.
6. Learn-promotion kräver explicit mänskligt godkännande.
7. `mqobsidian` exporterar learn-data read-only.
8. Ingen automatisk tvåvägssynk mellan `mqobsidian` och `mq-mcp`.
9. Rekommenderade command templates får visas eller kopieras, aldrig auto-exekveras.
10. Feedback ska registreras efter verklig användning.

---

## Kommandoyta

### Command observation och patterns

```bash
mqlaunch commands status
mqlaunch commands observations
mqlaunch commands patterns
mqlaunch commands recommend
mqlaunch commands feedback <pattern-id> helped
mqlaunch commands feedback <pattern-id> not-helped
mqlaunch commands rebuild
```

### General learn

```bash
mqlaunch learn status
mqlaunch learn inbox
mqlaunch learn draft <candidate-id>
mqlaunch learn search "<query>"
mqlaunch learn explain <lesson-id>
mqlaunch learn approve <candidate-id>
```

Använd inte samma ord för båda systemen:

- `commands` = observerat terminalbeteende och command patterns
- `learn` = verifierade generaliserade lessons

---

## Statusmodell för command patterns

```text
observed
    ↓
candidate
    ↓
experimental
    ↓
active
    ↓
stale
    ↓
deprecated
```

Promotionregler:

```text
observed → candidate
  minst två liknande observationer

candidate → experimental
  mänsklig kontroll av template, risk och scope

experimental → active
  positiv feedback eller bekräftad lyckad återanvändning

active → stale
  upprepad not_helped, felaktighet eller lång inaktivitet

stale → deprecated
  ersatt, farlig eller inte längre relevant
```

---

## Leverage points

De viktigaste förändringarna är:

1. separata namn: `commands` och `learn`
2. en canonical store per datatyp
3. explicit feedback efter användning
4. ingen automatisk promotion
5. tydlig evidens mellan observation, pattern och lesson
6. ranking som kombinerar frequency, success, reuse, recency och risk

---

## Viktigaste systeminsikt

Command-systemet är inte ett bibliotek som fylls på manuellt.

Det är ett observationssystem:

```text
verkligt beteende
→ mätbara signaler
→ upptäckta mönster
→ säkrare rekommendationer
```

Learn-systemet är nästa abstraheringsnivå:

```text
stabila mönster
→ verifierad generell princip
→ återanvändbar kunskap
```

De ska kopplas i serie, inte slås ihop.

---

## Rekommenderad intervention

Behåll `memory/commands` som systemets insamling och mönsterdetektor.

Gör därefter följande i ordning:

- [ ] Byt operatörsnamn från `learn-promote` till tydliga `commands`- och `learn`-ytor.
- [ ] Dokumentera `observations.jsonl` som canonical command-event store.
- [ ] Dokumentera `patterns.jsonl` som curated command-pattern store.
- [ ] Lägg till explicit command-feedback via `mq-agent`.
- [ ] Låt `feedback.py` fortsätta producera proposals, aldrig skriva direkt.
- [ ] Lägg till en read-only bridge som kan skapa en learn candidate från ett stabilt command pattern.
- [ ] Låt `mq-mcp` verifiera och lagra den generaliserade lesson.
- [ ] Exportera curated lessons ensriktat tillbaka till `mqobsidian`.
- [ ] Lägg till drift- och freshness-check för exporterade vyer.

Målarkitektur:

```text
command usage
    ↓
mqobsidian observations
    ↓
command patterns
    ↓
mqlaunch recommendations
    ↓
usage feedback
    ↓
stable pattern
    ↓
mq-agent proposal
    ↓
mq-mcp verified lesson
    ↓
read-only mqobsidian export
```
