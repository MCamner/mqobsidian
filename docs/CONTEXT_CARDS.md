# Context Cards

## Purpose

Context cards are small reusable notes for recurring MQ questions. They exist so
an agent can read one small note instead of a large document set.

A context card is not a mini-README. It is a compact answer surface.

The card schema is [`schemas/context-card.v1.json`](../schemas/context-card.v1.json)
and the starting shape is [`templates/context-card.md`](../templates/context-card.md).
Published cards live in [`memory/context-cards/`](../memory/context-cards/).

## When to create a card

Create a card when a question is common, stable enough to reuse, expensive to
answer by scanning larger docs, and narrow enough to keep small.

Good examples: token budget, vault structure, public-safe export, context-pack
format, skill generation.

## When not to create a card

Do not create a card when the topic is highly volatile, already small enough in
existing notes, better answered directly in source repos, or too broad to stay
compact.

Bad examples: full repo architecture, long workflow histories, broad roadmap
dumps, large command encyclopedias.

## Card format

Each card should follow this shape:

1. purpose
2. use when
3. core rule
4. short bullets
5. read next

Keep it structured and compact.

## Example skeleton

```text
# token-budget

## Purpose
Keep agent-readable context surfaces small.

## Use when
- sizing AGENTS.md
- sizing agent views
- reviewing task packs

## Core rule
A context surface must stay smaller than the material it replaces.

## Rules
- keep hot notes tiny
- split large notes
- prefer links over repeated prose

## Read next
- docs/TOKEN_BUDGET.md
```

## Naming

Prefer short, stable names: `token-budget`, `vault-structure`,
`public-safe-export`, `context-pack-format`, `skill-generation`. Avoid long
sentence titles.

## Size rule

Cards follow the enforced card budget in
[TOKEN_BUDGET.md](TOKEN_BUDGET.md): target 20–40 lines, soft 50, hard 60
(`memory/context-cards/*.md` is gated at 60). If a card grows beyond that, split
it or move detail elsewhere.

## Placement

System-specific cards belong with that system; cross-stack cards go in the shared
`memory/context-cards/` area. For `mqobsidian`, system cards should be easy to
find from `systems/mqobsidian/index.md` and `memory/learn/agent/mqobsidian.md`.

## Read-order role

Cards sit after the task pack, agent view, `hot.md`, and `index.md`. They are not
the first surface by default — they are the next compact step when a slightly
deeper answer is needed.

## Design rule

A good context card saves reading. A bad context card adds another thing to read.
