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

Verified routing outcomes use the `mq.model-route-outcome.v1` contract, canonical
here in `schemas/`. mq-agent vendors it and gates its copy against this one
(mq-agent #216); the contract's meaning is unchanged by that move. See
[Verified routing outcomes](ROUTING_OUTCOMES.md) for the local append-only
writer and report handoff.
