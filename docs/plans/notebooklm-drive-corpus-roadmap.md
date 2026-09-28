# Drive-Backed NotebookLM Corpus Roadmap

## Goal

Turn the existing NotebookLM archive in Google Drive into an evidence-aware,
selectively retrievable external research corpus for the MQ stack without
making NotebookLM canonical memory, reopening it as an intelligence provider,
or copying the archive into Git.

The target flow is:

```text
Google Drive / NotebookLM archive
  -> deterministic local catalog
  -> source-role classification
  -> bounded search
  -> selective fetch
  -> provenance-bearing answer or research candidate
  -> optional reviewed distillation into mqobsidian
```

The value is not "more NotebookLM". The value is making already-owned research
material discoverable across notebooks while preserving the same truth
boundaries used elsewhere in MQ.

## Why this is a new use case

Phase 12 evaluated NotebookLM as a synthesis and retrieval provider over MQ
material. That evaluation stays closed: the provider did not earn a place in
the active read path.

The new capability is materially different. A large mixed NotebookLM archive
now exists in Google Drive and can be addressed as stored research material.
The archive contains different evidence classes:

```text
SOURCE
  original or collected documents

DERIVED
  NotebookLM-generated reports, guides, presentations, summaries, audio/video

INTERACTION
  exported chat/session material and prior questions
```

The roadmap therefore treats Google Drive as external corpus storage and
NotebookLM output as one class of artifact inside that corpus. It does not use
NotebookLM as the answering engine.

## Existing contract relationship

This track does not repurpose `notebook-pack.v1`.

`notebook-pack.v1` describes the opposite direction:

```text
approved MQ sources -> deterministic pack -> optional external synthesis provider
```

The Drive corpus needs a separate contract because its direction and truth
semantics are different:

```text
Google Drive archive -> local metadata index -> selective read -> answer/research
```

A future `notebook-corpus-index.v1` may describe that local index if Phase 1
shows a real consumer need. Do not create the schema merely because the name is
available.

## Ownership

| Capability | Owner | Boundary |
| --- | --- | --- |
| Corpus vocabulary, source roles, provenance rules, evaluation definitions | `mqobsidian` | Defines durable contracts and public-safe examples; stores no live Drive corpus |
| Catalog build, query planning, source selection and research orchestration | `mq-agent` | Orchestrates reads; does not own external source truth |
| Authorized Drive read adapter | connector or `mq-mcp` adapter when required | Reads only the explicitly configured corpus; no implicit write-back |
| Raw archive files and folder structure | Google Drive | External storage; not canonical MQ memory |
| NotebookLM-generated artifacts | external derived material | May aid navigation and synthesis but never outrank original sources |
| Reviewed durable conclusions | `mqobsidian` normal research/memory workflow | Enter only through existing review and promotion boundaries |
| Operator status and degraded-mode reporting | `mq-hal`, later | Reports freshness and connector health; does not select evidence |

## Core invariants

1. **Drive stores the corpus; mqobsidian stores contracts and reviewed
   distillation.** Raw archive content is not copied into this repository.
2. **Source role is explicit.** Original sources, derived NotebookLM artifacts
   and chat/session exports are never silently treated as equivalent evidence.
3. **Derived content cannot strengthen its own source.** A NotebookLM summary
   may locate a claim, but the claim is grounded in the underlying source when
   that source is available.
4. **Interaction history is not evidence.** Chat/session material may reveal
   repeated questions or research gaps, but it cannot establish a factual claim.
5. **Read the smallest useful set.** Search and catalog metadata come before
   file fetch; a query does not scan or download the whole archive.
6. **No automatic promotion.** A cross-notebook synthesis is an answer or a
   candidate, never durable truth by frequency or model confidence alone.
7. **No write-back by default.** Cataloging, search and research are read-only
   against Drive. Rename, move, delete, share or source mutation require a
   separate explicit capability and approval.
8. **Semantic retrieval is earned by measurement.** No vector store or
   embedding pipeline is added until metadata and text search show a measured
   retrieval gap.

## Non-goals

- do not rebuild NotebookLM inside MQ;
- do not reopen NotebookLM as an active routing or synthesis provider;
- do not download or unzip the full archive locally as the normal workflow;
- do not commit Drive IDs, raw corpus text, chat transcripts or generated
  catalog contents to the public repository;
