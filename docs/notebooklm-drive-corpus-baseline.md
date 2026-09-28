# NotebookLM Drive corpus baseline

**Measured:** 2026-09-28  
**Scope:** read-only metadata and the archive's generated manifest in Google Drive  
**Roadmap slice:** D1 / Phase 0 of the Drive-backed NotebookLM corpus track

## Purpose

Establish what the existing NotebookLM archive actually contains before MQ
builds a catalog or retrieval path around it.

This measurement does not evaluate NotebookLM as an answering provider. The
earlier provider evaluation remains closed. It measures the Drive archive as an
external research corpus.

No raw source body, chat transcript, Drive identifier or credential is recorded
in this tracked report.

## Measurement boundary

The configured corpus root is the Drive folder displayed as
`NotebookLM Archive`.

The archive publishes its own generated manifest under a private manifest
subfolder. D1 reads that manifest plus Drive folder metadata rather than opening
all 6,914 file bodies.

Manifest snapshot:

```text
generated at       2026-09-28T16:32:50Z
processed files    6,914
declared notebooks 200
archive bytes      8,851,758,063 bytes / 8.244 GiB
source generation  one completed Takeout generation, five ZIP parts
```

Drive currently exposes 200 top-level folders under the corpus root: 199
notebook folders plus the manifest folder. The apparent 200-versus-199 notebook
difference is explained by one malformed manifest record with an empty notebook
name and a single root metadata file. It is not a usable notebook boundary and
must remain invalid/unknown rather than being assigned to another notebook.

The 199 valid notebook folders have Drive modification timestamps ranging from
2026-09-27T04:23:04Z to 2026-09-27T15:38:56Z. The generated manifest is newer,
so later phases must distinguish archive snapshot time from folder modification
time.

## Inventory by file type

| Type | Files | Size |
| --- | ---: | ---: |
| PNG | 2,226 | 3.311 GiB |
| PDF | 153 | 2.186 GiB |
| PPTX | 107 | 1.741 GiB |
| MP4 | 8 | 356.2 MiB |
| HTML | 2,118 | 344.8 MiB |
| WAV | 5 | 249.5 MiB |
| MP4(1) | 1 | 44.8 MiB |
| OTHER | 25 | 31.8 MiB |
| JSON | 2,193 | 1.6 MiB |
| MD | 78 | 0.6 MiB |
| **Total** | **6,914** | **8.244 GiB** |

The manifest also records 2,101 normalized extensionless PNG files and eight
shortened destination paths. Those are transformation facts, not evidence
roles.

## Notebook boundaries

For valid notebooks the archive has a stable two-level pattern:

```text
<notebook>/
  <notebook> metadata.json
  Sources/
  Artifacts/
  Chat History/
  Notes/              optional
```

This gives two independent reconstruction signals:

1. the generated manifest records `notebook` and `destination_path` for every
   processed file;
2. the Drive projection uses one notebook parent folder with typed child
   folders.

For D1 the generated manifest is the snapshot authority because it accounts for
all 6,914 processed files and exposes content hashes. The Drive folder tree is
the current storage projection. A later catalog must retain both concepts
instead of inferring notebook identity from a display title alone.

The malformed empty-name record proves why this matters: a title is not a
sufficient identity.

## Source-role classification baseline

Classification is structural, not extension-based:

| Archive location | D1 role | Evidence meaning |
| --- | --- | --- |
| `Sources/` | `source` | Candidate original/collected source; authority still depends on the source itself |
| `Artifacts/` | `derived` | NotebookLM-generated output |
| `Notes/` | `derived-note` | Note material; not primary evidence by default |
| `Chat History/` | `interaction` | Prior inquiry only; never claim evidence |
| notebook root / malformed path | `metadata-or-other` | Navigation/provenance metadata or unknown |

Measured coverage:

| Role | Files | Size |
| --- | ---: | ---: |
| source | 3,156 | 342.0 MiB |
| derived | 2,998 | 8,095.8 MiB |
| derived-note | 354 | 0.8 MiB |
| interaction | 186 | 2.4 MiB |
| metadata-or-other | 220 | 0.7 MiB |

