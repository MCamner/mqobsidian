# Truth Export

Truth export converts validated MQ signals into compact, sanitized durable
memory records.

## Export Sources

Typical exporters include:

- `mq-agent` stack summaries and release readiness snapshots.
- `mq-mcp` review and learn outputs.
- `repo-signal` readiness or inspect JSON.
- `mq-ums` endpoint readiness outputs.

## Export Requirements

Before writing to `mqobsidian`:

- validate the output shape
- keep the schema version
- include repo or system provenance
- remove secrets and machine-specific details
- prefer compact summaries over raw dumps

## Example Flow

```text
repo-signal report.v1
  -> sanitize names and paths
  -> map into stack-truth.v1
  -> store as durable memory
```

## Boundary

`mqobsidian` stores the memory of truth. It does not become the live runtime or
release gate.
