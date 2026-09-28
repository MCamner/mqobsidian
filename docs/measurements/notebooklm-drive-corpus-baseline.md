# NotebookLM Drive Corpus Baseline — D1

**Measured:** 2026-09-28  
**Mode:** read-only Google Drive metadata scan  
**Corpus:** configured `NotebookLM Archive` root  
**Content reads:** none  
**Drive mutations:** none

## Purpose

Establish the first reproducible baseline for the Drive-backed NotebookLM corpus
before a catalog schema, retrieval implementation or semantic index is added.

This measurement answers four questions:

1. How is the archive physically organized?
2. How much material exists by evidence role and MIME type?
3. Can source, derived and interaction material be separated without reading
   every file body?
4. What query set should later retrieval work be measured against?

The report intentionally contains no Drive file or folder identifiers and no raw
chat/source content.

## Observed archive structure

The configured archive has **199 notebook folders** plus one reserved
`_manifest` folder.

Notebook boundaries are structural rather than inferred from filenames. Each
notebook is a direct child of the corpus root, and the notebook exports use
named role folders beneath that notebook:

```text
Notebook
  ├─ Sources
  ├─ Artifacts
  ├─ Chat History
  └─ Notes          optional
```

Observed role-folder coverage:

| Role folder | Notebooks with folder | Coverage |
| --- | ---: | ---: |
| Sources | 199 | 100% |
| Artifacts | 176 | 88% |
| Chat History | 186 | 93% |
| Notes | 91 | 46% |

Artifact exports can contain one additional directory level for a generated
artifact. In the measured sample and full artifact metadata scan, those nested
artifact folders contained files and no deeper folders.

This gives a deterministic notebook-to-file relationship without reading file
bodies.

## File inventory

The complete metadata pass counted **2,456 files** totaling
**4,579,080,519 bytes** (about 4.26 GiB).

| Evidence lane | Files | Bytes | Observed MIME types |
| --- | ---: | ---: | --- |
| Source | 1,578 | 358,156,861 | 1,578 HTML |
| Derived artifact | 338 | 4,217,496,352 | 78 Markdown, 153 PDF, 107 PPTX |
| Interaction — chat | 186 | 2,543,307 | 186 HTML |
| Interaction — notes | 354 | 883,999 | 354 HTML |
| **Total** | **2,456** | **4,579,080,519** | |

Observed file modification timestamps span
`2026-09-27T04:23:04Z` through `2026-09-27T15:38:56Z`.

No file body was fetched to produce these counts.

## Source-role classification

The export structure itself is a stronger classifier than filename or extension,
so D1 uses the parent role folder as the initial classification signal.

| Export lane | D1 role | Confidence | Rule |
| --- | --- | --- | --- |
| `Sources/` | source | high | Collected/original input lane. Still not automatically authoritative; later answers must evaluate the actual source. |
| `Artifacts/` | derived | high | NotebookLM-generated material. Never primary evidence when an underlying source is available. |
| `Chat History/` | interaction | high | Prior questions/answers. Useful for gap analysis, never factual evidence. |
| `Notes/` | interaction/supporting | conservative | Notes may be user-authored or generated; until explicitly reviewed they do not establish claims. |

Eight notebooks across AI/MCP, enterprise architecture, grappling, guitar,
periodicals and NotebookLM-learning topics were sampled at metadata level. The
same role-folder pattern held across the sample. No content read was needed to
separate source, derived and interaction lanes.

Classification remains overridable in a future local catalog. A role folder is
not a claim that the contained material is factually correct.

## Duplicate baseline

D1 deliberately does not hash or download the corpus.

Using exact metadata equality within deterministic scan partitions
(`title + MIME type + byte size`) found a **conservative lower bound of 7
duplicate-candidate groups involving 14 source files**.

No duplicate candidate was observed in the completed chat or notes scans, and
none was observed within either artifact scan partition.

This is **not an exact archive duplicate count**:

- equal metadata does not prove equal content;
- duplicates that land in different scan partitions can be missed;
- no source content hash was read.

The correct D1 conclusion is therefore:

```text
duplicate candidates exist
exact duplicate identity remains unmeasured
nothing is deleted
```

A later catalog may add a content hash only when the file is actually read for a
legitimate retrieval purpose. D1 does not justify bulk downloading solely to
deduplicate.

## Frozen sanitized query set

Use these queries unchanged for the first metadata/text-search baseline unless a
query is technically impossible to express. They cover distinct archive
domains and one negative-retrieval case.

1. `MCP server i Python`
2. `agentisk AI och autonoma system`
3. `TOGAF 10 och enterprise architecture`
4. `IGEL OS 12 administration och säkerhet`
5. `BJJ principer och positionskontroll`
6. `blues-skala och pentatoniska gitarrmönster`
7. `mq-corpus-no-such-topic-9f3c7b` — negative control; expected to return no
   relevant result.

For each later retrieval run record at minimum:

- top-k returned notebooks/files;
- source role per candidate;
- number of metadata candidates considered;
- number and bytes of file bodies fetched;
- latency and Drive calls;
- whether the negative control correctly abstains.

## Ownership decision

No new decision record is required for D1.

The observed archive shape does not conflict with the accepted NotebookLM
boundary:

- Google Drive remains storage authority for raw external material;
- `mqobsidian` owns durable contracts and evaluation definitions;
- `mq-agent` is the intended owner of selection and orchestration;
- NotebookLM-derived artifacts remain external derived material;
- interaction history is not evidence;
- durable conclusions still require the existing review/promotion path.

Creating another ownership decision would duplicate an already compatible
boundary rather than resolve a conflict.

## D1 exit result

```text
configured corpus root known locally              PASS
notebook-to-file relationship deterministic       PASS
representative source roles explicit              PASS
tracked report needs no raw content or Drive ids  PASS
frozen sanitized query set exists                 PASS
Drive mutation                                    NONE
file-body reads                                   NONE
```

**D1 is complete.**

The next roadmap step is D2: decide whether a named consumer now needs a stable
`notebook-corpus-index.v1` contract. The existence of this baseline alone does
not require a schema.
