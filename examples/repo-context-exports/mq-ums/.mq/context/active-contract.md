# Active Contract: mq-ums

## Owns

* browser-based UMS operator workflows
* PSIGEL and PowerShell command wrapping
* allowlisted UMS command execution
* device search, dry-run, audit, and health endpoints
* operator-readable JSON summaries

## Does Not Own

* arbitrary PowerShell execution
* MQ-stack workflow orchestration
* durable memory curation
* repo health scoring
* MCP runtime contracts

## Rules

* Treat this file as routing context, not runtime truth.
* Verify current code, tests, CLI behavior, and contracts in the target repo.
* Do not duplicate behavior owned by another MQ repo.
