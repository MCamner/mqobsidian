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

`notebook-corpus-index.v1` now describes that local index. D2 established the
named consumer as the future `mq-agent` catalog/search path and froze only the
metadata fields that consumer needs. The real catalog remains local and
disposable.

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

**Status:** Completed 2026-09-28 — measured in
[`docs/notebooklm-drive-corpus-baseline.md`](../notebooklm-drive-corpus-baseline.md).

**Owner:** `mqobsidian` for definitions; `mq-agent` for measurement

Establish what the archive actually is before designing retrieval around it.

Tasks:

- [x] inventory the configured Drive corpus by folder, MIME type, file count,
  size and modification time without reading every file body — 6,914 files,
  8.244 GiB, 199 valid notebook folders plus one malformed empty-name manifest
  record;
- [x] identify how notebook boundaries are represented by parent folders and
  exported metadata — the manifest's notebook/path identity is the snapshot
  authority and the Drive folder tree is the current storage projection;
- [x] measure duplicates and repeated generated artifacts without deleting them
  — 39 duplicate SHA-256 groups, 45 redundant copies, including 11 groups that
  cross notebook boundaries;
- [x] sample several notebooks and record which artifacts can be classified
  reliably as source, derived or interaction — five samples use the same
  structural classifier and 96.8% of all files have a known evidence role;
- [x] define a small sanitized query set for later retrieval measurement — six
  frozen queries cover exact recall, cross-notebook synthesis, architecture,
  another domain, source-role ordering and a negative control;
- [x] write a decision record for the external-corpus boundary only if the
  ownership table above conflicts with an existing accepted decision — no new
  record is required; D1 confirms the existing Drive / mqobsidian / mq-agent
  ownership split.

Do not infer that a filename or extension proves authority. Classification
rules must be explicit and overridable.

**Exit gate**

- [x] the configured corpus root is known locally;
- [x] notebook-to-file relationships can be reconstructed deterministically;
- [x] a representative sample has explicit source roles;
- [x] no raw corpus content or Drive identifier is required in tracked files;
- [x] the baseline query set exists before search implementation starts.

**Measured result:** Phase 0 is closed. The baseline found 199 valid notebook
folders, one malformed empty-name manifest record, 6,914 files, 39 duplicate
hash groups and a structural source-role classification for 96.8% of files.
The full public-safe measurement is in
[`docs/notebooklm-drive-corpus-baseline.md`](../notebooklm-drive-corpus-baseline.md).

## Phase 1 — Corpus catalog contract

**Status:** Completed 2026-09-28 — contract frozen in
[`schemas/notebook-corpus-index.v1.json`](../../schemas/notebook-corpus-index.v1.json)
with a sanitized example, validation tests and
[`docs/notebooklm-corpus-index-contract.md`](../notebooklm-corpus-index-contract.md).

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

- [x] rebuilding unchanged metadata produces the same logical catalog — v1
  requires deterministic notebook/item ordering and uses source snapshot time,
  not build time, as catalog state;
- [x] every catalog record maps back to exactly one Drive item — notebook and
  file records carry explicit opaque Drive item identity;
- [x] unknown source role remains representable — `unknown` is a first-class
  classification role and method;
- [x] deleting the local catalog loses no canonical knowledge — Drive remains
  corpus storage; the tracked repository contains only contract, example and
  tests.

**Result:** D2 is closed. D3 may materialize this contract but must not add
search, semantic indexing or Drive mutation in the same slice.

### D3 materialization result

**Status:** Completed 2026-09-29 in `mq-agent` PR #303, merged as
`d8da5c21dffa947dde0434ea7e2adda55e233e21`.

D3 added the deterministic materializer for `notebook-corpus-index.v1`:

- normalized metadata becomes a schema-validated local catalog;
- logical notebook/item IDs derive deterministically from opaque Drive identity,
  not display titles;
- the D1 structural source-role rules are preserved, including explicit
  `unknown`;
- classification overrides require provenance;
- unmapped records are excluded and counted rather than assigned to a synthetic
  notebook;
- the local checkpoint records a deterministic source fingerprint, catalog
  SHA-256 and included/excluded counts;
