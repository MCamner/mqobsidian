# Skill selection contracts

mqobsidian owns the declarative vocabulary and schemas; source repositories
own skill profiles. mq-agent owns inventory, task profiling, eligibility,
selection and rendering. No selector or private vocabulary copy belongs in
mq-hal, repo-signal, macos-scripts or this vault.

## Contracts

* `skill-selection-vocabulary.v1`: `.mq/skill-selection-vocabulary.json` supplies
  intent, domain and risk aliases plus total and optional selection budgets.
  Consumers match aliases case-insensitively at word boundaries.
* `mq.skill-profile.v1`: source-owned `skill-profile.json` beside `SKILL.md`.
  All intent/domain/risk values must exist in the vocabulary. `required_for`
  contains risk identifiers. `supersedes` references existing profile IDs and
  must be acyclic. All fields are required; unknown properties are rejected.
* `mq.skill-route.v1`: one deterministic task selection. No timestamps, private
  filesystem paths, learning metrics or execution outcomes belong in this record.

The default budget is five total and three optional. Available required skills
are never removed by budget or supersession. Required overflow uses SKS007.
A matched description never creates a requirement; only `required_for` does.

`both` requests Codex and Claude. Optional skills can serve a subset; required
skills must resolve for every target. Supported targets are declared metadata;
discoverable targets are observations of the matching source document in the
agent's discovery directory. `missing_required` lists unavailable targets.

Selection states are `complete`, `partial`, `empty`, `invalid`. An invalid
contract or profile takes precedence over partial availability. No selection
without requirements is empty; a missing requirement is partial, never empty.
An unavailable vocabulary yields invalid without fallback semantics.

## Reason codes

| Code | Meaning |
| --- | --- |
| SKS001_VOCABULARY_UNAVAILABLE | Owner vocabulary or schema cannot be read |
| SKS002_VOCABULARY_INVALID | Owner vocabulary or schema malformed |
| SKS003_SKILL_PROFILE_INVALID | Invalid profile, source identity or references |
| SKS004_SKILL_NOT_DISCOVERABLE | Active matching skill not observed for target |
| SKS005_REQUIRED_SKILL_UNAVAILABLE | Required skill unavailable for a target |
| SKS006_SKILL_SUPERSEDED | Replaced by a surviving, equally/more relevant skill |
| SKS007_SELECTION_BUDGET_APPLIED | Optional truncation or required overflow |
| SKS008_NO_MATCH | No eligible skill selection |
| SKS009_TARGET_UNSUPPORTED | Profile does not support requested target |

Codes are API; message text is explanatory. Scope orders repo skills before
stack-only generic skills when relevance ties. Explicit disjoint task/skill
intents exclude optional candidates, preventing read-only skills from routing
implementation solely through a shared domain.

## Compatibility decision

`context-pack.v1` remains unchanged. mq-agent may render skills in Markdown,
but the route remains a separate machine contract. `mq.execution-outcome.v1`
remains unchanged. Outcome learning and ecosystem audit integration are deferred.

Land these owner contracts before the consuming mq-agent feature. Consumer
tests may use snapshots as fixtures, never as runtime fallback contracts.

## Published examples and CI

The vocabulary artifact is its own executable contract example. The static
[skill profile](../examples/skill-profile.example.json) and
[skill route](../examples/skill-route.example.json) demonstrate the two remaining
schemas. The route is an illustrative deterministic selection, not a runtime log.

`tests/test_skill_selection_contracts.py` checks the published examples, schema
identifiers, strict properties, and contract registration. The Public Safe Check
workflow runs it through unittest discovery alongside the artifact invariant.
