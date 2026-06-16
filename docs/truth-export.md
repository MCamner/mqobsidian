# Truth Export

Truth export is the process of converting a validated MQ signal into a durable,
sanitized memory record.

## Export sources

Typical exporters include:

* `mq-agent` stack summaries
* `mq-mcp` review and learn outputs
* `repo-signal` readiness or inspect JSON
* `mq-ums` endpoint readiness outputs

## Export requirements

Before writing to mqobsidian:

* validate the output shape
* keep the schema version
* include repo or system provenance
* remove secrets and machine-specific details
* prefer compact summaries over raw dumps

## Example flow

```text
repo-signal report.v1
-> sanitize names/paths
-> map into stack-truth.v1
-> store as durable memory
```
