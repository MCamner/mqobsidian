# mq-agent Integration

`mq-agent` is the orchestrator in the MQ stack.

## Relationship

`mq-agent` should export high-value, durable state into `mqobsidian`, such as:

* stack summaries
* release readiness snapshots
* reviewed action outcomes
* dashboard-ready truth summaries

## Rule

`mqobsidian` stores the memory of a run, not the live control logic of the run.
