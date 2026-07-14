# CodeGraph cross-repo contract map

The contract map traces each MQ schema contract from the repo that **produces**
it, through the repo that **consumes** it, to the command that **verifies** it —
without pretending the MQ stack has one federated code graph. It is the Delivery
B artifact of the "CodeGraph MQ Integration" roadmap block.

- Contract: `schemas/codegraph-contract-map.v1.json`
- Template: `templates/codegraph-contract-map.md`
- Example: `examples/codegraph-contract-map.example.json`

## Why this exists

Each MQ repo has an independent CodeGraph index. CodeGraph answers repo-local
questions (where is this symbol, who calls it) but cannot see across repo
boundaries. The gap is not a bigger graph — it is an explicit, declared record of
which repo emits a contract and which repo reads it. This map is that record.

```text
producer repo/symbol  --(schema contract)-->  consumer repo/surface
         |                                              |
         +----------------- verified by ----------------+
                     verification.command
```

## Boundary

- **CodeGraph upstream** owns parsers, symbol extraction, and repo-local graph
  edges. It is used only to find the producer/consumer symbol inside one repo.
- **mqobsidian** owns this contract metadata: the record schema, provenance to the
  owning schema, and the public-safe example. It does **not** build a second graph
  engine and does **not** infer cross-repo calls from static edges.
- **mq-agent** owns orchestration: running the verification commands and recording
  outcomes (Delivery D). This map only declares them.

## Contracts mapped first

| Contract | Producer | Consumer | Status |
| --- | --- | --- | --- |
| `context-pack.v1` | mqobsidian `render_pack` | mq-agent `build_task_pack` | verified |
| `repo-review.v1` | repo-signal `export_repo_review` (`review-export`) | mqobsidian `memory/reviews/` | verified |
| `endpoint-truth.v1` | mq-ums `endpoint-truth` | mq-agent context selection | planned (no producer yet) |
| `feedback-signal.v1` | mq-agent usage emitter | mqobsidian `feedback/` | unverified (emitter not wired) |

The two `verified` rows have passing verification commands. `endpoint-truth.v1`
carries no implementation symbol because no producer exists in mq-ums yet;
`feedback-signal.v1` is `unverified` because the mq-agent emitter is a separate
gated producer track that is not yet wired in code. Both are recorded honestly so
the map shows real coverage, not aspiration.

## Validation

The example is validated structurally in CI without requiring a local CodeGraph
installation:

```bash
python3 scripts/validate-export.py
python3 scripts/check-sensitive-content.py
```

`validate-export.py` enforces the `codegraph-contract-map.v1` schema const, the
required keys, the `verification.status` enum, and rejects any absolute machine
path in the record.
