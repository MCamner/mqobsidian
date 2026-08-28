---
type: agent-view
system: mqobsidian
generated: 2026-08-28
generator: mq-agent agent-views rebuild
sources: [systems/mqobsidian/hot.md, systems/mqobsidian/index.md, memory/learn/repos/mqobsidian.md]
---

# mqobsidian — agent view

Compressed first-stop for agents (read-order step 0). Generated — do not
edit by hand; re-run `mq-agent agent-views rebuild`.

## Current state

Hålla MQ-stackens durable memory tunn och public-safe, samt ge execution intelligence en stabil kontraktsgrund utan att flytta runtime till vaulten. Phase 12 och dess ownership-, CodeGraph mismatch- och contract-integrity-spår är stängda. `mq.execution-outcome.v1` är kontrakterat och validerat. mq-agent PR #206 är mergead med writer, execution report/compare…

## Active priorities

- Hålla read-order-kedjan liten: agent view -> hot -> index -> små cards.
- Samla verkliga `feedback-signal.v1`-utfall och utvärdera precision/recall tillsammans med tokenreduktion.
- Samla execution outcomes per task class och route; omätta räknare är okända, inte noll.
- Rapportera aktiv-vs-shadow-divergens innan någon kandidatpolicy bedöms.

## Current blockers

- Inga bekräftade blockers.
- Context surfaces kan växa till permanenta token-sänkor.
- Hårdkodade MVP-defaults kan misstas för generell memory query.
- Duplicerad source-repo-dokumentation i vaulten skapar drift.

## Relevant lessons

- Document and verify CodeGraph CLI query patterns for mqobsidian
- Prove the mqobsidian token-reduction MVP with one real context pack before broad rollout
- Keep mqobsidian context-export cleanup ownership-based and idempotent

## Read next

- [[systems/mqobsidian/hot]]
- [[systems/mqobsidian/index]]
