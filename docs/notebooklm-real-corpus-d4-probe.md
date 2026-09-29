# NotebookLM real-corpus D4 bounded probe

**Measured:** 2026-09-29  
**Corpus:** configured Drive-backed NotebookLM archive  
**Mode:** read-only, metadata/provider-search only

## Purpose

Record a real-corpus retrieval probe against the frozen D4 query set without
claiming that a complete current D3 catalog was materialized locally.

This measurement uses the connected Google Drive read surface and the same D4
lexical intent: exact query terms, bounded candidates, explicit source-role
inspection, no semantic expansion and no file-body fetch.

## Current root projection

The archive root currently exposes:

- 204 top-level items;
- 203 folders;
- one root metadata file;
- 201 notebook-folder candidates after excluding the manifest folder and one
  empty container folder.

This is a current storage-projection observation. It does not replace the D1
snapshot.

## Frozen query results

| Query class | Result | Observation |
| --- | --- | --- |
| MCP server in Python | PASS | Multiple notebook/file candidates found; an original source file matched more strongly than a related derived artifact |
| Agentic AI / multi-agent systems | PASS | Real source material and derived artifacts found across multiple notebooks |
| TOGAF 10 / enterprise architecture | PASS | Original TOGAF-related source material found under a typed source folder |
| Pentatonic guitar / rock licks | PASS | Relevant original source material found through Drive text/provider search despite weaker notebook-title recall |
| Source before NotebookLM artifact | PASS | Real notebooks expose both typed Sources and Artifacts; D4 role ordering keeps source ahead when relevance ties |
| Akkadian cuneiform accounting tablets | PASS | Zero Drive provider hits and zero notebook-title candidates; no broadening was performed |

## Retrieval truth boundary

The probe fetched metadata only.

```text
file bodies fetched: 0
bytes fetched:       0
Drive mutation:      0
semantic expansion:  0
```

The positive queries prove that relevant real-corpus material is reachable
without scanning file bodies. The negative control proves that the retrieval
path can abstain.

## Source-role observation

Representative real notebooks preserve the expected typed structure:

```text
Sources/
Artifacts/
Chat History/
Notes/        optional
```

Original source files were observed under `Sources/`; generated reports,
slides/images and other NotebookLM output were observed under `Artifacts/`.

At least one notebook also has files flattened at notebook root. Those records
remain conservative `metadata-or-other` or `unknown` rather than being
promoted by filename or MIME type.

## Limitation

This is a bounded real-corpus gate probe, not a complete adapter-produced D3
catalog.

Attempts to reconstruct the whole corpus through the conversational Drive
connector hit provider/tool enumeration limits. A broad metadata search also
returned a capped subset and therefore cannot serve as a truthful full-corpus
inventory.

The complete-catalog requirement remains operationally pending until the merged
`mq-agent notebook inventory` adapter runs with an authorized local Drive
OAuth token and writes a current disposable D3 input/catalog.

## Decision

The real-corpus D4 retrieval behavior passes the frozen qualitative gate:

- positive topics are retrievable;
- source-role ordering is observable;
- no file bodies are required for the baseline;
- the negative control remains no-result.

This does **not** unlock D5 yet. D5 remains blocked on a complete current
adapter-produced D3 catalog plus the same frozen queries executed over that
catalog.
