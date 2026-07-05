# Roadmap

`mqobsidian` is the single source of truth and durable memory for the MQ stack.
Its job is to own the canonical structure of truth, inbox, promotion, and
memory — and to export stable surfaces that other repos read, rather than each
tool inventing its own partial state.

## Ownership boundary

The stack has one clean responsibility split. `mqobsidian` holds the truth;
other repos read or delegate to it.

- `mqobsidian` — canonical truth schema, inbox/promotion state, durable memory
  model, exported views/manifests, freshness markers.
- `mq-agent` — orchestration: inbox analysis, ranking, review-gated promotion,
  and contract enforcement against mqobsidian exports. Runs the workflow; does
  not own the schema.
- `macos-scripts` / `mqlaunch` — terminal runtime, menus, and UI. A thin
  read-only or delegate-only surface; never a truth owner.

`mqobsidian` does **not** own: terminal UX, shell runtime authority,
orchestration logic, review execution, or menu routing.

## Single Source Of Truth And Promotion Governance

**Status:** Proposed
**Priority:** P1
**Type:** Memory / Truth model / Governance
**Goal:** Make `mqobsidian` the canonical owner of truth structure, inbox
state, promotion state, and durable memory views across the stack.

### Why this matters

Without one canonical truth layer, every tool starts inventing its own partial
memory, ranking, and status model. That produces drift, duplicate state, weak
trust, and manual moderation bottlenecks.

### This repo owns

- canonical truth schema
- inbox structure and promotion queue structure
- durable memory categories and persistence rules
- canonical status/views/manifests consumed by other repos
- freshness/state markers for truth surfaces
- promotion state and memory lifecycle states
- single-source-of-truth rules across the stack

### This repo does not own

- terminal UX
- shell runtime authority
- orchestration logic
- review execution engine
- agent delegation UX
- menu routing

### Target state

- one canonical schema for status, inbox, views, decisions, learn, and reviews
- one canonical promotion queue
- one canonical durable memory model
- one canonical export surface for consumers
- no competing truth plane in shell or agent layers

### Scope

- define canonical note/schema structure
- define inbox item model
- define scoring fields and promotion-state fields
- define durable memory categories and thresholds
- define canonical views/manifests for consumers
- define freshness/version markers for exported truth surfaces
- define moderator checkpoints where automation stops

### Delivery

#### A. Canonical schema

- define status manifest
- define inbox manifest
- define views manifest
- define learn/review/decision schemas
- define promotion-state fields
- define archival/deprecation lifecycle fields

#### B. Inbox and ranking model

- define what enters the inbox
- define recurrence/evidence fields
- define ranking inputs
- define review-needed vs auto-promotable states
- define thresholds and exception paths

#### C. Durable memory governance

- define what qualifies as durable memory
- define what remains transient or session-local
- define promotion approvals and guardrails
- define the rollback/deprecation path for bad memory
- define traceability from source evidence to durable note

#### D. Consumer contracts

- define canonical read surfaces for `mqlaunch`
- define canonical delegation/contract surfaces for `mq-agent`
- version exported truth surfaces
- expose freshness and drift markers

### Exit criteria

- `mqobsidian` is the undisputed truth owner
- inbox, ranking, promotion, and durable memory have one canonical model
- consumers read from exported truth surfaces instead of inventing local truth
- every promoted durable memory item can be traced back to source evidence

## Related

- `mq-agent` orchestration milestone: `v1.22.0 — Inbox ranking and promotion
  orchestration` (consumes the exports defined here).
- `macos-scripts` runtime governance: `Phase 12 / v2.0.0 — Runtime Authority
  And Shell Governance` (delegates to the surfaces defined here).
