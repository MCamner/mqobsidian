# NotebookLM real-corpus D5 bounded probe

**Measured:** 2026-09-29  
**Mode:** read-only, bounded source/derived inspection

## Purpose

Validate D5's selective-fetch authority rules against representative live corpus
material without claiming that the complete current D3 catalog has been
materialized.

## Observation

A representative notebook contained both:

- an original/collected source under `Sources/`;
- a NotebookLM-generated Markdown artifact under `Artifacts/`.

The source was an exported HTML representation of an imported PDF. Its file body
began with a large inline base64 image before readable text. The derived
Markdown artifact began with normal readable text.

This exposed an important bounded-fetch edge case: HTTP success does not imply
usable evidence. A small byte-range read of the source HTML can contain only the
inline image payload and no readable text.

## D5 response

The merged D5 implementation therefore treats:

```text
HTTP success + readable text
  -> fetch status ok

HTTP success + no readable text inside the bounded payload
  -> unavailable / no_readable_text_in_budget

unsupported binary MIME
  -> unavailable / unsupported_mime
```

An unavailable source can never become claim-eligible evidence.

## Authority behavior

D5 enforces:

- only `source` can become `claim_eligible=true`;
- derived material remains secondary context;
- interaction material is never fetched as claim evidence;
- derived-only retrieval reports `MISSING_SOURCE`;
- conflicting source excerpts remain separate;
- provider errors remain explicit unavailable records;
- live-runtime scope delegates to current source/runtime tools and performs no
  corpus fetch.

## Fetch budget

The implemented defaults are:

```text
max files           4
max bytes per file  64 KiB
max total bytes     256 KiB
excerpt              4,000 characters
```

No Drive mutation is part of the path.

## Limitation

This probe verifies D5 behavior against representative live corpus structure,
not full-corpus activation. Full activation still requires:

1. a complete current adapter-produced D3 catalog;
2. the six frozen D4 queries passing over that complete catalog;
3. D5 retrieval operating from that catalog without authority violations.

Until then, D5 is implemented but not declared fully activated for the entire
archive.
