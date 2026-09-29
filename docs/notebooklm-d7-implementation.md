# NotebookLM D7 interaction-gap implementation

**Closed:** 2026-09-29  
**Implementation:** `mq-agent` PR #308  
**Merge:** `0d1c66273a9e791fe08041a1e555c5c96a17e335`

## Purpose

Record the completed interaction-history and research-gap layer without changing
the archive evidence hierarchy.

D7 answers questions about prior inquiry:

- what was asked;
- what recurred;
- which notebooks contained the inquiry;
- whether current lexical catalog search finds source, derived or no matching
  material.

It never answers a factual question from interaction history.

## Implemented commands

```text
mq-agent notebook questions --catalog <catalog.json>
mq-agent notebook gaps --catalog <catalog.json>
```

## Question extraction

Only D3 items classified as `interaction` are selectively read.

Extraction is deterministic:

1. split bounded text into candidate utterances;
2. keep question-mark or question-word candidates;
3. normalize prefixes, case and punctuation;
4. deduplicate on the normalized key;
5. derive a stable SHA-256-based question identity.

Each result carries recurrence and notebook counts. Interaction traces remain:

```text
source_role: interaction
claim_eligible: false
evidence_role: inquiry-history-only
```

## Gap states

D7 reuses D4 lexical metadata/text matching and produces:

| State | Meaning |
| --- | --- |
| `NO_SOURCE_EVIDENCE` | no source or derived candidate matched |
| `DERIVED_ONLY` | derived material matched without a source match |
| `STALE_SOURCE_THEME` | matching source candidates exist but all exceed the age threshold |
| `SOURCE_MATCHES_PRESENT` | at least one current-enough source candidate matched |

These states describe retrieval condition only. They do not assert that a
matching source actually answers the question.

## Privacy boundary

Extracted private interaction text may be shown to the local operator by the
command, but D7 has no tracked-output or durable-memory write path.

Repository tests contain synthetic interaction text only.

## Semantic boundary

D7 uses no embeddings and no semantic index. It depends only on deterministic
normalization, D3 roles, D4 lexical matching and timestamps.

That matters for the next phase: D8 remains an experiment, not a dependency.

## Verification

PR #308 passed:

- full pytest suite;
- Ruff lint;
- mypy/type checks;
- docs consistency;
- command-reference consistency;
- macOS runtime/release gate;
- Markdownlint;
- MQ Stack Gate;
- Install smoke test.

The D7-specific tests verify:

- deterministic question extraction;
- deterministic deduplication across notebooks;
- reads restricted to interaction-role files;
- source/derived/missing/stale gap classification;
- no answer field sourced from chat history;
- interaction history remains non-claim-eligible.

## Next-phase gate

D8 semantic retrieval should open only if complete-catalog D4 measurement shows
a named query class where metadata plus provider text matching fails a named
metric.

No semantic layer should be implemented merely because D7 is complete.
