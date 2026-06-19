# Active Contract: mq-agent

## Owns

* CLI workflow orchestration
* stack gates and release checks
* memory query and context export commands
* agent-view rebuild and drift checks
* safe execution routing through approval gates

## Does Not Own

* durable Obsidian storage format
* low-level MCP tool execution
* repo-signal scoring internals
* mqobsidian note curation
* endpoint runtime execution

## Rules

* Treat this file as routing context, not runtime truth.
* Verify current code, tests, CLI behavior, and contracts in the target repo.
* Do not duplicate behavior owned by another MQ repo.
