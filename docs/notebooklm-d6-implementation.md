# NotebookLM D6 cross-notebook research implementation

**Closed:** 2026-09-29  
**Implementation:** `mq-agent` PR #307  
**Merge:** `3115772556c00cd1e74dd21d3bf17d8bb5b8b855`

## Purpose

Record the completed D6 implementation without claiming that the full Drive
archive has passed the activation gate.

D6 sits above D5 selective retrieval. It does not scan the archive independently
and it does not create a second evidence path.

## Implemented behavior

The operator surface is:

```text
mq-agent notebook research "<question>"
```

D6 can return:

- common findings;
- supported disagreements;
- source evidence;
- NotebookLM-derived interpretations kept as secondary context;
- unanswered questions and missing evidence.

The synthesizer is advisory. Its proposed support ids are re-validated against
the D5 evidence bundle before any cross-source finding is accepted.

## Independence rule

A common finding requires:

1. at least two D5 `claim_eligible=true` source items;
2. at least two independent source identities;
3. support across at least two notebooks.

When `content_sha256` exists, two files with the same digest count as one
independent source even if their Drive item ids differ. When no digest exists,
the opaque Drive item id is the conservative fallback identity.

Derived and interaction material never satisfy this requirement.

## Disagreements

Conflicting positions remain separate. D6 does not vote, average or select a
winner. A disagreement must itself have source-supported positions backed by at
least two independent sources across at least two notebooks.

## Derived material

NotebookLM-generated interpretations are returned separately and remain
`claim_eligible=false`. A proposal that mixes a primary source into the
derived-only section is rejected rather than silently reclassified.

## Review boundary

An operator may explicitly save a local review candidate. The candidate does
not write to decisions, learn records, systems, promotion state or other durable
mqobsidian memory.

## Verification

PR #307 passed:

- Tests;
- Markdownlint;
- MQ Stack Gate;
- Install smoke test.

The test suite covers independent-source enforcement, duplicate-content
deduplication, derived-source rejection, disagreement preservation,
derived-only interpretations, no-source abstention, local review-candidate
behavior and live-runtime delegation.

## Activation boundary

This closeout proves the D6 implementation and its deterministic authority
rules. It does **not** prove whole-archive D6 operation.

Whole-archive activation still requires:

1. a complete current adapter-produced D3 catalog;
2. the six frozen D4 queries passing over that complete catalog;
3. D5 retrieval operating over the same catalog without authority or provenance
   violations.

Only after those gates pass should D6 be measured and described as active over
the complete archive.
