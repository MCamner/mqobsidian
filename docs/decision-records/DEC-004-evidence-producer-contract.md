---
schema: decision-record.v1
decision_id: DEC-004
created_at: 2026-07-17T00:00:00Z
title: An evidence producer contract must exist before a generalized evidence adapter
status: accepted
---

# Decision

## Context

The v1.22 plan (mq-agent, Task 8) specifies a generalized evidence adapter:
parse "bounded JSON evidence documents with explicit producer/schema ids" from
mq-mcp review outputs and repo-signal readiness, attach them as proposal
evidence, and reject "raw text, unknown schema, missing candidate, and
path-bearing refs".

Checked against what the producers actually emit, the premise does not hold:

1. **mq-mcp `review_file` returns a string** — free-form AI review prose, not a
   JSON document. `review_contract.v1` in mq-mcp's repo contract names review
   *modes* under `reviews/contracts/`, not an emitted evidence schema. The
   plan's own "reject raw text" rule would reject mq-mcp's only real output.
2. **repo-signal declares `readiness_score.v1` and `publish_checklist.v1` and
   emits neither.** Those names appear only in its repo contract. It emits
   `readiness.v1`, `doctor.v1`, `inspect.v1`, `suggest.v1`.
3. **No repo-signal output carries a candidate key.** All eight example
   documents were checked. The plan's "reject missing candidate" rule would
   reject every one.
4. **`readiness.v1` carries an absolute private path** (`"path":
   "/Users/mansys/repo-signal"`). If it ever becomes evidence it must be
   sanitized, the way `build-truth-exports.py` sanitizes observations.

So the adapter would reject both real producers, and would only ever accept
documents nobody sends. Its tests could only be written against invented
fixtures.

This stack has produced that failure three times already: a perception module
with no producer, a loop-audit consumer built ahead of its writer, and a v1.22
inbox consumer that duplicated work #124 had shipped. The common shape is a
consumer built against an imagined contract, green on fixtures, untested
against reality.

## Decision

Do not build a generalized evidence adapter until at least one producer
actually emits candidate-bearing, bounded JSON evidence with an explicit
`producer` and `schema_id`.

Task 8 is **blocked by producer contracts** — not "todo", not "deferred for
capacity". The distinction matters: nothing about mq-agent needs to change for
it to become unblocked.

## Consequences

- **repo-signal** must be able to emit candidate-bearing evidence JSON before
  its readiness output can feed promotion. Its declared contract names should
  also be reconciled with what it emits, or the declaration is misleading.
- **mq-mcp** either keeps feeding memory through the path that already works —
  `run_cochange` → `cochange_observation.build_observation` →
  `memory-observation.v1`, which carries `proposed_memory_key` and is in
  service today — or grows a separate JSON evidence output mode. Raw AI review
  text is not evidence and must not be accepted as such.
- **mq-agent** proceeds to Task 10 (the `obsidian inbox` CLI), which builds on
  Task 7's ranking — verified against the real vault, not fixtures.
- Any future evidence document must resolve through
  `memory-evidence-manifest.v1`, per the v1.22 locked design: opaque refs never
  become justification.

## Related

- DEC-002 — mqobsidian owns current truth surfaces.
- DEC-003 — strict schema enforcement. Same theme: a contract nobody can
  enforce, or a producer nobody has, is not a contract.
