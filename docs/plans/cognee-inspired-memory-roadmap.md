# Evidence-Grounded Hybrid Memory Roadmap

## Goal

Adopt the useful memory patterns demonstrated by Cognee without turning
`mqobsidian` into a memory runtime or weakening MQ's review, provenance and
public-safe boundaries.

The target is not feature parity. The target is better recall with evidence:

```text
authorized source
  -> sanitized observation
  -> reviewed memory candidate
  -> durable memory + provenance projection
  -> hybrid retrieval in shadow mode
  -> bounded context pack
  -> usage feedback and evaluation
```

## Ownership

| Capability | Owner | Boundary |
| --- | --- | --- |
| Memory vocabulary, schemas, provenance contracts and evaluation definitions | `mqobsidian` | Declares truth; runs no live retrieval or ingestion workflow |
| Session lifecycle, task routing, candidate creation and context selection | `mq-agent` | Orchestrates; does not own durable truth |
| Keyword/vector/graph retrieval, parsing adapters and safe tool execution | `mq-mcp` | Runtime; writes only through declared approval and path contracts |
| Source structure and code relationships | CodeGraph / `repo-signal` | Evidence input; never promotes memory |
| Operator health, freshness and degraded-mode reporting | `mq-hal` | Reports; does not select or mutate memory |
| Terminal entrypoints | `macos-scripts` / `mqlaunch` | Thin delegate-only surface |

## Non-goals

- no Cognee fork or embedded Cognee runtime;
- no graph, vector or session database inside `mqobsidian`;
- no automatic promotion from frequency, similarity or model output;
- no capture of raw prompts, tool stdout, credentials, enterprise logs or PHI;
- no ontology generation before a concrete retrieval failure requires it;
- no multi-tenant platform until MQ has more than one defined trust domain;
- no replacement of CodeGraph, OpenAI vector stores or current keyword search.

## Phase 0 — Baseline and decision record

**Owner:** `mqobsidian`  
**Consumers:** `mq-agent`, `mq-mcp`

1. Record current retrieval quality by task class using the existing
   `feedback-signal.v1` evaluation path.
2. Inventory the current keyword, vector, CodeGraph and context-pack retrieval
   surfaces. Identify overlap, blind spots and data-egress boundaries.
3. Define representative MQ queries covering:
   - exact known-item recall;
   - cross-repo relationship recall;
   - temporal conflict and stale-memory handling;
   - negative retrieval where no answer should be returned;
   - public-safe redaction.
4. Write an ADR deciding the minimum graph projection and whether existing
   contracts can represent it. Add a schema only when a named consumer cannot
   use an existing one.

**Exit gate**

- reproducible baseline exists;
- each proposed component has an owner and consumer;
- threat model covers local, OpenAI-hosted and future self-hosted backends;
- no implementation starts from an unmeasured “graph is better” assumption.

## Phase 1 — Provenance graph projection

**Owner:** `mqobsidian` for contract; `mq-agent` for materialization

Create a derived, rebuildable graph over already-reviewed records:

```text
source -> observation -> evidence -> score -> promotion event
       -> durable memory -> context pack -> feedback signal
```

Requirements:

- every node resolves to an existing record or manifest;
- every edge carries relation type, source reference and freshness;
- conflicting or superseded memories remain visible;
- projection files are local, gitignored and disposable;
- deletion of the projection never deletes canonical memory;
- CodeGraph edges remain source metadata and never become promotion evidence.

Start with deterministic JSON adjacency output. Introduce NetworkX, Kuzu or
another graph engine only after the baseline shows that traversal needs it.

**Exit gate**

- projection rebuild is deterministic and idempotent;
- orphan, broken-reference and stale-edge checks pass;
- a reviewer can trace any retrieved memory back to evidence and promotion.

## Phase 2 — Hybrid retrieval in shadow mode

**Owner:** `mq-mcp` runtime; `mq-agent` orchestration; `mqobsidian` evaluation

Run existing retrieval and a candidate hybrid path side by side:

```text
query
  -> keyword candidates
  -> vector candidates when configured
  -> provenance/relationship expansion
  -> deterministic dedupe and bounded ranking
  -> shadow result + retrieval trace
```

The active context path remains unchanged. Shadow output must have zero effect
on prompts, routing and promotion.

Evaluate:

