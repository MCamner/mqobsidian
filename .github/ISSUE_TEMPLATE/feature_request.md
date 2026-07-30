---
name: Feature request
about: Propose a durable-memory, context, schema, or template improvement
title: "[Feature] "
labels: ""
assignees: ""
---

## Problem

What verified workflow or context problem should this solve?

## Proposed change

Describe the smallest useful change and its expected output.

## Ownership boundary

Explain why mqobsidian owns this change. Execution belongs in `mq-mcp`,
orchestration in `mq-agent`, and live repo truth in the relevant source repo.

## Contract impact

List any affected schemas, templates, generated examples, context budgets, or
consumer documentation. Write `none` when no public contract changes.

## Success criteria

- [ ] The behavior is verifiable.
- [ ] Generated and hand-written surfaces remain in sync.
- [ ] The change stays within the public-safe boundary.

## Alternatives

What existing surface or smaller change was considered?

## Public-safe check

Do not include secrets, customer data, private hostnames, machine-specific
paths, or unsanitized operational logs.
