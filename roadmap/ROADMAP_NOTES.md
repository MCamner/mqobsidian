<!-- Local-only / gitignored. Standing note on where Phase 12 actually is. -->

# ROADMAP_NOTES

_Updated 2026-08-25._

## Current state

The Phase 12 memory architecture is **validated**:

- 1 producer, 2 producers, cross-producer promotion, feedback gating, event
  sourcing, schema stability — all proven **without** new contracts, new statuses,
  or rewriting the scorer.

## The bottleneck is not code

```text
The architecture is validated.

The bottleneck is not code.
The bottleneck is observation volume from real producers.

Priority:
Acquire more real data — do not build the next abstraction layer yet.
```

Today, **three** producers have emitted during real work: Claude, Codex, and
repo-signal. The local observation surface contains 15 real observations
(Claude 9, Codex 2, repo-signal 4). Synthetic fixtures under
`memory/fixtures/` remain architecture tests and do not count as evidence.

The producer gate is complete. The binding gap is cross-producer overlap: no
`proposed_memory_key` currently appears from two independent producers.

## Two tracks (decision 2026-06-27)

| Track | What it is | Counts toward readiness? |
|-------|------------|--------------------------|
| **Real evidence** | command-pattern producer (+ future real emitters) | **Yes** |
| **Synthetic fixtures** | architecture stress-tests under `memory/fixtures/` | **No** |

Rule (ADR-008 Principle 11): **fixtures ≠ evidence.** Synthetic data may validate
the architecture; only real observations may advance the Slice 2 Definition of
Ready (≥3 producers, ≥25 observations, ≥5 shared `memory_id`, ≥3 cross-producer
promotions, ≥1 merge conflict).

## What advances things from here

1. [ ] **Real data, slowly** — continue normal roadmap, review, PR, and Atlas
   work. Current volume is 15/25 real observations; do not run empty work only
   to increase the count.
2. [x] **One real emitter** — repo-signal has an opt-in, failure-isolated
   `memory-observation.v1` emitter and has produced four real observations.
3. [x] **Stress-tests, in parallel** — labelled fixtures under
   `memory/fixtures/` exercise DD-001 (downgrade/feedback binding) and DD-003
   (cross-producer merge). They inform design but never readiness.

## Current readiness — 2026-08-25

| Gate | Target | Actual | Status |
|------|-------:|-------:|:------:|
| Real producers | ≥3 | 3 | ✅ |
| Real observations | ≥25 | 15 | ❌ |
| Shared `memory_id` / proposed key | ≥5 | 0 | ❌ |
| Cross-producer promotions | ≥3 | 0 | ❌ |
| Real merge conflict | ≥1 | 0 | ❌ |

A real repo-signal inspection of mqobsidian on 2026-08-25 returned public
readiness 16/16 and no issue. The emitter correctly wrote no observation.

## CodeGraph boundary (ADR-009, 2026-06-27)

```text
ADR-009:
CodeGraph Core now.
CodeGraph Memory Producer later.
Graph data ≠ observation evidence.
```

CodeGraph splits into Project A (Core — parser/graphs/hotspots/query, builds now,
own repo) and Project B (`codegraph → memory-observation.v1`, data-gated, parked).
Graph history may validate/suggest, but never counts as readiness, feedback, or
promotion evidence. See [[decisions/ADR-009-codegraph-memory-boundary]].

## What NOT to do now

- ❌ build Slice 2 / the Generic Engine
- ❌ build cross-producer merge (DD-003)
- ❌ change any public contract
- ❌ fabricate observations to tick the readiness gate

> "Systemet är färdigt för tillfället. Nu behöver vi erfarenheter, inte fler
> abstraktioner."