- precision and recall against explicit relevance labels;
- stale or contradicted memory rate;
- provenance coverage;
- context lines/tokens added;
- latency and external API use;
- active-versus-shadow divergence by task class.

**Exit gate**

- hybrid retrieval beats or complements the baseline on named task classes;
- every result has provenance and a freshness state;
- negative queries do not become plausible fabricated answers;
- human approval is required before activating any task class.

## Phase 3 — Session-to-candidate handoff

**Owner:** `mq-agent`; contract owned by `mqobsidian`

Add an ephemeral session layer that can survive compaction without becoming
durable memory automatically.

Lifecycle:

```text
session start -> bounded local state -> compaction checkpoint
-> session end summary -> sanitized memory-observation.v1 candidate
-> normal scoring and review gate
```

Capture only typed facts needed for continuity: task id/class, selected route,
approved decisions, changed artifact references, verified outcome and explicit
user correction. Do not capture full prompts, raw tool traces or source files.

**Exit gate**

- session cache has a retention limit and explicit purge command;
- generated candidates validate against existing contracts;
- secrets/private-path fixtures are rejected;
- session frequency cannot trigger promotion;
- sessions work with memory disabled.

## Phase 4 — Controlled ingestion adapters

**Owner:** `mq-mcp` adapters; `mq-agent` workflow

Add format support only for demonstrated MQ inputs, one adapter at a time:

1. detect format and authorization boundary;
2. parse locally with bounded size and time limits;
3. remove secrets, identifiers and machine-specific paths;
4. deduplicate against source identity and content hash;
5. emit observation candidates, never durable notes;
6. require review before promotion or publication.

Initial candidates should be Markdown, strict JSON/JSONL and public-safe text.
Office, PDF, images, audio and remote URLs remain deferred until a concrete use
case and parser threat model exist.

**Exit gate**

- malformed and adversarial files fail closed;
- re-ingestion is idempotent;
- every candidate records parser/version/source provenance;
- no adapter makes an undeclared network request.

## Phase 5 — Operator visibility and activation

**Owner:** `mq-hal` reporting; owning runtimes expose read-only health

Expose compact status for:

- index/projection freshness;
- retrieval backend availability;
- shadow divergence and evaluation coverage;
- unreviewed candidate count and oldest age;
- session cache retention state;
- degraded mode and safe fallback path.

Activate capabilities independently per task class. Each activation requires:

1. measured evidence from Phase 2;
2. documented data-egress mode;
3. human approval;
4. rollback to the previous retrieval path;
5. post-activation comparison against the same baseline.

## Deferred capability register

| Cognee-like capability | Decision |
| --- | --- |
| Automatic ontology generation | Defer until controlled vocabulary cannot solve a measured retrieval gap |
| Dynamic entity extraction with an LLM | Defer; high false-edge and data-egress risk |
| Interactive graph UI | P2 after provenance projection proves useful |
| Multi-tenant dataset ACL | Defer until a second trust domain is defined |
| Multimodal memory ingestion | Defer; use `mq-image-analyze` outputs as sanitized observations first |
| Pluggable graph/vector backend matrix | Reject for now; support the smallest proven local and configured paths |
| Autonomous `improve` operation | Reject; MQ retains feedback -> evidence -> human-reviewed promotion |

## Delivery slices

Keep implementation as independent PRs:

1. baseline query set and measurement report;
2. architecture ADR and threat model;
3. deterministic provenance projection contract and example;
4. projection materializer plus validation;
5. shadow retrieval trace and comparison report;
6. session cache contract and local implementation;
7. first bounded ingestion adapter;
8. mq-hal health surface;
9. one task-class activation decision.

Do not combine contract creation, runtime activation and backend migration in
one PR.

## Stack-level definition of done

- ownership matches the table above;
- runtime truth stays in source repos and tools;
- canonical memory remains reviewable without graph/vector infrastructure;
- retrieval results are evidence-traceable and freshness-aware;
- disabling the new layer restores current behavior without data loss;
- public-safe, schema, token-budget and retrieval-evaluation gates pass;
- documentation states measured gains and known failure modes, not platform
  parity claims.

## Source inspiration

Cognee concepts used as design input: document ingestion and chunking,
knowledge-graph projection, vector plus graph retrieval, session memory,
feedback, provenance visualization and backend isolation. MQ deliberately keeps
its existing ownership, approval and promotion model rather than copying
Cognee's runtime architecture.
