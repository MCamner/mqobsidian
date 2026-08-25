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
