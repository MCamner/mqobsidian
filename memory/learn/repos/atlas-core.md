---
type: learn
system: atlas-core
status: verified
date: 2026-09-29
tags: [atlas-core, loop, repo-review, evidence, ci, release-gates]
source_evidence_refs:
  - https://github.com/MCamner/atlas-core/pull/127
  - https://github.com/MCamner/atlas-core/commit/8b7e4bfc34f41dc8c4af7855eac1cd6f170b478e
  - https://github.com/MCamner/atlas-core/actions/runs/36606444857
---

# Atlas Core — observation is not enough without a producer

## Lesson

A repo-review loop can successfully route, plan, read the correct files and preserve evidence, yet still end in `no_on_topic_finding` when no deterministic producer owns the question being asked.

Prompt-tuning is not the fix for that failure mode.

The correct repair is:

1. define a narrow review topic,
2. name the exact sources that can answer it,
3. add a deterministic producer that turns those observations into typed findings,
4. let the existing checker/evaluator decide whether those findings hold,
5. stop honestly when the producer cannot establish the relation.

## Evidence

Repeated runs against `mq-agent` read `release-check.sh`, GitHub workflow files and `scripts/check-gate-parity.py`, but still exhausted the loop with:

```text
findings_are_on_topic
no_on_topic_finding
```

The cause was not missing observation. `atlas_core/review_producers.py` had producers for CI test-command parity, changelog/package-version parity and release-metadata parity, but none for local release-gate versus CI gate parity.

Atlas Core PR #127 adds the missing vertical slice:

```text
ci_gate_parity
  -> exact source plan
  -> deterministic gate comparison
  -> typed source-bound findings
  -> evaluator
```

It also keeps the distinction between:

- **declared gate parity** — checks/targets agree in the observed files,
- **runtime success** — the checks actually passed in CI.

The producer may establish the first. It must not claim the second.

## Reuse

Apply this pattern whenever Atlas repeatedly reaches:

```text
observe ✅
route   ✅
plan    ✅
verify  ✅
finding ❌
```

Do not add more iterations or broaden the prompt first. Inspect whether the route has a producer capable of expressing the requested relation as checkable findings.

## Operational rule

For deterministic repo-review tasks, prefer a small vertical producer over a general-purpose prose generator when the relation can be computed from observed source text.

Exact source plans should remain bounded. Repository metadata such as `.DS_Store` is not evidence and should not consume observation budget.

## Verification

Verified on 2026-09-29 after Atlas Core PR #127 was squash-merged as
`8b7e4bfc34f41dc8c4af7855eac1cd6f170b478e` and the exact-main GitHub
Actions test run `36606444857` completed successfully. That run included the
pinned end-to-end `mq-agent` gate-parity smoke test as well as unit tests,
mypy, pyright, pip-audit, secret scanning, reproducible build and SBOM gates.
