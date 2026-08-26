# MQ Stack Intelligence evaluation

## Purpose

Measure whether NotebookLM adds useful cross-document synthesis beyond compact
mqobsidian retrieval and CodeGraph source discovery. This is an evaluation
specification, not evidence that the provider is useful.

Notebook: `mq-stack-intelligence` / **MQ Stack Intelligence**.

## Source lanes

| Lane | Provider | Status | Meaning |
| --- | --- | --- | --- |
| reviewed | mqobsidian | active | Reviewed decisions, contracts, architecture, and durable knowledge. |
| observed | CodeGraph | deferred | Commit-bound structural code observations; never canonical memory. |

Until the observed lane is implemented, questions requiring current code
comparison must answer that the evidence is unavailable. Correct abstention is
better than an invented conclusion.

## Fixed questions

Each answer must cite at least two source paths and distinguish reviewed facts,
observed facts, interpretation, and recommendation.

1. Which responsibilities belong to mqobsidian, mq-agent, and CodeGraph, and
   where would a NotebookLM exporter violate those boundaries?
2. Which published contracts govern context selection, memory retrieval, and
   NotebookLM source provenance, and how do they relate?
3. Which current roadmap priorities still lack real feedback or routing
   evidence, and what prevents them from being marked complete?
4. Does current code structure contradict any reviewed architecture or
   ownership statement? If the observed CodeGraph lane is unavailable, state
   exactly what cannot be concluded.
5. What security and operational gates must pass before real MQ material is
   uploaded or a remote NotebookLM source is changed?

## Baselines

Run the same questions through:

1. **Compact MQ baseline** — agent view, hot/index, relevant contracts, and no
   NotebookLM.
2. **MQ + CodeGraph baseline** — compact MQ context plus bounded CodeGraph only
   for the current-code question.
3. **NotebookLM candidate** — the approved source pack; observed lane only when
   a repository revision is present.

Record source files read, context lines delivered to the answering agent,
latency, unavailable evidence, and whether every material claim is traceable.
Do not infer token savings from line counts without labelling the result as an
estimate.

## Scoring

| Dimension | Score | Requirement |
| --- | ---: | --- |
| Groundedness | 0–2 | Material claims match cited sources. |
| Cross-source completeness | 0–2 | Uses the independent sources needed by the question. |
| Provenance | 0–2 | Paths and revisions are sufficient to verify the answer. |
| Correct abstention | 0–1 | Missing observed/runtime evidence is stated, not guessed. |
| Compactness | 0–1 | Delivers the answer without unnecessary source or transcript content. |

Maximum: 8 points per question, 40 total.

## Decision gate

Proceed beyond the manual one-notebook proof only if:

- all five questions are executed against all available baselines
- no forbidden source reaches the provider
- every material claim in the evaluated answers is traceable
- provider failure leaves compact MQ retrieval usable
- NotebookLM improves cross-source completeness or compactness without reducing
  groundedness or correct abstention

If the candidate does not beat the local baselines, keep NotebookLM optional
and do not build incremental sync, automatic routing, or write-back.

## Result — 2026-08-26

Executed against all three baselines. Candidate: 22 sources from
`notebook-pack.v1` at commit `2b06cafa`, content hash `ee051683`, no forbidden
source present.

| Question | NotebookLM | Compact MQ | MQ + CodeGraph |
| --- | ---: | ---: | ---: |
| 1 Responsibilities | 7 | 7 | 7 |
| 2 Contracts | 7 | 7 | 7 |
| 3 Roadmap gaps | 7 | 7 | 7 |
| 4 Code contradictions | 7 | 7 | 8 |
| 5 Gates | 6 | 8 | 8 |
| **Total** | **34** | **36** | **37** |

Context delivered: 1704 lines to the provider, 250 lines locally (agent view
41, hot 55, index 80, codegraph card 58, plus a contract table). Questions 3–5
were grounded after 176 lines; only 1 and 2 required expansion.

### Where the differences are

**Question 5 — the candidate lost a groundedness point to a factual error.**
It claimed manifests require "verification that the working directory is not
dirty". The schema requires `dirty` to be *declared*, not to be false. It read
the sentence in `systems/mqobsidian/index.md` and turned a disclosure rule into
a gate. Both baselines read the same sentence and did not.

**Question 4 — CodeGraph won the only point.** All three correctly abstained
from claiming anything about current code. CodeGraph could then actually look:
`validate_notebook_profile` in `scripts/validate-export.py` is a validator, not
an exporter, and no networking library is imported anywhere in `scripts/`. That
is an observed fact neither of the other two could produce.

**Questions 1–3 were a draw** — same claims, same sources, more words.

### Verdict: gate fails

The gate requires the candidate to improve cross-source completeness or
compactness *without* reducing groundedness or correct abstention. The outcome
was the inverse: lower groundedness (one factual error no baseline made) and
7x worse compactness. No question was answered better than locally.

Per this document's own rule, NotebookLM stays optional. Do not build
incremental sync, automatic routing, or write-back. Roadmap **12f** (cross-repo
contract distribution) is debt that should not be paid: it existed to serve a
consumer that has not earned it.

### Limits of this measurement

Two, stated so the result is not over-read:

1. **Not blind.** The same agent scored the candidate and the baselines.
2. **The corpus was pre-compressed.** All 22 sources are reviewed, distilled
   vault material — context cards exist precisely to compress repo knowledge.
   Asking a synthesis provider to beat local retrieval on the artifacts local
   retrieval already produced is close to a rigged comparison. The provider's
   plausible strength is synthesis over material that has *not* been distilled.

A fair retest is specified in `12g`. This result stands for the reviewed
corpus, not for NotebookLM in general.
