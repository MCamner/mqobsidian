---
schema: context-card.v1
repo: mq-release-state
role: Compact pointer to release readiness state across MQ repos
updated_at: 2026-06-19T00:00:00Z
freshness: current
scope: cross-repo
publishability: public-safe
---

# Context Card: release state

## Role

Compact pointer to release readiness state across MQ repos.

## Owns

* release-readiness routing hints
* compact release-state summaries
* pointers to repo-local release checks
* reminders to use live tools before release claims

## Does not own

* final release authority
* source repo version bumps
* changelog authorship
* CI execution
* GitHub release publication

## Reads from

* repo-local `VERSION` and changelog files
* repo release-check outputs
* repo-signal readiness signals
* mq-agent release and stack summaries

## Writes to

* context-pack release hints
* durable release-state summaries
* operator next-action notes
* no repo tags or releases directly

## Use this card when

* task involves release readiness
* task needs current release surfaces to inspect
* task spans multiple repo versions
* task should avoid old changelog archaeology

## Avoid reading unless needed

* historic release notes
* old CI logs
* unrelated roadmap files
* full GitHub release archives
