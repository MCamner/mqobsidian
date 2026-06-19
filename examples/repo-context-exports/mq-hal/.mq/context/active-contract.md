# Active Contract: mq-hal

## Owns

* natural-language operator command routing
* safe JSON-intent handling through a Python allowlist
* operator summaries for stack, release, repo, and CI state
* `mqlaunch hal` command surface integration
* local HAL-style dashboard and brief outputs

## Does Not Own

* MQ-stack runtime truth production
* uncontrolled shell execution from model output
* durable Obsidian memory
* MCP tool implementation
* repo health scoring internals

## Rules

* Treat this file as routing context, not runtime truth.
* Verify current code, tests, CLI behavior, and contracts in the target repo.
* Do not duplicate behavior owned by another MQ repo.
