---
schema: decision-record.v1
decision_id: DEC-006
created_at: 2026-09-07T00:00:00Z
title: Extend mq.execution-outcome.v1 additively for optional runtime provenance
status: accepted
---

# Decision

## Context

`mq.execution-outcome.v1` is owned here. Consumer repositories may vendor the
schema, but they do not get to redefine it independently: `.mq/repo-contract.json`
declares this repository as the contract source, and mq-agent's vendoring gate
requires its copy to match the canonical file before it can merge or package a
change.

That ownership matters for runtime provenance. mq-agent Phase 5.2 wants to record
which runtime produced an execution observation. The first question is not the
field shape or its policy effect; it is whether adding that evidence means
extending `mq.execution-outcome.v1` or creating `mq.execution-outcome.v2`.

The current contract is strict: `additionalProperties: false`, nineteen declared
properties and eight required properties. It also already states the historical
rule that drives this decision: counters a runtime does not measure are absent,
and absent is not zero. Historical records are append-only and are not backfilled
merely because a later producer learns to observe more.

This repository already has precedent for additive evolution without a major
schema-name change. The changelog records all of these while keeping `.v1`:

- `mq.model-route-outcome.v1` gained optional `application`;
- `mq.model-route-outcome.v1` gained optional `execution_run_id`;
- `memory-query.v1` gained optional `repositories`.

The same history records the other side of that rule. `route` in
`mq.execution-outcome.v1` was deprecated rather than removed because changing
whether new producers write a field is different from invalidating records that
already carry it. Removal is reserved for a later contract version.

So the repository's working versioning rule is semantic rather than cosmetic:
adding optional evidence that leaves every old record valid is an additive v1
change; removing, redefining or making existing data invalid is a later-version
change.

There is, however, a real compatibility cost that the additive rule must not
hide. Because the schema is closed, adding a new optional property gives
**backward compatibility but not forward compatibility**:

- a new schema accepts historical records that do not contain the new field;
- an old schema rejects newer records that do contain it as an additional
  property.

That second case is observable in mq-agent's append-only execution store. An
older mq-agent reading records written by a newer mq-agent can currently route a
healthy newer record into its `invalid_records` path. `_split_contracts` is the
known consumer seam where this shows up.

Creating `mq.execution-outcome.v2` does not solve that mixed-version-reader
problem. An older reader does not know the new schema identity either; a version
bump makes the incompatibility explicit, but does not make an old reader able to
understand new records. A new contract version is therefore the wrong tool when
the data change itself is additive and old records remain semantically valid.

## Decision

**Runtime provenance is added to `mq.execution-outcome.v1` as optional evidence;
it does not create `mq.execution-outcome.v2`.**

The canonical contract change lands in mqobsidian first. Consumer repositories
then update their vendored copies through their existing drift gates before they
write or rely on the new field.

The field is optional. Historical records are not backfilled. Its absence means
that runtime provenance was not observed for that execution; it must never be
interpreted as a mismatch, a false value or proof that the runtime was current.

This decision fixes only the versioning rule. It deliberately does **not** decide:

- the final property name or nested shape of the runtime fingerprint;
- whether a `running` versus `checkout` mismatch such as RTP010 blocks an
  operation;
- whether stack-wide provenance belongs in `runtime_guard`, a release gate, or
  presentation.

Those are separate Phase 5.2 decisions. In particular, a stale mq-mcp process
does not by itself make an unrelated mq-agent execution unattributable, so a
stack-wide policy must not be smuggled into this contract decision.

## Consequences

- **No `mq.execution-outcome.v2` is introduced for optional runtime provenance.**
  A later version is reserved for an incompatible semantic change such as
  removal, redefinition, or a requirement that invalidates historical v1 data.
- **The schema remains closed.** `additionalProperties: false` continues to make
  undeclared producer output a contract error; the new property becomes legal
  only after the canonical schema explicitly declares it.
- **Historical execution observations remain immutable and valid.** They carry
  no synthesized runtime fingerprint and require no migration or backfill.
- **Consumer sequencing is owner first, vendor second.** mq-agent may not invent
  the field locally and reconcile later; mqobsidian publishes the canonical
  shape first, then mq-agent updates its vendored contract and writer/reader.
- **Forward incompatibility is explicit debt, not corruption to ignore.** Before
  a producer starts emitting the new field, mq-agent must have a regression test
  for a mixed-version store showing what an older schema does with a newer
  record. `_split_contracts` is the known read boundary. Whether the long-term
  answer is an upgrade requirement or a distinct "newer contract" classification
  is a consumer-policy decision, not permission to loosen the canonical schema.
- **A v2 would not avoid that reader problem.** Unknown schema identity is at
  least as incompatible with an old reader as an unknown property on v1, while
  also implying a semantic break that this change does not contain.
- **Absence stays epistemic.** Missing runtime provenance means "not observed",
  never "matched", "healthy" or `false`.

## Verified basis

The decision rests on repository behavior already present rather than a new
versioning policy invented for Phase 5.2:

- `.mq/repo-contract.json` lists `mq.execution_outcome.v1` among contracts owned
  by mqobsidian and states that consumers may validate against these shapes but
  must not redefine them locally.
- `schemas/mq.execution-outcome.v1.json` is closed with
  `additionalProperties: false`, has nineteen properties, eight required fields,
  and already documents absent measurements as absent rather than zero.
- `CHANGELOG.md` records multiple additive optional-field extensions that kept
  their `.v1` identity, and records retention of deprecated execution data so
  existing observations remain valid.
- The consumer experiment with one current execution record and one record
  carrying a future optional field produced one valid record and one
  `invalid_records` entry under the older schema. The incompatibility is real
  and must be tested, not inferred away.

## Related

- DEC-002 — mqobsidian owns truth surfaces; the contract changes at the owner,
  not in a consumer first.
- DEC-003 — strict schema enforcement; keeping `.v1` does not mean accepting
  undeclared fields.
- DEC-004 — a contract must correspond to a real producer and enforceable
  behavior; the future runtime field is not added until its producer semantics
  are defined.
- `schemas/mq.execution-outcome.v1.json` — canonical execution-observation
  contract.
- `CHANGELOG.md` — additive-v1 precedents and the existing deprecation rule.
