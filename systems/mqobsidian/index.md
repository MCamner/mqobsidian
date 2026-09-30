---
type: index
system: mqobsidian
status: active
tags: [index, system]
updated: 2026-09-17
owner:
links_to: [hot]
---

# mqobsidian Index

## Purpose
Navsidan för `mqobsidian`: MQ-stackens durable memory layer och agent-routade kontextyta.

## Current state
`mqobsidian` lagrar reviewed knowledge, schemas, templates, examples och compact
memory. Det kör inte workflows och ska inte ersätta `mq-agent` eller `mq-mcp`.
`v0.4.0` (2026-09-11) stängde Execution and Routing Contract Integrity: ADR-010
delade routing per modellanrop, `mq.model-route-outcome.v1` är kanoniskt här,
`application` och `execution_run_id` skiljer tillämpad routing från råd, och
`.mq/repo-contract.json` deklarerar nu 33 kontrakt som grindas mot `schemas/` i
båda riktningar. Task-aware skill selection har kontrakt men ingen exekvering
här. Det är en kontraktsgrund, inte levererad Execution Intelligence: fallback
recording, aktiv-vs-shadow-divergens och hela det human-gated policylagret är
öppna. Phase 12 och ownership-spåret (DEC-005) är stängda. NotebookLM-spåret D3–D8
är implementerat i `mq-agent` och förblir opt-in: `mq.notebook-corpus-index.v1`
är kanoniskt här, exekveringen ligger där, och dataapproval är öppen.

## Current priorities
1. Regenerera steg 0 när hot eller index ändras; read-order-kedjan ska vara liten och sann.
2. Skaffa applied-evidens från fler än en task; de 14 överförda posterna är alla samma `docs-review`-beslut.
3. Samla execution outcomes per task class och route; underlaget domineras i dag av task class `docs`.
4. Rapportera aktiv-vs-shadow-divergens innan någon kandidatpolicy bedöms.
5. Samla verkliga `feedback-signal.v1`-utfall och utvärdera precision/recall tillsammans med tokenreduktion.

## Key links
- [[hot]]
- [[../../memory/learn/agent/mqobsidian]]
- [[../../docs/roadmap-token-reduction]]
- [[../../docs/context-budget]]
- [[../../docs/context-effect]]
- [[../../docs/FEEDBACK_LOOP]]
- [[../../docs/notebooklm-bridge]]
- [[../../docs/ROUTING_OUTCOMES]]
- [[../../docs/skill-selection]]
- [[../../templates/context-pack]]

## Core notes
- [[../../summaries/2026-08-23-mqobsidian-health-and-validation]] — grön lokal validering, reproducerbar Ruff och verifierat evidensgap för retrieval/routing.
- [[../../summaries/2026-08-23-mqobsidian-learn-command-and-search-fix]] — återställd learn/command-kontext och robust MCP-sökresultat i mq-agent.
- [[../../README]] — publik roll och repo-layout.
- [[../../schemas/context-pack.v1]] — task-pack contract.
- [[../../schemas/notebook-pack.v1]] — provenance-kontrakt för valda externa synteskällor.
- [[../../schemas/mq.model-route-outcome.v1]] — kanoniskt routingkontrakt (ADR-010).
- [[../../schemas/mq.execution-outcome.v1]] — exekveringsobservation; `route` deprekerad.
- [[../../examples/sanitized-context-pack]] — public-safe exempel.
- [[../mq-agent/index]] — orchestration och agent-view regeneration.
- [[../mq-mcp/index]] — bounded MCP tools och runtime contracts.

## Active risks
- Överföringen till `routing/outcomes.jsonl` är manuell, så vault och runtime-store glider isär tyst mellan körningar.
- Ett underlag dominerat av en task class ser ut som routingevidens utan att kunna jämföra routes.
- Kontrakt kan vara kompletta i båda ändar utan att sömmen körs; en tom yta bevisar ingenting.
- Context surfaces kan växa till permanenta token-sänkor.
- Hårdkodade MVP-defaults kan misstas för generell memory query.
- Duplicerad source-repo-dokumentation i vaulten skapar drift.
- Extern syntes kan läcka felklassificerat material om allowlist eller operator approval kringgås.

