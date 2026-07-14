# Template: codegraph-contract-map.v1

Canonical shape for a cross-repo contract record (Roadmap: CodeGraph MQ
Integration → Delivery B). The map is a JSON document validated against
`schemas/codegraph-contract-map.v1.json`; this template documents the record
shape and the rules for filling one in. See
`examples/codegraph-contract-map.example.json` for a complete public-safe
instance and `docs/CODEGRAPH_CONTRACT_MAP.md` for the operating guide.

## Record skeleton

```json
{
  "contract": "<schema-id, e.g. repo-review.v1>",
  "schema_source": "schemas/<schema-id>.json",
  "producer": {
    "repo": "<producer repo basename>",
    "entrypoint": "<repo-relative file or CLI command that emits the contract>",
    "symbol": "<repo-local implementation symbol; omit if not implemented>"
  },
  "consumer": {
    "repo": "<consumer repo basename>",
    "surface": "<repo-relative read surface or consuming symbol>"
  },
  "verification": {
    "command": "<command that verifies the contract end-to-end>",
    "status": "verified | unverified | planned",
    "evidence_timestamp": "<ISO 8601, when the command last passed>"
  },
  "notes": "<optional ownership/boundary note>"
}
```

## Rules

- **Provenance required.** `schema_source` must point at the owning schema in
  `mqobsidian/schemas/`. A record without a source schema is invalid.
- **No absolute machine paths.** Every value is a repo basename, a repo-relative
  path, or a symbol name. Absolute paths (`/Users/...`, `$HOME`, leading `/`) are
  rejected by `scripts/validate-export.py`.
- **CodeGraph is repo-local only.** Use CodeGraph to find the producer/consumer
  `symbol` inside a single repo. Do **not** claim a cross-repo call — repos are
  joined only through this declared record.
- **Honest status.** `verified` requires that `verification.command` has actually
  passed; use `unverified` when the wiring exists but is unproven, and `planned`
  when the producer or consumer does not exist yet (omit `symbol` in that case).
- **Public-safe.** Records live in the tracked, public surface; they must contain
  no secrets, tokens, or private paths.
