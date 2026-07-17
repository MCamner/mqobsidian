---
schema: decision-record.v1
decision_id: DEC-003
created_at: 2026-07-17T00:00:00Z
title: mqobsidian takes a jsonschema dependency for strict schema enforcement
status: accepted
---

# Decision

## Context

mqobsidian published `schemas/` as consumer contracts and validated its own
output with a hand-rolled checker, `_schema_lite_errors`, deliberately written
to avoid a JSON-Schema dependency. Its docstring described it as "shallow" and
"enough to validate the truth-surface manifest examples".

It was not enough, and "shallow" understated the gap. The checker recursed only
through `properties`. Every keyed manifest declares its records under
`additionalProperties: {<subschema>}` — a schema, not `false` — and the checker
had no branch for that case. The records inside were therefore not inspected at
all. A score record of literal garbage produced zero errors:

```text
scores: {"m-1": {"TOTAL": "GARBAGE", "not_even_a_score": true}}  ->  no errors
```

This was not theoretical. The scoring engine wrote `ebms_state` onto every score
record; `memory-score.v1` is `additionalProperties: false` and declares no such
field. Every published record violated mqobsidian's own contract for weeks. The
producer's validator could not see it. The consumer caught it: mq-agent's export
contract mirrors the schema exactly and rejected the real bundle (#45), while
144 tests here and 906 there were green.

A jsonschema-based test already existed in this repo — and skipped itself when
the library was absent, which was always, in CI. The one real check present was
structurally silent.

## Decision

Take the dependency. `requirements.txt` pins `jsonschema>=4.21,<5`; CI installs
it before any validation step; `validate-export.py` validates against the schema
as written via `Draft202012Validator`.

Alternatives rejected:

- **Keep the shallow validator.** No new dependency, but it cannot enforce the
  contracts this repo publishes, and its failure mode is silent acceptance of
  invalid data. Nothing about this repo's purpose survives that.
- **Extend the hand-rolled checker** to recurse into `additionalProperties`,
  `patternProperties`, `$ref`, `oneOf`, and so on. This is the worst option: it
  is a partial JSON-Schema engine, which is precisely what already existed and
  precisely what failed. Each gap is invisible until data exercises it.

The stdlib-only stance was worth holding while nothing depended on validation
being correct. Consumers now do. A dependency is cheaper than a contract that
cannot be enforced.

## Consequences

- `python3 scripts/validate-export.py` now requires `pip install -r
  requirements.txt`. A bare interpreter fails loudly rather than validating
  nothing.
- Strict validation applies to the built bundle too, via
  `build-truth-exports.validate_bundle`. A non-conforming record fails the build
  and leaves `exports/` untouched instead of publishing.
- The jsonschema-based test no longer skips.
- Producers must publish exactly what the schema declares. Internal engine state
  stays internal; see #45, where score records are projected onto the fields
  `memory-score.v1` declares, read from the schema rather than restated.

## Verified

Re-introducing the `ebms_state` bug against the new validator fails the build
and names the field and every affected record:

```text
export build failed validation; exports/ left unchanged:
  - memory-score-manifest.json: <root>.scores.missing-tests-folder-tests:
    Additional properties are not allowed ('ebms_state' was unexpected)
```

## Related

- DEC-002 — mqobsidian owns current truth surfaces. This decision is what makes
  that ownership enforceable rather than asserted.