## Open questions
- Vilka verkliga uppgifter ska ingå i nästa mätbatch?
- Är `repo_scope` rätt dimension? Öppen som research node, inte som åtagande (#97).
- När finns tillräckligt med `applied`-poster per route för att divergensrapporten säger något?
- Vilka repon får en beslutad publik agentyta (och därmed tracked `.mq/context/`)?
- Får något verkligt MQ-material skickas till NotebookLM, och under vilken organisatorisk dataapproval? (Teknisk nytta är nu mätt och utebliven; frågan kvarstår organisatoriskt.)

## Recent changes
- 2026-09-30: `mq.semantic-refresh.v1` landade (#124) och gjorde registret 33 kontrakt. Kontraktet definierar logisk identitet (repo + artifact_type), authority, replacement semantics och en postcondition: exakt en aktiv generation i den auktoritativa store-mängden och ingen retrieval-auktoritativ generation utanför den. `mq-agent` implementerade latest-only refresh, konvergensväntan och legacy-avveckling (#312–#314), och `memory status` skiljer nu `configured`, `reachable` och `fresh` med källrevision som grund. Freshness-gaten täcker nu även kontraktsantalet i hot och index — det påståendet hade glidit två gånger med gröna gates.
- 2026-09-29: NotebookLM D3–D8 stängdes i `mq-agent` (#307–#309) och registrerades här som implementationsposter. `mq.notebook-corpus-index.v1` (#114) gjorde registret 32 kontrakt. D8 är ett opt-in semantiskt experiment mot den frysta D4-lexikala baslinjen, med lokal `nomic-embed-text` via Ollama och ingen hostad embedding-egress; det är inte en aktiverad default-retrievalväg. Den organisatoriska dataapprovalfrågan är oförändrad.
- 2026-09-17: Refreshade hot/index till v0.4.0-läget och överförde de 14 `applied`-posterna (130 -> 144). Write-gaten avvisade fem av dem: `record-routing-outcome.py` krävde `model_output_received=true` på varje PASS, ett krav från tiden före ADR-010 D8 när varje route var ett modellanrop. `deterministic-local` kör ingen modellinferens, så kravet avvisade den enda sanna post en sådan körning kan skriva. Invarianten är nu route-medveten i båda riktningar — en deterministisk route får inte heller påstå mottagen modelloutput.
- 2026-09-13: Regenererade agent views efter learn-refresh (#106) och bevarade 2026-08-04-inventeringen av vector stores som research node.
- 2026-09-11: **`v0.4.0` släppt** — Execution and Routing Contract Integrity (#105). Roadmapen gjordes sann efter v0.3.0 (#104), och ett odeklarerat schema äger inget: `mq.model-route-outcome.v1` hade schema, tester, docs och beslutspost men saknades i `.mq/repo-contract.json`, och kontraktsgrinden gick kedjan i bara en riktning. Båda är fixade (#103). Registret deklarerade då 31 kontrakt.
- 2026-09-10: Taggen är releasen — `v*` publicerar med noter ur changelog-sektionen (#101), och en trunkerad sektion faller högt i stället för att publicera något som inte är den kanoniska beskrivningen (#102).
- 2026-09-07: `mq.execution-outcome.v1` fick valfri `runtime_fingerprint` (#100) med DEC-006 som beslut: additiv utökning, inte v2 — historiska poster förblir giltiga och frånvaro betyder att proveniens inte observerades (#99). Task-aware skill selection fick kontrakt: `mq.skill-profile.v1`, `mq.skill-route.v1`, `skill-selection-vocabulary.v1` (#98).
- 2026-09-05: Öppnade research node om huruvida `repo_scope` är rätt dimension (#97).
- 2026-08-29 → 09-04: ADR-010 landade i fem steg. Routing- och execution-outcomes blev kanoniska här i stället för att lösas från ett sibling-checkout (#90); `execution_run_id` korrelerar observation med exekvering (#91); `application` skiljer tillämpad routing från råd och deprekerar `execution.route` (#92); en route är en exekveringsstrategi, inte en modell (#94); ett brutet kontextfönster blev uttryckbart i stället för tyst (#95); och en modell som fick slut på tid var inte otillgänglig (#96).
- 2026-08-28: Mergeade mq-agent PR #206. `mq.execution-outcome.v1` skrivs best-effort från betydande entrypoints, roteras vid 10 MiB med tre historikfiler och kan stängas av. `execution report`, `execution compare` och `route readiness` rapporterar data utan automatisk routeändring; eligibility är 30 observationer, 2 routes, 14 dagar och 10 per route.
- 2026-08-28: Mergeade #85 med gröna `main`-kontroller och stängde Phase 12-follow-ups. Lade till `mq.execution-outcome.v1` med schema, public-safe exempel, exportvalidering och kontraktstest. Roadmapen går nu vidare med observation, deskriptiv inspektion, shadow routing och först därefter human-godkända routingexperiment.
- 2026-08-27: **Phase 12 stängd.** 12g kördes en gång under fryst protokoll — 35 spårade public-safe källor, kall lokal baslinje, blind poängsättning. NotebookLM fick 17/40 mot 40 och 39; grinden krävde 38. Sämre än 12c trots 21x materialet. Två failure modes väger tyngre än siffran: providern svarade från ett föråldrat systemtillstånd på Q3 (2/8) med roadmapfilen i sin egen korpus, och besvarade inte Q5 alls (0/8). Det enda äkta cross-source-fyndet kom från CodeGraph-baslinjen, inte providern. 12d och 12e stängda; se [[../../docs/notebooklm-evaluation]].
- 2026-08-27: Slöt två tomma sömmar. `feedback-signal.v1` hade kontrakt i båda ändar men ingen producent — `mq-agent context feedback` emitterar nu poster (mq-agent #209), och `scripts/eval-retrieval.py` har data för första gången. Routingutfallen fanns hela tiden i `~/.mq-agent/route-outcomes.jsonl`; de 130 posterna är nu överförda till `routing/outcomes.jsonl` via write-gaten. Routing är `NOT_ELIGIBLE` på verifieringsgrad 0,434, inte på datamängd: 72 av 74 eskaleringar är `verification-failed`, och grinden kräver att varje evidence-item är ordagrant — uppmätt 70 % korrekta citat ger 33 % godkända svar.
- 2026-08-26: Körde NotebookLM-proven mot alla tre baslinjer: 34/40 mot 36 och 37. Beslutsgaten faller — provider förblir valfri, ingen sync/routing/write-back, och skuld 12f ska inte betalas. Ett faktafel i kandidatens svar (dirty som gate i stället för deklaration) och 1704 levererade rader mot 250 lokalt. Rättvist omtest på odestillerat material specas i roadmap 12g; se [[../../docs/notebooklm-evaluation]].
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
