---
type: index
system: mqobsidian
status: active
tags: [index, system]
updated: 2026-06-22
owner:
links_to: [hot]
---

# mqobsidian Index

## Purpose
Navsidan för `mqobsidian`: MQ-stackens durable memory layer och agent-routade kontextyta.

## Current state
`mqobsidian` lagrar reviewed knowledge, schemas, templates, examples och compact memory. Det kör inte workflows och ska inte ersätta `mq-agent` eller `mq-mcp`. `mq-agent context export` är mergat till `main`; fem idempotenta, budgeterade context-filer har rullats ut till nio repo. Exporter-policyn är nu avgjord (ADR-006): public-safe `.mq/context/`-exporter versionshanteras i målrepo, lokal regen är arbetsmetod, och repo utan beslutad publik agentyta förblir local-only.

## Current priorities
1. Hålla read-order-kedjan liten: agent view -> hot -> index -> små cards.
2. Rulla ut tracked public-safe `.mq/context/`-exporter med drift-gates (ADR-006) och påbörja Phase 11 (negative context, block-metadata).
3. Samla fler effektmätningar från verkliga uppgifter.

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
- Vilka verkliga uppgifter ska ingå i nästa mätbatch?
- Vilka repon får en beslutad publik agentyta (och därmed tracked `.mq/context/`)?

## Recent changes
- 2026-06-22: ADR-006 stänger exporter-frågan — public-safe `.mq/context/` trackas i målrepo; lokal regen är arbetsmetod; local-only-undantag speglar ADR-005 P6. Roadmapen fick Phase 11 (next context-quality layer: negative context, block-metadata, feedback-loop).
- 2026-06-20: `mq-agent context export` landade isolerat i mq-agent PR #92; mqobsidian förblir ägare för cards, budgetkontrakt och public-safe exempel.
- 2026-06-20: Rullade lokalt ut fem `.mq/context/`-filer till nio repo; andra körningen gav 45 oförändrade filer och alla låg inom budget.
- 2026-06-20: Verifierade exportstruktur, tokenbudget och 94,8 % first-read-reduktion inför mq-agents context-export-implementation.
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
