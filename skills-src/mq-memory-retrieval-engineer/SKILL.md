---
name: mq-memory-retrieval-engineer
description: Use when designing, reviewing, or improving local-first evidence-based memory retrieval for mqobsidian, including observation scoring, deduplication, promotion, chunking, metadata, command-score, and compressed agent context.
---

# MQ Memory Retrieval Engineer

Use this skill when the task involves `mqobsidian` memory architecture, evidence-based memory, retrieval, scoring, deduplication, promotion rules, chunking, metadata, or agent-facing context.

## Principle

Make Obsidian the inspectable source of truth for durable operational knowledge gathered from real work. Do not treat this as a generic vector database problem.

## Ownership

```text
mqobsidian = durable notes, schemas, templates, context cards, examples, compact memory surfaces
mq-agent = context selection, pack generation, export, orchestration, agent-view regeneration
mq-mcp = execution runtime, tools, safety metadata
repo-signal = readiness, security posture, public-safe scoring
macos-scripts = macOS CLI tooling and launchers
```

Do not reimplement `mq-agent` or `mq-mcp` behavior inside the vault. When runtime truth matters, verify in the source repo or through the appropriate tool.

## Best use cases

- `mqobsidian` memory structure
- Evidence-Based Memory System
- memory inbox and promotion
- command-score and pattern-score design
- observation scoring
- repo-specific learn files
- Claude/Codex/ChatGPT/repo-signal ingestion
- durable memory
- Obsidian as source of truth
- local retrieval
- markdown chunking
- metadata schemas
- deduplication
- compressed agent context
- semantic search planning
- vector database evaluation only after local retrieval pain is proven

## Read order

Read the smallest useful context and stop when grounded:

1. `memory/learn/agent/<repo>.md` if present
2. `systems/<system>/hot.md`
3. `systems/<system>/index.md`
4. directly relevant notes in `summaries/`
5. `memory/context-cards/<repo>-card.md` when context-card routing matters
6. `docs/CONTEXT_CONTRACT.md`
7. `docs/context-export-contract.md`
8. `docs/FEEDBACK_LOOP.md`
9. relevant files in `memory/commands/`
10. full pattern notes only when compressed views are insufficient

Do not read the entire vault unless the task explicitly requires it.

## Core question

The system must answer:

```text
What have we learned from real work, and how confident are we that it should affect future agent behavior?
```

Do not treat every observation as permanent memory.

Memory becomes stronger when it is:

- repeated
- linked to real work
- tied to a repo
- tied to a command or workflow
- supported by evidence
- useful for future decisions
- not contradicted by newer evidence

## Memory layers

1. Raw observations
   Untrusted notes from agents, tools, reviews, command output, or user input.

2. Scored observations
   Observations with source, repo, frequency, confidence, and usefulness.

3. Promoted memory
   Durable knowledge accepted into memory.

4. Agent context
   Compressed, task-specific memory exported to Claude, Codex, ChatGPT, mq-agent, or other tools.

Avoid turning noise into doctrine.

## Recommended flow

Use this default flow unless the repo defines another one:

```text
event / run / tool output
  -> observation inbox
  -> dedupe by content hash + normalized text + repo context
  -> score by frequency + source + confidence + usefulness
  -> candidate memory
  -> promotion review
  -> permanent memory / learn note
  -> compressed agent context
```

Deduplicate before scoring.

## Metadata standard

Every durable memory should explain why it exists.

```yaml
id: stable-id-or-content-hash
type: observation | pattern | rule | decision | warning | command-score
repo: mq-agent | mq-mcp | mqobsidian | macos-scripts | repo-signal | unknown
source: claude | codex | chatgpt | repo-signal | mq-agent | human | test | review
created: YYYY-MM-DD
updated: YYYY-MM-DD
confidence: low | medium | high
frequency: number
status: inbox | candidate | promoted | deprecated | rejected
evidence:
  - path-or-run-id
related:
  - memory-id
```

Inbox items can have incomplete metadata. Promoted memory should not.

## Scoring model

Keep scoring simple before making it clever.

Useful signals:

- frequency
- source quality
- repo relevance
- actionability
- recency
- contradiction
- noise level

Suggested shape:

```text
score =
  frequency_weight
+ source_weight
+ actionability_weight
+ repo_relevance_weight
+ recency_weight
- contradiction_penalty
- noise_penalty
```

Suggested default promotion rule:

```text
Promote automatically only when:
- frequency >= 15
- contradiction_penalty == 0
- actionability is medium or high
- at least one concrete evidence link exists
```

High-risk memories require human review even when frequency is high.

## Chunking strategy

For Obsidian Markdown, prefer structure-aware chunking:

1. file
2. heading
3. subsection
4. bullet group
5. fenced block only when needed

Avoid blind fixed-size chunking as the first strategy.

Preserve note path, heading path, repo, memory type, date, tags, links, and evidence references.

Suggested chunk ID:

```text
<repo>/<relative-path>#<heading-slug>/<content-hash>
```

## Deduplication rules

Use:

- exact hash for identical observations
- normalized text hash for formatting changes
- repo + command + error signature when available
- semantic similarity only as a secondary signal

Do not merge observations that look similar but have different causes. When uncertain, group them as related instead of merging.

## Retrieval rules

For any task, retrieve in this order:

1. repo-specific agent view or hot memory
2. repo-specific learn memory
3. relevant decisions
4. relevant command-score patterns
5. relevant prior reviews
6. broader MQ-stack memory only if needed

Prefer small, high-signal context over large dumps.

A useful retrieval result explains what was found, why it matters, confidence, evidence location, and whether it is current.

## Local-first rule

Default path:

1. Markdown files
2. frontmatter metadata
3. content hashes
4. ripgrep
5. SQLite index if needed
6. local embeddings if keyword search becomes insufficient
7. vector database only after retrieval pain is proven

Do not recommend Pinecone, Qdrant, Weaviate, FAISS, or pgvector as the first step unless the user explicitly asks or the need is proven.

## Agent context output

Good agent-facing memory includes current repo facts, active risks, repeated patterns, relevant commands, recent decisions, known mistakes to avoid, and evidence links.

Bad agent-facing memory includes full vault dumps, duplicate observations, old speculation, unrelated history, unsourced claims, and memories without confidence.

## Promotion rules

Promote memory when it is likely to improve future work.

Promote if it is repeated, evidence-backed, actionable, current, not contradicted, and relevant to future agent behavior.

Reject or keep in inbox if it is one-off, vague, already captured, contradicted, missing repo/source context, or emotional but not operational.

Deprecate old memory instead of deleting it when it may explain past decisions.

## Output format

Use this shape when it helps:

```md
## Goal
<what memory problem is being solved>

## Key findings
<what matters>

## Recommendation
<best design or change>

## Proposed rule / schema / flow
<actual rule, schema, or flow>

## Files affected
<likely files or folders when known>

## Verification
<how to check that it works>

## Next step
<one concrete next action>
```
