# NotebookLM Drive corpus baseline — D1

**Measured:** 2026-09-28  
**Mode:** read-only metadata inspection  
**Corpus:** configured NotebookLM archive in Google Drive  
**Purpose:** establish a reproducible baseline before catalog or retrieval code is built

## Scope and method

This baseline inspected the connected Google Drive archive without downloading
the corpus and without reading file bodies. The run used folder metadata,
parent relationships, MIME type, size and modification timestamps.

No Drive identifier, raw source text, chat transcript, credential or private
path is recorded in this tracked report.

Two evidence levels are kept separate:

1. **Live connector measurement** — read-only Drive metadata observed during
   this D1 run.
2. **Archive-builder summary** — the previously recorded migration output from
   the completed NotebookLM archive build. It covers file classes the current
   connector inventory surface did not enumerate in the same paginated
   document/image passes.

The second is retained as operator-recorded evidence, not relabelled as a live
Drive recount.

## Folder topology

The archive root currently exposes:

| Level | Count | Meaning |
| --- | ---: | --- |
| notebook folders | 199 | one first-level folder per exported notebook |
| root manifest folders | 1 | reserved `_manifest` folder |
| role folders | 670 | structural folders immediately below notebooks |
| nested artifact folders | 153 | generated artifact groupings below role folders |
| deeper folders observed | 0 | no fourth folder level in the full traversal |

Role folders observed across the 199 notebooks:

| Folder role | Count | Baseline interpretation |
| --- | ---: | --- |
| `Sources` | 199 | source lane |
| `Artifacts` | 176 | derived lane |
| `Chat History` | 186 | interaction lane |
| `Notes` | 91 | derived lane |
| `Discovered Sources` | 18 | unresolved source candidate; do not promote by folder name alone |

The notebook boundary is therefore reconstructable without reading content:

```text
archive root
  -> notebook folder
     -> Sources
     -> Artifacts
        -> optional artifact folder
     -> Notes
     -> Chat History
     -> optional Discovered Sources
```

The first-level notebook folder is the notebook boundary. Parent relationships
are sufficient to reconstruct file membership deterministically.

## Live MIME inventory

The connector can paginate folders, document-like files and images directly.
Those live passes produced the following exact baseline:

| MIME type | Files | Bytes |
| --- | ---: | ---: |
| `image/png` | 2,226 | 3,555,556,271 |
| `application/pdf` | 153 | 2,347,139,791 |
| `application/vnd.openxmlformats-officedocument.presentationml.presentation` | 107 | 1,869,714,559 |
| `text/html` | 2,118 | 361,584,167 |
| `text/markdown` | 78 | 642,002 |
| **Live connector subtotal** | **4,682** | **8,134,636,790** |

Observed file modification range for those classes:

```text
earliest  2026-09-27T04:23:04.121Z
latest    2026-09-27T15:38:56.810Z
```

The counts for PNG, PDF, PPTX, HTML and Markdown match the prior archive-builder
summary exactly. That is useful cross-check evidence that the folder traversal
is looking at the intended migrated corpus rather than an unrelated Drive
surface.

## Archive-builder inventory

The completed archive build previously recorded:

| Class | Files | Recorded size |
| --- | ---: | ---: |
| PNG | 2,226 | 3.3 GB |
| PDF | 153 | 2.2 GB |
| PPTX | 107 | 1.7 GB |
| MP4 | 8 | 356.2 MB |
| HTML | 2,118 | 344.8 MB |
| WAV | 5 | 249.5 MB |
| MP4(1) | 1 | 44.8 MB |
| OTHER | 25 | 31.8 MB |
| JSON | 2,193 | 1.6 MB |
| MD | 78 | 627.0 KB |
| **Total** | **6,914** | **about 7.9 GB** |

The live Drive connector pass does not claim to have re-counted the JSON,
audio/video and OTHER classes. D3 must make that distinction explicit in its
catalog status instead of pretending the connector-visible subtotal is the
whole corpus.

## Source-role sampling

Ten notebooks were sampled across the root ordering using folder metadata only.

Observed structural coverage in that sample:

| Role folder | Sample presence |
| --- | ---: |
| `Sources` | 10 / 10 |
| `Artifacts` | 9 / 10 |
| `Chat History` | 8 / 10 |
| `Notes` | 6 / 10 |

One notebook was inspected one level deeper. Its source material was stored
under `Sources`, generated notes under `Notes`, prior conversations under
`Chat History`, and generated visual material under `Artifacts`.

The structural classification rule for the next phase is therefore:

```text
Sources             -> source
Artifacts           -> derived
Notes               -> derived
Chat History        -> interaction
Discovered Sources  -> unknown/source-candidate until origin is verified
anything else       -> unknown
```

This is a navigation rule, not a claim that a filename proves authority.
Explicit metadata or a future override must be able to replace the structural
default.

## Duplicate baseline

The document-like corpus was scanned in two independent half-corpus passes using
the metadata signature:

```text
title + MIME type + byte size
```

That found **at least 10 duplicate-candidate groups**, each with two matching
file records. Some are repeated across different notebooks and some are repeated
inside one notebook.

This is deliberately a lower bound:

- the two half-corpus passes do not detect a pair split across the pass boundary;
- metadata equality is not content-hash equality;
- image quarter-scans found no duplicate candidates within their own quarters,
  but that does not prove there are no cross-quarter PNG duplicates.

D3 should therefore compute exact duplicate groups from the complete local
catalog, using stable identity first and content hash only when content is
actually read.

Nothing was deleted or mutated during this measurement.

## Frozen baseline queries

These queries are public-safe and intentionally span different parts of the
corpus. They are inputs to the later metadata/text-search comparison, not
evidence that retrieval already works.

1. `agent orchestration MCP tool interoperability`
2. `enterprise architecture governance target architecture`
3. `closed guard posture break retention`
4. `macOS endpoint management Intune IGEL`
5. `pentatonic guitar phrasing picking technique`
6. `lunar regolith kiln calibration for polar construction` — negative control;
   retrieval should be allowed to return no relevant result

For each later run record top-k relevance, candidates considered, file bodies
fetched, bytes fetched, connector calls, latency and source-role mix.

## Ownership check

The measured Drive structure does not conflict with the accepted NotebookLM/MQ
boundary:

- Drive remains storage authority for the raw archive;
- `mqobsidian` owns durable vocabulary, provenance rules and evaluation;
- `mq-agent` owns future catalog/search/research orchestration;
- NotebookLM-derived files remain external derived material;
- no write-back or automatic promotion is introduced.

A new decision record is therefore **not required** for D1. If later catalog or
runtime work needs a different ownership boundary, that change must create a
new decision before implementation.

## D1 conclusion

D1 is sufficient to open catalog design, with one important honesty constraint:
the next catalog must distinguish a **complete**, **partial** and
**connector-visible** inventory. The 4,682-file live subtotal must never be
reported as the 6,914-file full archive unless the remaining classes have been
enumerated by the catalog implementation.

No schema is created by D1. D2 should create a catalog contract only when the
consumer implementation proves it needs a stable interchange format.
