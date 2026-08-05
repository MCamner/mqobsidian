# mq-agent Integration

`mq-agent` is the orchestrator in the MQ stack.

## Relationship

`mq-agent` should export high-value, durable state into `mqobsidian`, such as:

* stack summaries
* release readiness snapshots
* reviewed action outcomes
* verified model-routing outcomes
* dashboard-ready truth summaries

## Rule

`mqobsidian` stores the memory of a run, not the live control logic of the run.

Verified routing outcomes use mq-agent's `mq.model-route-outcome.v1` contract
unchanged. See [Verified routing outcomes](ROUTING_OUTCOMES.md) for the local
append-only writer and report handoff.