6,694 of 6,914 files, **96.8%**, are therefore assignable to an evidence role
from directory structure alone. The remaining 220 stay metadata/unknown; D1
does not guess their authority.

This classifier is explicit and overridable. A file under `Sources/` is only a
source *candidate*; the folder name does not prove that its contents are
accurate, independent or current.

## Representative notebook sample

Five notebooks were sampled across different topics and sizes. Only the already
public MQ notebook is named; the other archive titles are intentionally not
published in this report.

| Sample | Files | Source | Derived | Notes | Interaction | Metadata/other |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| MQ Stack Intelligence | 90 | 46 | 37 | 5 | 1 | 1 |
| Sample B | 23 | 2 | 19 | 0 | 1 | 1 |
| Sample C | 21 | 2 | 17 | 0 | 1 | 1 |
| Sample D | 35 | 4 | 29 | 0 | 1 | 1 |
| Sample E | 26 | 4 | 19 | 1 | 1 | 1 |

The same structural role rules work across all five samples. That is enough for
a D1 classification baseline; it is not evidence that every future or manually
modified notebook will preserve the same layout.

## Duplicate measurement

Duplicate detection uses the manifest's SHA-256 values. No file body was opened
for duplicate comparison.

```text
duplicate hash groups       39
files participating         84
redundant copies            45
estimated redundant bytes   10,740,978 / 10.24 MiB
within-notebook groups      28
cross-notebook groups       11
```

Duplicates are evidence relationships, not deletion candidates. Cross-notebook
copies especially must not be counted as independent sources during later
research.

## Frozen sanitized query set for D4

The following public-safe queries are fixed before search implementation so D4
cannot tune the retrieval path to examples it has already seen:

1. **Exact-topic recall:** “Find sources about building an MCP server in Python.”
2. **Cross-notebook recall:** “What design patterns recur across material about
   agentic AI and multi-agent systems?”
3. **Architecture recall:** “Find material explaining TOGAF 10 and enterprise
   architecture.”
4. **Cross-domain recall:** “Find sources about pentatonic guitar technique and
   recurring rock licks.”
5. **Source-role check:** “For a matching notebook, return original sources
   before NotebookLM-generated artifacts.”
6. **Negative control:** “Find sources about Akkadian cuneiform accounting
   tablets.”

D4 must run these as written. A semantically poor result is a result, not a
reason to rewrite the query after seeing output.

## Ownership decision

No new decision record is required.

The measured corpus does not conflict with the accepted NotebookLM/MQ ownership
boundary:

- Drive owns raw archive storage;
- `mqobsidian` owns durable vocabulary, provenance rules and evaluation;
- `mq-agent` owns future catalog/search orchestration;
- NotebookLM-derived artifacts remain external derived material;
- no archive output writes directly into durable MQ memory.

D1 therefore confirms the existing ownership split rather than creating a new
one.

## Findings that constrain D2/D3

1. **Do not use notebook display title as the sole identity.** The malformed
   empty-name record demonstrates that title-derived identity can fail.
2. **Keep snapshot and live projection separate.** The manifest is a generated
   extraction snapshot while Drive folder timestamps describe the current
   projection.
3. **Represent `unknown` explicitly.** 220 records are metadata or malformed
   rather than source/derived/interaction evidence.
4. **Track duplicate relationships.** Eleven duplicate hash groups cross
   notebook boundaries, so file count is not independent-source count.
5. **Do not create a schema yet.** D1 proves a consumer need for a catalog, but
   D2 should first identify the minimum fields the `mq-agent` consumer will
   actually read before freezing a contract.

## Phase 0 exit gate

- configured corpus root known: **PASS**
- notebook-to-file relationships reconstructible: **PASS**, using manifest
  notebook/path identity with one malformed record retained as invalid
- representative sample has explicit source roles: **PASS**
- tracked report contains no raw corpus body or Drive identifier: **PASS**
- sanitized retrieval query set frozen before implementation: **PASS**

**Result:** Phase 0 / D1 baseline complete. Proceed to D2 only as a contract
design exercise; do not implement catalog materialization in the same PR.