- do not treat NotebookLM reports, guides or presentations as primary evidence;
- do not treat chat/session exports as evidence;
- do not vectorize the entire archive before a baseline exists;
- do not let corpus search bypass current code/runtime truth when the question
  is about live MQ behavior;
- do not create a second durable-memory or promotion plane.

## Phase 0 — Corpus baseline and ownership decision

**Owner:** `mqobsidian` for definitions; `mq-agent` for measurement

Establish what the archive actually is before designing retrieval around it.

Tasks:

- [ ] inventory the configured Drive corpus by folder, MIME type, file count,
  size and modification time without reading every file body;
- [ ] identify how notebook boundaries are represented by parent folders and
  exported metadata;
- [ ] measure duplicates and repeated generated artifacts without deleting them;
- [ ] sample several notebooks and record which artifacts can be classified
  reliably as source, derived or interaction;
- [ ] define a small sanitized query set for later retrieval measurement;
- [ ] write a decision record for the external-corpus boundary only if the
  ownership table above conflicts with an existing accepted decision.

Do not infer that a filename or extension proves authority. Classification
rules must be explicit and overridable.

**Exit gate**

- the configured corpus root is known locally;
- notebook-to-file relationships can be reconstructed deterministically;
- a representative sample has explicit source roles;
- no raw corpus content or Drive identifier is required in tracked files;
- the baseline query set exists before search implementation starts.

## Phase 1 — Corpus catalog contract

**Owner:** `mqobsidian` for contract; `mq-agent` for materialization

Define the smallest local catalog needed for navigation. Candidate fields are:

```text
corpus / notebook identity
Drive file identity
title
MIME type
size
modified time
parent relationship
source role: source | derived | interaction
origin/provider
optional content hash when actually measured
classification confidence or explicit override provenance
```

The real generated catalog is local and disposable. A tracked schema and
sanitized example are justified only when a named consumer needs a stable
format.

Requirements:

- deterministic ordering;
- stable notebook identity independent of display-name changes where possible;
- no file body in the catalog;
- no credential, connector token or sharing metadata;
- explicit unknown classification rather than guessed source authority;
- duplicate detection reports relationships but never deletes files.

**Exit gate**

- rebuilding unchanged metadata produces the same logical catalog;
- every catalog record maps back to exactly one Drive item;
- unknown source role remains representable;
- deleting the local catalog loses no canonical knowledge.

## Phase 2 — Incremental, quota-aware Drive inventory

**Owner:** authorized read adapter; orchestration in `mq-agent`

Build a resumable reader rather than a full rescan/download loop.

Flow:

```text
configured corpus root
  -> list metadata
  -> checkpoint page/cursor
  -> compare file id + modified time
  -> update changed catalog rows
  -> leave unchanged files unread
```

Requirements:

- Drive reads are scoped to the configured corpus root;
- pagination state is opaque and passed back unchanged;
- rate-limit and transient failures stop or back off without corrupting state;
- retries never duplicate catalog records;
- a partial scan is labelled partial, never current;
- deleted or inaccessible items become missing/stale state rather than erased
  history;
- the default operation is read-only.

**Exit gate**

- an interrupted scan resumes without starting over;
- an unchanged second scan reads materially less content than the first;
- quota/rate-limit failure produces a truthful partial state;
- no Drive mutation is required to maintain the index.

## Phase 3 — Metadata and text search baseline

**Owner:** `mq-agent`

Start with simple retrieval before adding embeddings.

Provisional operator surface:

```text
mq-agent notebook catalog
mq-agent notebook search "<query>"
mq-agent notebook show <notebook-or-result>
```

The exact command names are not a contract until implemented.

Search order:

```text
query
  -> notebook/title/topic metadata
  -> Drive text search where available
  -> bounded candidate set
  -> source-role ordering
  -> selective file fetch only when needed
```

Measure:

- top-k relevance against the Phase 0 query set;
- number of notebooks and files considered;
- number and bytes of file bodies fetched;
- latency and connector calls;
- source/derived/interaction mix in returned candidates.

**Exit gate**

