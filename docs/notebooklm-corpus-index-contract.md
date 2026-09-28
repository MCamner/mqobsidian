# Notebook corpus index contract

**Contract:** `notebook-corpus-index.v1`  
**Owner:** `mqobsidian`  
**Named consumer:** future `mq-agent` Drive-corpus catalog/search path

## Purpose

Define the smallest stable metadata contract that `mq-agent` needs to build,
inspect and later search a disposable local catalog of the configured NotebookLM
archive.

The contract contains metadata only. It is not a cache of file bodies and it is
not durable MQ memory.

## Why a schema is justified now

D1 established a real corpus and a concrete consumer boundary:

- `mq-agent` must navigate notebook/file relationships before selective fetch;
- source role must survive catalog materialization;
- item identity must remain stable when a display title changes;
- content hashes, when available, must support duplicate grouping across
  notebooks;
- unknown classification must stay explicit rather than be guessed.

That is enough consumer need to freeze a v1 metadata shape before D3 writes a
builder.

## Contract shape

Top level:

```text
schema
corpus.key
corpus.provider
snapshot_at
notebooks[]
items[]
```

A notebook record carries only stable logical identity, its opaque Drive item
identity and its current display title.

A file record carries:

```text
item_id
drive_item_id
notebook_id
parent_drive_item_id
title
mime_type
size_bytes
modified_time
origin_provider
content_sha256?       optional, only when actually measured
classification
```

Classification is explicit:

```text
role =
  source
  derived
  derived-note
  interaction
  metadata-or-other
  unknown

method =
  structural
  override
  unknown
```

An override must include `override_provenance`.

## Determinism and duplicate semantics

D3 must emit notebooks ordered by `notebook_id` and items ordered by
`item_id`. Rebuilding the same source snapshot therefore yields the same
logical catalog.

No separate duplicate object is stored in v1. Records sharing the same measured
`content_sha256` are the duplicate relationship. This avoids storing two
competing representations of the same fact and preserves the D1 rule that a
duplicate is a relationship, never an instruction to delete a file.

## Identity

Display titles are labels, not identity.

`notebook_id`, `item_id` and Drive item identities are opaque. D3 may derive
the logical IDs deterministically from stable provider identity, but consumers
must never reconstruct identity from a title or path.

Every item record represents exactly one Drive item and references exactly one
catalog notebook.

## Privacy and truth boundary

The tracked schema and example contain no real Drive IDs, connector tokens,
sharing metadata, chat text or file bodies. A real generated catalog is local,
disposable and must not be committed.

Deleting that local catalog loses no canonical knowledge: Drive remains corpus
storage and `mqobsidian` remains the owner of the contract and reviewed
distillation.

## D3 hand-off

D3 may now implement only the deterministic materializer against this contract.
It must not change v1 fields merely to fit convenient implementation details.
A contract change requires an explicit schema revision.
