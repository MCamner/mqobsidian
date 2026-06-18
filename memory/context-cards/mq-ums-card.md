---
schema: context-card.v1
repo: mq-ums
role: Local operator UI for bounded IGEL UMS management
updated_at: 2026-06-19T00:00:00Z
---

# Context Card: mq-ums

## Role

Local operator UI for bounded IGEL UMS management.

## Owns

* browser-based UMS operator workflows
* PSIGEL and PowerShell command wrapping
* allowlisted UMS command execution
* device search, dry-run, audit, and health endpoints
* operator-readable JSON summaries

## Does not own

* arbitrary PowerShell execution
* MQ-stack workflow orchestration
* durable memory curation
* repo health scoring
* MCP runtime contracts

## Reads from

* UMS connection configuration
* PSIGEL command output
* local allowlist configuration
* mq-agent or mqlaunch operator requests

## Writes to

* local browser UI responses
* command history and audit outputs
* structured UMS summaries
* no MQ durable memory unless exported by another layer

## Use this card when

* task involves UMS device operations
* task involves PowerShell safety boundaries
* task touches browser operator workflows
* task needs to separate UMS UI from MQ orchestration

## Avoid reading unless needed

* unrelated MQ release notes
* old browser UI experiments
* raw enterprise logs
* full stack architecture docs