- relevant material is found without reading the full corpus;
- retrieval traces explain why each candidate was selected;
- source-role ordering is visible;
- a no-result query remains a no-result rather than broadening until something
  plausible appears.

## Phase 4 — Evidence-aware selective retrieval

**Owner:** `mq-agent`; provenance rules owned by `mqobsidian`

Fetch only the material needed to answer the current question.

Evidence precedence:

```text
original/collected source
  > derived NotebookLM artifact
  > interaction/chat history
```

This is not a universal quality ranking. It is an authority rule for claims
about what the stored material supports.

Requirements:

- every quoted or paraphrased material claim resolves to notebook + Drive file
  - source role;
- a derived artifact is labelled derived in output;
- when a derived artifact points to an available source, ground the claim in the
  source before presenting it as established;
- conflicting sources stay visible rather than being merged into one story;
- missing source evidence is reported as missing;
- live-code or runtime questions are delegated to current source/runtime tools,
  not answered from an old notebook.

**Exit gate**

- every answer has a provenance trace for material claims;
- derived content cannot masquerade as original evidence;
- interaction material cannot become claim evidence;
- provider/connector failure degrades to a readable unavailable state.

## Phase 5 — Cross-notebook research

**Owner:** `mq-agent`

Add synthesis only after selective retrieval is reliable.

Provisional surface:

```text
mq-agent notebook research "<question>"
```

A research result should separate:

- common findings supported by independent sources;
- disagreements and conflicting source claims;
- source evidence;
- NotebookLM-derived interpretations;
- unanswered questions and missing evidence.

A cross-source conclusion requires at least two distinct source documents when
the conclusion is presented as cross-source. More files from the same generated
artifact chain do not count as independent evidence.

**Exit gate**

- cross-notebook answers can name which independent sources support each
  synthesis;
- disagreements are not averaged away;
- a derived artifact cannot satisfy the independent-source requirement by
  repeating its source;
- the result can be saved as a review candidate without becoming durable memory
  automatically.

## Phase 6 — Interaction-history and research-gap analysis

**Owner:** `mq-agent`

Use chat/session exports for what they are good at: describing prior inquiry,
not proving facts.

Provisional capabilities:

```text
mq-agent notebook questions
mq-agent notebook gaps
```

Candidate outputs:

- recurring questions;
- topics revisited across notebooks;
- questions that repeatedly ended without source evidence;
- areas where only derived material exists;
- stale research themes whose sources have not been refreshed.

Never report "the answer is X" because a previous chat said X.

**Exit gate**

- every gap traces to interaction history without promoting it to evidence;
- repeated questions are deduplicated deterministically;
- private chat text is not copied to tracked artifacts;
- gap output is useful without requiring semantic embeddings.

## Phase 7 — Optional semantic retrieval evaluation

**Owner:** runtime retrieval component; evaluation owned by `mqobsidian`

Open this phase only if Phase 3 measurements show a real search failure that
metadata plus Drive text search cannot solve.

Candidate design:

```text
selected text-capable files
  -> bounded chunks
  -> disposable local semantic index
  -> query
  -> candidate ids
  -> source-role and provenance filter
  -> selective Drive fetch
```

Requirements:

- index entries retain Drive file identity and chunk provenance;
- deletion of the vector index loses no canonical data;
- hosted embeddings require a separate explicit data-egress decision;
- no automatic indexing of binaries or unsupported media;
- semantic similarity never overrides source role or freshness.

Compare semantic retrieval against the Phase 3 baseline on the same frozen query
set.

**Exit gate**

- semantic retrieval improves a named metric on a named query class;
- provenance coverage remains complete;
- context/fetch volume does not grow without measured benefit;
- disabling the semantic layer restores the Phase 3 path cleanly.

If the baseline is already good enough, close this phase without implementation.

## Phase 8 — MQ context and reviewed distillation

**Owner:** `mq-agent` for selection; `mqobsidian` for durable reviewed output

Integrate the corpus as an external research lane, not as a memory replacement.

Flow:

```text
task
  -> external corpus search when relevant
  -> selected evidence + provenance
  -> bounded context
  -> answer or research candidate
  -> human review
  -> optional public-safe research/memory record
```

Requirements:

- context packs contain only selected excerpts or compact synthesis, not archive
  dumps;
