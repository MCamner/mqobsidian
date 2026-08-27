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

Maximum: 8 points per question, 40 total (2 + 2 + 2 + 1 + 1).

**Record every dimension, never only the per-question total.** The decision gate
below is stated per dimension, so per-question totals cannot decide it. Two
systems can tie on a question while failing on different dimensions, and a total
hides which. Each run must produce one row per question *per baseline*:

| Question | Baseline | Ground | Complete | Prov | Abstain | Compact | Total |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |

Scoring compactness once for a whole run is not permitted: it is a per-answer
dimension, and a run-level judgement makes the per-question totals unreadable.

## Decision gate

Proceed beyond the manual one-notebook proof only if **all** of the following
hold. Let `D(system)` be a dimension summed over the five questions, and let the
comparison baseline be the *best-scoring* local baseline on that dimension.

Preconditions — any failure voids the run:

- all five questions are executed against all available baselines
- no forbidden source reaches the provider
- every material claim in the evaluated answers is traceable
- provider failure leaves compact MQ retrieval usable
- scoring followed the blinding procedure below

Decision, evaluated arithmetically from the dimension table:

1. `D(groundedness)` of the candidate is **not lower** than the baseline's.
2. `D(correct abstention)` of the candidate is **not lower** than the baseline's.
3. The candidate exceeds the baseline by **at least 2 points** on
   `D(cross-source completeness)` or on `D(compactness)`.

The 2-point margin on rule 3 is deliberate. Each dimension is scored in whole
points across five questions by one human-directed judgement; a 1-point edge is
inside the noise of a single borderline call and is not evidence of a better
system. Rules 1 and 2 have no margin because they are safety properties, not
performance ones: any measurable loss of groundedness or abstention disqualifies.

**Blinding.** Score each answer without knowing which system produced it: strip
system labels, shuffle the answers per question, and score all three before
revealing the mapping. A run scored unblinded is still recorded, but must state
so and cannot by itself justify proceeding.

If the candidate does not beat the local baselines, keep NotebookLM optional
and do not build incremental sync, automatic routing, or write-back.

### Unique cross-source finding

Frozen before the 12g run so it cannot be fitted to the results:

```text
Unique cross-source finding =
a correct, source-supported conclusion requiring evidence
from at least two distinct source documents/types,
not present in the competing compact-MQ answer,
and not merely a more detailed restatement of the same conclusion.
```

The finding must be verifiable back against the actual sources. A conclusion
that cannot be traced to the cited documents does not count, however impressive
it reads.

### 12g decision procedure

Applied only after blind scoring is complete and the mapping is revealed. All
conditions compose with the dimension rules above; none replaces them.

```text
NotebookLM < 38/40
  -> FAIL / close Phase 12

NotebookLM >= 38/40
but no unique verified cross-source finding
  -> FAIL / close Phase 12

NotebookLM >= 38/40
+ unique verified cross-source finding
+ strictly beats compact MQ
  -> PASS / 12d may open
```

A tie closes the phase. If NotebookLM scores 39, compact MQ 39, and CodeGraph
38, Phase 12 still closes: the roadmap rule is that ties and losses end the
question, and a provider costing 6-7x the context material must win to earn its
failure modes.

### Blind scoring protocol for 12g

The agent that produces the answers does not score them. Self-blinding is not
blinding.

1. Run A, B, and C once each. No prompt changes between systems or after
   seeing any output.
2. Save every answer raw, with the corpus id, content hash, commit, and the
   questions as asked.
3. Present the questions with the three answers labelled `Response X`,
   `Response Y`, `Response Z`, ordered independently per question, to a scorer
   who is not the producing agent.
4. Keep the `X/Y/Z -> system` mapping local and undisclosed until scoring ends.
5. Score against this document's frozen rubric.
6. Only then reveal the mapping and apply the decision procedure above.

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

The verdict survives the gate's later repair. Rule 1 is a safety property with
no margin, and the candidate lost a groundedness point on question 5 that no
baseline lost -- so the run fails on rule 1 alone, whatever the unrecorded
dimension table would have shown for rules 2 and 3.

Per this document's own rule, NotebookLM stays optional. Do not build
incremental sync, automatic routing, or write-back. Roadmap **12f** (cross-repo
contract distribution) is debt that should not be paid: it existed to serve a
consumer that has not earned it.

### Limits of this measurement

Three, stated so the result is not over-read:

1. **The dimension table was never recorded.** Only per-question totals exist,
   so the verdict above was reached from prose, not arithmetic, and no later
   reader can recompute it. The gate is stated per dimension; this run cannot
   be re-evaluated against it, and cannot be compared dimension-by-dimension
   with the `12g` retest. Two facts are recoverable from the totals and are
   worth naming, because they show what a total hides:
   - The candidate lost exactly one point on each of questions 1-4. If that
     point is compactness -- which it must be, at 1704 lines against 250 --
     then the candidate scored *perfectly* on the other four dimensions there.
   - Compact MQ also lost exactly one point on each of questions 1-4, and it
     cannot lose compactness. The document never says what it lost. So
     "questions 1-3 were a draw" is a numeric tie between two systems failing
     on different dimensions, not an equivalence.
2. **Not blind.** The same agent scored the candidate and the baselines.
3. **The corpus was pre-compressed.** All 22 sources are reviewed, distilled
   vault material — context cards exist precisely to compress repo knowledge.
   Asking a synthesis provider to beat local retrieval on the artifacts local
   retrieval already produced is close to a rigged comparison. The provider's
   plausible strength is synthesis over material that has *not* been distilled.

A fair retest is specified in `12g`. This result stands for the reviewed
corpus, not for NotebookLM in general.
