# Context Contract

## Purpose

This document defines how `mqobsidian` should be used as the durable memory and
context-contract layer for the MQ stack.

The goal is simple:

- lower token usage
- stronger continuity
- fewer broad repo scans
- better separation between memory and live truth

This contract governs *how to read* the vault. The
[context export contract](context-export-contract.md) governs the *format* of the
`.mq/context` export files, and [TOKEN_BUDGET.md](TOKEN_BUDGET.md) governs their
*size*.

## Core rule

Read the smallest useful surface first.

Do not start with broad vault scans, large READMEs, or many full notes if a
smaller context surface already exists.

## What mqobsidian owns

- durable memory of verified work
- compact context surfaces for agents
- agent views
- system `hot.md` and `index.md` notes
- context cards
- context-pack schemas, templates, and rules
- token-budget rules
- public-safe export rules

## What mqobsidian does not own

- live runtime truth
- active execution state
- current CLI truth
- current review execution
- mutation workflows
- orchestration control

Those belong to source repos and tools such as `mq-agent`, `mq-mcp`, `mq-hal`,
`repo-signal`, `mq-ums`, and `mq-image-analyze`.

## Standard read order

For MQ stack work:

1. task pack if one exists (`.mq/context/task-pack.md`)
2. repo agent view (`memory/learn/agent/<repo>.md`)
3. repo `hot.md`
4. repo `index.md`
5. small context cards
6. only then larger notes or source-repo docs

For `mqobsidian` itself:

1. `memory/learn/agent/mqobsidian.md`
2. `systems/mqobsidian/hot.md`
3. `systems/mqobsidian/index.md`
4. relevant context cards
5. larger docs only if needed

Stop reading once the task is grounded.

## Smallest useful surfaces

Preferred surfaces, from cheapest to most expensive:

1. generated task pack
2. agent view
3. `hot.md`
4. `index.md`
5. context card
6. focused durable note
7. full repo docs
8. full broad scans

Always prefer the smallest surface that can answer the task.

## Context surfaces

### Agent views

Repo-specific read-me-first surfaces; a compact routing layer for agents. Should
state what to read first, what to avoid, the current boundary, and the next
likely files.

### `hot.md`

Current high-value operating context: current state, priority, risk, immediate
next action, and the truth boundary if relevant. Not long history, not broad docs
duplication, not raw logs.

### `index.md`

Stable system map: repo role, what it is not, read order, key files,
source-of-truth map, and generated surfaces.

### Context cards

Small reusable notes for recurring questions (token budget, vault structure,
public-safe export, context-pack format, skill generation). See
[CONTEXT_CARDS.md](CONTEXT_CARDS.md).

## Truth-boundary rule

If a question is about current code, tests, CLI behavior, review behavior, or
runtime status, verify in the source repo or tool.

If a question is about durable patterns, prior lessons, stable architecture
memory, reusable workflow knowledge, or routing, use `mqobsidian` first.

## Expansion rule

A reader may expand from one surface to the next only when the smaller surface is
insufficient, the remaining uncertainty is material, or the task requires direct
source verification. Expansion should be explicit, not automatic.

## Anti-patterns

Do not:

- scan the full vault by default
- treat durable memory as live truth
- duplicate large README sections into notes
- dump raw logs into durable memory
- turn every lesson into hot context
- keep growing agent surfaces without budget limits

## Practical decision rule

Use `mqobsidian` first when the question is about memory. Use source repos first
when the question is about truth. That boundary must stay clear.