- generated JSON is written atomically;
- the canonical D2 schema is vendored into `mq-agent` and protected by its
  existing cross-repo drift gate.

The implementation deliberately does not contain a Drive adapter, search,
selective file fetch, embeddings or Drive mutation.

## Phase 2 — Incremental, quota-aware Drive inventory

**Status:** Implementation completed 2026-09-29 in `mq-agent` PR #305,
merged as `0ce86adc273b174a9860972d75ceffe1f7ae8c5f`.

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

- [x] an interrupted scan resumes without starting over — opaque page cursors
  and discovered child-folder work survive checkpoint/resume;
- [x] an unchanged second scan reads materially less content than the first —
  after the initial traversal, refresh uses the Drive change feed and an
  unchanged corpus completes with one change-feed request;
- [x] quota/rate-limit failure produces a truthful partial state — retryable
  quota/transient responses use bounded backoff and a failed page never becomes
  current;
- [x] no Drive mutation is required to maintain the index — the adapter
  implements metadata-list and change-feed reads only.

**Current projection observation, 2026-09-29:** a separate read-only connector
inspection found 204 top-level items under the configured archive root:
203 folders and one root metadata file. D1 recorded 200 top-level folders on
2026-09-28. The current folder set includes the manifest folder plus one empty
container folder; excluding those leaves 201 current notebook-folder candidates.
This is a new storage-projection observation, not a correction to D1's immutable
snapshot.

The same inspection also found at least one notebook-folder candidate whose
generated artifacts are flattened directly at notebook root rather than under
the usual typed `Sources/` and `Artifacts/` folders. The classifier must keep
such records conservative (`metadata-or-other` or `unknown`) until stronger
provenance is available rather than inferring authority from file type.

**Result:** Phase 2 implementation is closed. The remaining operational step is
to run the merged adapter against the real corpus, project a current D3 catalog,
and execute the frozen D4 evaluation. That measurement, not the adapter merge,
is what can unlock D5.

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

### D4 implementation result

**Implementation status:** Completed 2026-09-29 in `mq-agent` PR #304,
merged as `c4268d5daf86864f6bcab2e160c92688ae40fb01`.

D4 now provides:

- lexical metadata retrieval over the D3 catalog;
- optional provider text-match metadata as a separate input channel;
- deterministic ranking with item-title, provider-text and notebook-title
  signals;
- source-role ordering as a tie-breaker;
- bounded top-k results;
- explicit query traces covering candidate counts, returned role mix,
  connector-call count and zero file-body/byte reads by D4 itself;
- `mq-agent notebook catalog`, `search` and `show` operator commands;
- the six D1 queries frozen verbatim in tests, including the negative control;
- a hard no-broadening rule when nothing matches.

The tracked tests use a sanitized synthetic corpus. They prove retrieval
semantics and trace behavior.

A bounded real-corpus probe was completed 2026-09-29 and is recorded in
[`docs/notebooklm-real-corpus-d4-probe.md`](../notebooklm-real-corpus-d4-probe.md).
All six frozen query behaviors passed against the live Drive projection without
file-body reads, including source-before-derived behavior and the Akkadian
negative control.

The probe is intentionally not treated as a complete D3-catalog measurement:
the conversational Drive connector cannot truthfully enumerate the whole corpus
within its provider/tool limits. The remaining Phase 3 requirement is therefore
a complete current catalog produced by the merged local Drive adapter, followed
by the same six queries over that catalog.

Do not start D5 selective fetch until that complete-catalog run passes.

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
2. **D1 — baseline inventory:** **completed 2026-09-28** — read-only
   measurement and sanitized report; no schema was added;
3. **D2 — catalog contract:** **completed 2026-09-28** —
   `notebook-corpus-index.v1`, sanitized example and validation tests;
4. **D3 — deterministic catalog builder:** **completed 2026-09-29** in
   `mq-agent` PR #303 — deterministic catalog + local checkpoint;
5. **D4 — metadata/text search:** **implementation completed 2026-09-29** in
   `mq-agent` PR #304 — lexical baseline, query trace and frozen evaluation
   set; real-corpus measurement is pending a current adapter-produced D3 catalog;
6. **D5 — selective fetch + provenance:** blocked until the real-corpus D4
   measurement passes;
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
