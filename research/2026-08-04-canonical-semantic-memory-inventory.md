---
type: research
system: mq-agent
status: closed
priority: medium
confidence: high
research_tag: research-node
source: mq-agent docs/plans/2026-08-04-canonical-semantic-memory.md (branch feat/canonical-semantic-memory, deleted 2026-09-13)
tags: [research-node, semantic-memory, vector-store, point-in-time]
updated: 2026-09-13
links_to: [systems/mq-agent/index]
owner:
validation_state: verified
---

# Research Node: Did the legacy knowledge store hold anything unique?

> **Point-in-time observation, 2026-08-04.** This node records what an inventory
> found on that date and what decision it unblocked. It is **not** current store
> status: no store has been read since, and nothing here should be treated as a
> live inventory.

## Problem

Before `ask`/`chat` could move off the macos-scripts shell surface, one question
had to be closed: does the legacy `macos-scripts-knowledge` vector store hold
content that would be lost if it were retired? Until that was answered, the
migration could not proceed without risking silent data loss.

## Why this exists

The answer was reached once, by reading the store, and the reasoning lived only
in an implementation plan on a feature branch. The branch's code was superseded
by a different and better implementation (mq-agent #285), so the branch was
deleted on 2026-09-13 — but the inventory is evidence that cannot be
reconstructed without redoing the work.

## Known facts (as of 2026-08-04)

Two stores existed:

| Store | Files | Bytes | Last active |
|---|---:|---:|---|
| semantic repository memory (canonical) | 211 | 3.4 MB | 2026-07-16 |
| legacy knowledge store | 101 | 2.2 MB | 2026-06-18 |

Filename overlap between them was zero, but that is a naming artifact — the
canonical store uses a flattened `{repo}__{path}.ext` convention and the legacy
store used bare names. Overlap counts proved nothing either way.

All 101 legacy files were classified:

| Class | Count | Disposition |
|---|---:|---|
| Source path present in git history | 89 | Regenerable |
| Repo sources the name heuristic missed | 3 | Regenerable |
| Generated view of tracked HTML | 1 | Regenerable |
| The store's own upload manifest | 1 | Bookkeeping |
| Rendering of a tracked shell script | 1 | Regenerable |
| Swedish command guides, in no repo | 6 | **Rescued 2026-08-03 into this vault** |

The store's own `upload-manifest.md` (dated 2026-06-18) independently confirmed
the classification: it maps every uploaded filename back to a repository path.

### The one file whose source was not obvious

The largest entry, 62184 bytes, was a terminal guide with no plain source. The
tracked HTML it came from yields only 98 bytes of static text — its content
lives in a `COMMANDS` array of 297 entries inside a large inline script block.
Eight distinct strings sampled from the store's copy appear verbatim in the
tracked HTML, and the size matches a rendering built from the English
description fields. It is a generated view of tracked data.

## Conclusion

The legacy store contained nothing that was not either in git or already
preserved in this vault. There was no content left to migrate, so the memory
question no longer blocked the move.

## What this does not license

Retiring the legacy store is a **separate operation** with its own gate, and
that gate is not met. Four macos-scripts shell consumers still name the legacy
store as their fallback, and one of them has no canonical fallback at all —
retiring the store before they are repointed would break the terminal guide
silently. That work is tracked in the macos-scripts roadmap, not here.

## Method note

The largest file could not be downloaded: the API refuses direct download of
files uploaded for assistant use. Its content was read through search results
instead. The reusable form of that technique is recorded in the learn surface,
not in this node.
