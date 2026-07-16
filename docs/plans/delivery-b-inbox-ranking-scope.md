# Delivery B — Inbox Ranking And Promotion Boundary (Scope)

**Status:** Proposed — **planning artifact, not build work.** No schema or code
change is authorized by this document. Its only job is to fix the boundary so a
later, separately-approved PR builds the right thing in the right repo.

**Owner boundary (one line):** `mqobsidian` owns the *vocabulary and the
thresholds as data*; `mq-agent` owns the *computation and the workflow*;
`macos-scripts` stays out of both.

Grounded against the schemas on `main` (2026-07-06) and DEC-002. Delivery A
(canonical schema) is closed; this scopes ROADMAP Delivery B ("Inbox and
ranking model").

---

## What already exists (so we don't reinvent it)

Delivery B is mostly *wiring existing vocabulary*, not new invention:

| Surface | Role in ranking |
| --- | --- |
| `memory-score.v1` | The score itself: `factors` (frequency, source_count, confidence, recency, usage_score, manual_boost), `feedback` (positive/negative), `status` on the promotion axis, `first_seen`/`last_seen`. |
| `feedback-signal.v1` | Pack-usage feedback events (`useful`/`noise`/`missing`/`stale`). Emitted by `mq-agent` into a **local-only, gitignored** `feedback/` surface. "The loop never auto-publishes: promotion/downgrade are proposals, not commits." |
| `inbox-manifest.v1` | The candidate set: items with `state ∈ {observed, candidate}`, `occurrences`, `evidence[]`, optional mirrored `score`. |
| `promotion-event.v1` | The reversible audit trail of tier changes; every promotion is `reason`-bearing and a downgrade is just an event in the other direction. |
| DEC-002 / ADR-008 | "Frequency never promotes on its own." Consumers read manifests, never reconstruct truth. |

**Implication:** no new *vocabulary* schema is obviously required. The open work
is (a) where thresholds live and (b) codifying the review-vs-auto boundary.

---

## 1. Ranking inputs

The score is a function of `memory-score.v1.factors` + `feedback`. Constraints
to preserve, not redesign:

- **No single factor promotes.** Frequency, recency, or a single source count
  are inputs, never triggers (ADR-008).
- **Evidence is required for traceability.** A candidate's `evidence[]`
  (`inbox-manifest.v1`) must resolve to real source records; promotion writes
  `source_evidence_refs` onto the durable record (added in Delivery A).
- **Feedback is signed but bounded.** `feedback.negative` and `noise`/`stale`
  judgments can block or downgrade, but only as a *proposal*.

Open: is the exact scoring formula owned as data (below) or left to `mq-agent`
as documented heuristics? Recommendation: **weights as data, formula as code.**

## 2. Thresholds

Two thresholds define the boundary: a **review threshold** (enter the human
queue) and an **auto-promote threshold** (eligible to promote without review).

- **Recommendation:** thresholds and factor weights are **data owned by
  `mqobsidian`** — a small versioned policy surface — so the promotion boundary
  is itself single-source-of-truth and auditable, not buried in `mq-agent`.
- **Locked:** `promotion-policy.v1` owns weights, review/auto thresholds,
  minimum supporting factors, negative-feedback blocking, and manifest age.
  (`{review_threshold, auto_threshold, weights{…}, min_supporting_factors: 2,
  block_negative_feedback: true, max_manifest_age_seconds: …}`).

## 3. Review-vs-auto-promote boundary

The one decision this doc exists to frame:

| Bucket | Condition (illustrative, not final) | Action |
| --- | --- | --- |
| **Stay in inbox** | below `review_threshold` | keep accumulating evidence |
| **Review-needed** | ≥ `review_threshold`, or conflicting signals (negative feedback, `stale`), or single-factor-only | enqueue for a **moderator checkpoint** |
| **Auto-promotable** | ≥ `auto_threshold` AND multi-factor AND no blocking feedback | may promote **as a proposal**, still logged as a `promotion-event.v1` |

**Human checkpoint is non-negotiable** (per `feedback-signal.v1`): even
"auto-promotable" produces a proposal + event, never a silent commit. The
moderator checkpoint is where automation stops (ROADMAP Scope).

## 4. What belongs to `mqobsidian` (schema hooks — owns)

- the vocabulary: `memory-score.v1`, `inbox-manifest.v1`, `promotion-event.v1`,
  the promotion axis, `source_evidence_refs`.
- **thresholds/weights as versioned data** (`promotion-policy.v1`).
- the audit-trail contract (`promotion-event.v1`).
- **NOT** the scoring computation, the queue, or the review UI.

## 5. What belongs to `mq-agent` (orchestration — owns)

- compute `memory-score.v1` from evidence and feedback.
- rank the inbox and bucket items using the mqobsidian-owned thresholds.
- run the review gate; on approval, emit a `promotion-event.v1` and write the
  durable record with `promoted_at` + `source_evidence_refs`.
- this is the substance of the **`mq-agent` v1.22.0** milestone; Delivery B does
  not duplicate it here.

## 6. What stays out of `macos-scripts`

- `mqlaunch` may **surface** the review queue and **delegate** an approve/reject
  to `mq-agent`; it **never** computes a score, applies a threshold, or writes a
  promotion. Read-or-delegate only (DEC-002).

---

## Decisions to lock before any Delivery-B build

- [x] thresholds/weights are owned as **mqobsidian data**.
- [x] publish `promotion-policy.v1` and discover it through the canonical export index.
- [ ] the moderator-checkpoint surface: `mqlaunch` review view vs `mq-agent` CLI (rec: delegate from mqlaunch).
- [x] scoring formula ownership is weights-as-data in mqobsidian + formula-as-code in mq-agent.

## Exit criteria (scope done)

- the six boundaries above are agreed;
- the "locked decisions" list is resolved;
- policy/schema publication remains separate from private vault mutation state.