- external-corpus material is labelled separately from MQ durable memory;
- a distilled record cites its external source provenance;
- no automatic write into decisions, learn, systems or promoted memory;
- existing token budgets still apply.

**Exit gate**

- a task can use the corpus without broad Drive reads;
- external evidence is distinguishable from MQ-reviewed memory;
- promotion still goes through the existing review path;
- disabling the corpus path leaves existing MQ retrieval unchanged.

## Phase 9 — Operator visibility and safe automation

**Owner:** `mq-hal` for reporting; `mq-agent` for scheduled read-only refresh

Expose only the operational facts an operator needs:

- corpus configured/unconfigured;
- last complete scan;
- current/partial/stale index state;
- connector availability;
- notebook/file counts from the catalog;
- unknown source-role count;
- duplicate count;
- last retrieval fallback reason.

A periodic refresh may be added only after incremental scanning is proven
quota-safe. Scheduling a refresh does not authorize Drive mutation.

**Exit gate**

- operator can distinguish unavailable, stale, partial and current;
- scheduled refresh is idempotent and read-only;
- failures do not erase the last known complete catalog;
- no dashboard becomes a second source of corpus truth.

## Evaluation metrics

Use measurements before introducing ranking complexity:

| Metric | Why it matters |
| --- | --- |
| Catalog coverage | Proves the index represents the configured corpus rather than a convenient subset |
| Source-role coverage | Shows how much material has known evidence semantics |
| Duplicate rate | Prevents generated copies from looking like independent evidence |
| Top-k relevance | Measures whether simple search actually finds the intended material |
| Files fetched per query | Protects the smallest-useful-read invariant |
| Bytes fetched per query | Detects retrieval that quietly becomes archive scanning |
| Provenance coverage | Every material claim should resolve to a source |
| Derived-as-source violations | Must remain zero |
| No-answer correctness | Measures whether retrieval can abstain |
| Latency and Drive calls | Makes connector/quota cost visible |

Do not collapse these into one readiness score. A retrieval path that finds more
material while losing provenance is not an improvement.

## Delivery slices

Keep implementation reviewable and independently reversible:

1. **D0 — roadmap and boundary:** this document plus the top-level roadmap link;
2. **D1 — baseline inventory:** read-only measurement, sanitized report, no new
   schema unless a consumer proves it needs one;
3. **D2 — catalog contract:** schema/example/validation only when justified;
4. **D3 — deterministic catalog builder:** local generated index and checkpoint;
5. **D4 — metadata/text search:** query trace and frozen evaluation set;
6. **D5 — selective fetch + provenance:** source-role-aware answer context;
7. **D6 — cross-notebook research:** common findings, disagreements and gaps;
8. **D7 — interaction-gap analysis:** questions/gaps without evidence promotion;
9. **D8 — semantic retrieval experiment:** only if the D4 baseline misses the
   frozen gate;
10. **D9 — context integration and operator health:** bounded handoff and
    read-only freshness reporting.

Do not combine catalog contract creation, Drive adapter implementation,
semantic indexing and runtime activation in one PR.

## Stack-level definition of done

- Google Drive remains the storage authority for the archive;
- mqobsidian owns the external-corpus semantics, not the raw content;
- mq-agent owns selection and orchestration;
- source, derived and interaction material remain distinguishable end to end;
- no material claim relies on chat history as evidence;
- no derived artifact silently becomes primary evidence;
- normal queries fetch a bounded subset rather than the corpus;
- retrieval has a reproducible baseline before semantic search is considered;
- every activated retrieval path is provenance-bearing and freshness-aware;
- disabling the corpus layer restores existing MQ behavior without data loss;
- no Drive write-back or durable-memory promotion happens implicitly.

## Relationship to the closed NotebookLM evaluation

The previous Phase 12 verdict remains valid and is not superseded by this
roadmap. It answered a different question:

> Should NotebookLM become an MQ synthesis/retrieval provider?

The answer remains no on the measured evidence.

This roadmap asks:

> Can material already stored in the user's NotebookLM Drive archive become a
> useful external research corpus when MQ controls classification, selection,
> provenance and retrieval?

That question has not yet been measured. The phases above are the measurement
and implementation path, not evidence that the answer is yes.
