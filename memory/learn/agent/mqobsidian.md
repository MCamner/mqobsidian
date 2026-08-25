---
type: agent-view
system: mqobsidian
generated: 2026-08-25
generator: mq-agent agent-views rebuild
sources: [systems/mqobsidian/hot.md, systems/mqobsidian/index.md, memory/learn/repos/mqobsidian.md]
---

# mqobsidian — agent view

Compressed first-stop for agents (read-order step 0). Generated — do not
edit by hand; re-run `mq-agent agent-views rebuild`.

## Current state

Hålla MQ-stackens durable memory tunn, public-safe och billig för agenter att läsa. `mqobsidian` är kunskapslagret, inte exekverings- eller orchestrationlagret. En experimentell, read-only NotebookLM consumer profile och `notebook-pack.v1` finns nu som public-safe kontraktsyta. Ingen adapter, export, sync eller automatisk routing är aktiverad.

## Active priorities

- Hålla read-order-kedjan liten: agent view -> hot -> index -> små cards.
- Samla verkliga `feedback-signal.v1`-utfall och utvärdera precision/recall tillsammans med tokenreduktion.
- Samla verifierade routingutfall per task class inför en separat evidence review; aktivera inte automatisk routing från otillräckligt underlag.
- Håll NotebookLM read-only och lokal tills adapterbeteende, dataapproval och ett avgränsat `mq-stack`-experiment är verifierade.

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
