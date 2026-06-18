---
schema: context-card.v1
repo: mq-blockers
role: Compact pointer to current MQ blockers and risks
updated_at: 2026-06-19T00:00:00Z
---

# Context Card: current blockers

## Role

Compact pointer to current MQ blockers and risks.

## Owns

* cross-repo blocker summaries
* risk hints for context packs
* reminders to verify runtime blockers in source repos
* short status surfaces for agents

## Does not own

* live runtime diagnosis
* issue tracker authority
* release go/no-go decisions
* source-repo fixes
* unsanitized operational logs

## Reads from

* system hot notes
* stack truth summaries
* review summaries
* source repos when a blocker is runtime-sensitive

## Writes to

* task context packs
* compact blocker summaries
* next-action hints
* no live system state

## Use this card when

* task asks what is currently blocking progress
* task needs risk context before edits
* task crosses several MQ repos
* task should avoid scanning full review history

## Avoid reading unless needed

* stale issue notes
* raw logs
* archived review dumps
* unrelated release history
