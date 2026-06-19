---
type: index
system: mqobsidian
status: active
tags: [index, system]
updated: 2026-06-20
owner:
links_to: [hot]
---

# mqobsidian Index

## Purpose
Navsidan för `mqobsidian`: MQ-stackens durable memory layer och agent-routade kontextyta.

## Current state
`mqobsidian` lagrar reviewed knowledge, schemas, templates, examples och compact memory. Det kör inte workflows och ska inte ersätta `mq-agent` eller `mq-mcp`. `mq-agent context export` är lokalt implementerat och har rullat ut fem idempotenta, budgeterade context-filer till nio repo. Mqobsidians export är versionshanterad; command-implementationen och övriga exporter är ännu lokala.

## Current priorities
1. Hålla read-order-kedjan liten: agent view -> hot -> index -> små cards.
2. Landa `mq-agent context export` som en avgränsad ändring utan att blanda in pågående cockpit-arbete.
3. Besluta versionshantering för exporter och samla fler effektmätningar.

## Key links
- [[hot]]
- [[../../memory/learn/agent/mqobsidian]]
- [[../../docs/roadmap-token-reduction]]
- [[../../docs/context-budget]]
- [[../../templates/context-pack]]

## Core notes
- [[../../README]] — publik roll och repo-layout.
- [[../../schemas/context-pack.v1]] — task-pack contract.
- [[../../examples/sanitized-context-pack]] — public-safe exempel.
- [[../mq-agent/index]] — orchestration och agent-view regeneration.
- [[../mq-mcp/index]] — bounded MCP tools och runtime contracts.

## Active risks
- Context surfaces kan växa till permanenta token-sänkor.
- Hårdkodade MVP-defaults kan misstas för generell memory query.
- Duplicerad source-repo-dokumentation i vaulten skapar drift.

## Open questions
- Ska repo-lokala `.mq/context/`-exporter versionshanteras i varje målrepo eller regenereras lokalt?
- Vilka verkliga uppgifter ska ingå i nästa mätbatch?

## Recent changes
- 2026-06-20: Rullade lokalt ut fem `.mq/context/`-filer till nio repo; andra körningen gav 45 oförändrade filer och alla låg inom budget.
- 2026-06-20: Verifierade exportstruktur, tokenbudget och 94,8 % first-read-reduktion; nästa ägarskapssteg är `mq-agent context export`.
- 2026-06-18: Wiki freshness för MQ-stackens GitHub Wikis fångades i [[../../memory/stack-truth/2026-06-18-mq-wiki-status]].
- 2026-06-17: `systems/mqobsidian/` skapades för att ge agent-view-kortet en riktig systemkälla.
- 2026-06-17: Token-reduction MVP är dokumenterad i [[../../docs/roadmap-token-reduction]].

## Related systems
- [[../mq-agent/index]]
- [[../mq-mcp/index]]
- [[../mq-ums/index]]

## Navigation rules
- Använd `mqobsidian` för durable memory, agent routing och compact context.
- Använd källrepo eller verktyg för live code behavior, tester, CLI truth och runtime state.
- Stoppa läsning när minsta användbara yta räcker.
