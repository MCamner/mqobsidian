<!-- Local-only / gitignored. Standing note on where Phase 12 actually is. -->

# ROADMAP_NOTES

_Updated 2026-06-27._

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

Today, exactly **one** producer actually emits during real work (command-pattern,
~7 real observations). repo-signal / mq-mcp / mq-agent emit nothing yet — the
"producer #2" used so far is **synthetic fixtures** (`memory/fixtures/`).

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

1. **Real data, slowly** — run normal work (roadmap, reviews, PRs, Atlas sessions);
   let the command-pattern producer accumulate genuine observations.
2. **Optionally, one real emitter** — if volume stays too low, wire a genuine
   `memory-observation.v1` emitter into repo-signal (the deferred cross-repo step).
   That is the only thing that makes the multi-producer data _real_.
3. **Stress-tests, in parallel** — labelled fixtures in `memory/fixtures/` to pin
   down DD-001 (downgrade/feedback binding) and DD-003 (cross-producer merge).
   These inform design, never readiness.

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
