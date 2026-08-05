---
type: agent-view
system: mqobsidian
generated: 2026-08-05
generator: mq-agent agent-views rebuild
sources: [systems/mqobsidian/hot.md, systems/mqobsidian/index.md, memory/learn/repos/mqobsidian.md]
---

# mqobsidian — agent view

Compressed first-stop for agents (read-order step 0). Generated — do not
edit by hand; re-run `mq-agent agent-views rebuild`.

## Current state

Hålla MQ-stackens durable memory tunn, public-safe och billig för agenter att läsa. `mqobsidian` är kunskapslagret, inte exekverings- eller orchestrationlagret. Budgetkontraktet och CI-vakten mot stale exempel är mergade till `main`. En lokal writer kan nu lagra schema-giltiga routingutfall i append-only JSONL utan rå modelloutput; negativa utfall…

## Active priorities

- Hålla read-order-kedjan liten: agent view -> hot -> index -> små cards.
- Phase 11-kontraktet (11a negative context, 11b block-metadata, 11c feedback-loop) är klart här och producerat/konsumerat i mq-agent (PR #102)…
- Samla verifierade routingutfall per task class inför en separat evidence review.

## Current blockers

- Inga bekräftade blockers.
- Context surfaces kan växa till permanenta token-sänkor.
- Hårdkodade MVP-defaults kan misstas för generell memory query.
- Duplicerad source-repo-dokumentation i vaulten skapar drift.

## Relevant lessons

- Document CodeGraph CLI query patterns in mqobsidian integration docs and test-run the tool

## Read next

- [[systems/mqobsidian/hot]]
- [[systems/mqobsidian/index]]
