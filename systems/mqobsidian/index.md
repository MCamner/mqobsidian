---
type: index
system: mqobsidian
status: active
tags: [index, system]
updated: 2026-08-25
owner:
links_to: [hot]
---

# mqobsidian Index

## Purpose
Navsidan för `mqobsidian`: MQ-stackens durable memory layer och agent-routade kontextyta.

## Current state
`mqobsidian` lagrar reviewed knowledge, schemas, templates, examples och compact memory. Det kör inte workflows och ska inte ersätta `mq-agent` eller `mq-mcp`. En experimentell NotebookLM consumer profile återanvänder befintliga truth/context-ytor och kompletteras av `notebook-pack.v1`; ingen provideradapter eller export körs från detta repo.

## Current priorities
1. Hålla read-order-kedjan liten: agent view -> hot -> index -> små cards.
2. Samla verkliga `feedback-signal.v1`-utfall och utvärdera precision/recall tillsammans med tokenreduktion.
3. Samla verifierade routingutfall per task class inför en separat evidence review; aktivera inte automatisk routing från otillräckligt underlag.
4. Håll NotebookLM read-only och lokal tills adapterbeteende, dataapproval och ett avgränsat `mq-stack`-experiment är verifierade.

## Key links
- [[hot]]
- [[../../memory/learn/agent/mqobsidian]]
- [[../../docs/roadmap-token-reduction]]
- [[../../docs/context-budget]]
- [[../../docs/context-effect]]
- [[../../docs/FEEDBACK_LOOP]]
- [[../../docs/notebooklm-bridge]]
- [[../../templates/context-pack]]

## Core notes
- [[../../summaries/2026-08-23-mqobsidian-health-and-validation]] — grön lokal validering, reproducerbar Ruff och verifierat evidensgap för retrieval/routing.
- [[../../summaries/2026-08-23-mqobsidian-learn-command-and-search-fix]] — återställd learn/command-kontext och robust MCP-sökresultat i mq-agent.
- [[../../README]] — publik roll och repo-layout.
- [[../../schemas/context-pack.v1]] — task-pack contract.
- [[../../schemas/notebook-pack.v1]] — provenance-kontrakt för valda externa synteskällor.
- [[../../examples/sanitized-context-pack]] — public-safe exempel.
- [[../mq-agent/index]] — orchestration och agent-view regeneration.
- [[../mq-mcp/index]] — bounded MCP tools och runtime contracts.

## Active risks
- Context surfaces kan växa till permanenta token-sänkor.
- Hårdkodade MVP-defaults kan misstas för generell memory query.
- Duplicerad source-repo-dokumentation i vaulten skapar drift.
- Extern syntes kan läcka felklassificerat material om allowlist eller operator approval kringgås.

## Open questions
- Vilka verkliga uppgifter ska ingå i nästa mätbatch?
- Vilka repon får en beslutad publik agentyta (och därmed tracked `.mq/context/`)?
- Får något verkligt MQ-material skickas till NotebookLM, och under vilken organisatorisk dataapproval?

## Recent changes
- 2026-08-25: Lade till `notebook-pack.v1`, read-only `mq-stack-intelligence`-profil, fem fasta evalfrågor och lokal `.notebooklm/`-gräns; CodeGraph-lanen är revision-bunden och fortsatt deferred. `revision` kräver nu `dirty`, så ett manifest inte kan påstå commit-bundet innehåll när sha256 beskriver ocommittat arbetsträd.
- 2026-08-23: Gjorde Ruff 0.16.4 reproducerbar via dev-krav, återställde README-budgetmarginal och bekräftade att verkliga Phase 11c- och routingutfall ännu saknas; se [[../../summaries/2026-08-23-mqobsidian-health-and-validation]].
- 2026-08-23: Återförde tre verifierade mqobsidian-lärdomar till canonical mq-mcp-store, regenererade command/agent-vyer och fixade `mq-agent learn search` för nästlade MCP-resultat; se [[../../summaries/2026-08-23-mqobsidian-learn-command-and-search-fix]].
- 2026-08-19: Utökade `memory-query.v1` additivt med valfria `repositories` för stackövergripande frågor och lade kontraktet under exportvalidering.
- 2026-08-19: Lade till `scripts/eval-retrieval.py` för precision, recall, F1, sufficiency och blockverdicts från `feedback-signal.v1`; freshness mäts separat från relevans.
- 2026-08-04: Lade till en idempotent, fil-låst writer för schema-giltiga `PASS`-routingutfall; lokal historik är gitignorad och kan läsas direkt av `mq-agent route report`.
- 2026-06-23: Phase 11c (feedback-loop) definierad: `feedback-signal.v1`-schema + sanerat exempel + `docs/FEEDBACK_LOOP.md`, gitignorad `feedback/`-yta, CI-validering, och no-auto-publish-garanti (lokal ADR-007). 11a/11b produceras/konsumeras nu i mq-agent (PR #102).
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
