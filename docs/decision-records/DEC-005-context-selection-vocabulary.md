---
schema: decision-record.v1
decision_id: DEC-005
created_at: 2026-08-28T00:00:00Z
title: mqobsidian owns context-selection vocabulary; mq-agent owns context selection execution
status: accepted
---

# Decision

## Context

`systems/mqobsidian/hot.md:29` states that `mq-agent` owns context selection,
pack generation and export, and `systems/mqobsidian/index.md:17` states that
this repo does not run workflows. The code did not read that way, and the
mismatch was found the hard way: it surfaced from the CodeGraph baseline during
the Phase 12 evaluation, and was then verified directly in source.

Two things in this repo look like violations of that sentence. They are not the
same case, and they do not get the same answer.

**`scripts/generate-context-pack.py` duplicates mq-agent's selection logic.**
It classifies a task as source-heavy against `CODEGRAPH_TASK_HINTS` and
`CODEGRAPH_TASK_SUPPRESS`, then builds bounded per-task queries under
`MAX_CODEGRAPH_QUERIES`. `mq_agent/tools/context_pack.py` contains the same
three constants and the same two functions. Compared by parsing both files,
the constants are currently **identical** — there is no drift yet. Nothing
prevents it either: the only protection is a convention that both copies get
edited together.

**`scripts/generate-repo-context-export.py` is not migration debris.** It is
load-bearing in this repo's own CI:

```yaml
- name: Check context exports are regenerated
  run: |
    python3 scripts/generate-repo-context-export.py --all
    if ! git diff --quiet -- examples/repo-context-exports; then
```

It regenerates `examples/repo-context-exports` — a published surface this repo
owns — and fails the build when that surface goes stale. Moving it to mq-agent
would make the contract owner's CI depend on a consumer repo, inverting the
relationship `.mq/repo-contract.json:33` establishes.

So "move the generators to mq-agent" would break a working freshness gate to
fix a duplication problem that has a better answer, and "leave both copies
alone" keeps a silent drift risk in the one place where the ownership sentence
is genuinely wrong.

## Decision

**mqobsidian owns the context-selection vocabulary. mq-agent owns context
selection execution.**

The words that define what counts as source-heavy are knowledge about the
system's own semantics, which is what this repo exists to hold. Deciding to
apply them to a concrete task and assembling a pack is orchestration, which is
mq-agent's.

This is the split the repo already uses successfully elsewhere:
`.mq/context-budgets.json` is, per `scripts/context_budgets.py`, "owned by
mqobsidian, also consumed by mq-agent", and `promotion-policy.v1` keeps weights
and thresholds as auditable data owned here while the formula runs there.

Under this reading `hot.md:29` is already true and needs no rewrite: mq-agent
owns selection; mqobsidian owns the vocabulary that selection consumes.

## Consequences

- **The heuristic becomes a versioned, declarative contract in mqobsidian.**
  It must be a serialized artifact of the same class as
  `.mq/context-budgets.json` — **not** a Python constant in another module.
  Re-expressing it as code would move the duplicate rather than remove it,
  which is the failure this decision exists to prevent.
- **mq-agent keeps no copy of the vocabulary.** It reads the published
  contract. A vendored copy is acceptable only as an explicitly temporary
  consumer strategy with a drift test, never as the resting state.
- **mqobsidian makes no runtime selection decisions.** Its reference generator
  may validate, render and export against the published contract, and nothing
  more. Producing a pack for a live task remains mq-agent's.
- **No general cross-repo contract distribution is built for this.**
  Consumption uses the established `context-budgets` pattern. Phase 12 closed
  with 12f recorded as debt that should not be paid, and this decision does not
  reopen it.
- **The export freshness gate stays here.** It guards a surface this repo
  publishes; that is ownership, not orchestration.

## Related

- DEC-002 — mqobsidian owns current truth surfaces. Same boundary, applied to
  selection vocabulary.
- DEC-003 — strict schema enforcement. The vocabulary contract needs real
  validation, not a hand-rolled shallow check.
- DEC-004 — a contract nobody can enforce, or a producer nobody has, is not a
  contract. Here the inverse risk applies: two producers of the same truth,
  with nothing making them agree.
- `ROADMAP.md`, Ownership boundary — the track this decision closes point 2 of.
  Point 3 (rewriting `hot.md`) follows implementation, not this record.
