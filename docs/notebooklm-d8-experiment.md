# NotebookLM D8 semantic retrieval experiment

**Implemented:** 2026-09-29  
**mq-agent PR:** #309  
**Merge:** `aa7411d9a820239cf9163cf7afad818dfbcdaecf`

## Purpose

D8 is an opt-in semantic retrieval experiment. It exists to measure whether a
local semantic layer improves the frozen D4 lexical baseline without weakening
provenance or evidence authority.

It is not an activated default retrieval path.

## Implemented commands

```text
mq-agent notebook semantic-build
mq-agent notebook semantic-search
mq-agent notebook semantic-eval
```

## Local-only embedding path

The default embedding model is `nomic-embed-text` through local Ollama.

The implementation performs no hosted embedding egress.

The build path is:

```text
D3 catalog
  -> bounded D5 text fetch
  -> bounded chunks
  -> local Ollama embeddings
  -> disposable JSON semantic index
```

## Provenance

Every indexed chunk retains:

- Drive item identity;
- notebook identity and title;
- item title;
- source role;
- inherited claim eligibility;
- modified time;
- content hash when available;
- character offsets.

Similarity scoring cannot change these fields.

## Evaluation contract

D8 uses the exact six frozen D4 queries. The operator supplies the expected
Drive item ids for the measured corpus, and the evaluation compares D4 lexical
results with D8 semantic results on the same top-k setting.

Reported metrics include:

- lexical passes;
- semantic passes;
- semantic improvements;
- semantic regressions;
- provenance coverage;
- hosted-egress state.

The decision labels are descriptive only:

- `SEMANTIC_BENEFIT_MEASURED`;
- `NO_MEASURED_BENEFIT`;
- `SEMANTIC_REGRESSION_OR_MIXED`.

None automatically activates semantic retrieval.

## Reversibility

The semantic index is explicitly disposable and non-canonical. Deleting it
loses no source material or MQ memory. D4 remains unchanged and available when
D8 is disabled.

## Verification

mq-agent PR #309 passed:

- full pytest suite;
- Ruff;
- mypy;
- docs consistency;
- command-reference consistency;
- macOS runtime/release gate;
- Markdownlint;
- MQ Stack Gate;
- Install smoke test.

A mypy annotation issue in the test fixture was found and corrected before
merge.

## Activation boundary

D8 should not become an active retrieval path until complete-corpus measurement
shows a named benefit over D4 with:

1. no semantic regression on the frozen query set;
2. complete provenance coverage;
3. no evidence-role violation;
4. justified fetch/context cost.

Until then D8 remains an experiment.
