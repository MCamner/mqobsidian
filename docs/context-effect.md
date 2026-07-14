# Context Effect

This note records whether `mqobsidian` is currently reducing first-read context
for Codex and Claude Code.

## Current measurement

Measured with:

```bash
python3 scripts/measure-context-effect.py --format markdown
```

Task pack:

```text
.mq/context/task-pack.md
```

Relevant repos:

* `mq-mcp`
* `mqobsidian`
* `mq-agent`

Result:

| Context path | Lines |
| --- | ---: |
| Context pack + available cards | 222 |
| Broad first-read baseline | 4797 |
| Avoided first-read lines | 4575 |
| Reduction | 95.4% |

## Interpretation

The context layer is already giving practical effect for the first real MQ task.
Instead of reading broad README, changelog, roadmap, and docs surfaces across
three repos, an agent can start with one task pack and three compact context
cards.

This does not prove every future task will get the same reduction. It does prove
that the current MVP path is useful enough to keep tightening Phase 2.

## CodeGraph source-intelligence measurement (Phase 4.5)

A second, complementary measurement for a *source-structure* task — the kind a
context pack points at but does not itself answer.

Task: trace what feeds CodeGraph notes into a generated pack (who calls
`apply_codegraph_defaults`, and what it calls), measured in `mqobsidian` with a
local `.codegraph/` index (11 files, 116 nodes).

Measured with:

```bash
codegraph node apply_codegraph_defaults        # path: context pack + CodeGraph
grep -rn apply_codegraph_defaults scripts/      # then read the file by hand (baseline)
```

| Context path | First-read lines | Answers caller/callee directly? |
| --- | ---: | :---: |
| Context pack only | 213 | No — points to CodeGraph or the file |
| Context pack + CodeGraph (`codegraph node`) | 42 | Yes — verbatim source + exact edges |
| Broad source-scan baseline (read full file) | 267 | Only after a manual trace |

CodeGraph answered the structure question in **42 lines vs 267** for the broad
baseline (~84% fewer first-read lines) and returned the exact `Called by ← main`
/ `Calls → task_is_source_heavy` edges that grep alone does not surface.

### Interpretation

The two layers do different jobs and the numbers reflect it. The context pack
wins on *memory and orientation* (which repos, which files, prior decisions); it
deliberately does not encode call structure. CodeGraph wins on *source structure*
(callers, callees, impact) for one symbol without a broad read. For source-heavy
tasks the cheapest path is pack-for-orientation **plus** a targeted CodeGraph
query — which is exactly what `apply_codegraph_defaults` now nudges agents toward.

`.codegraph/` stays local and git-ignored (self-ignored via
`.codegraph/.gitignore`); none of it is committed or exported.

## Cross-repo measurement — `fix mq-mcp brain writer paths` (Phase 4.5)

The first "minimum first task" from the roadmap, now that the whole stack is
indexed (`mq-mcp` = 74 files / 1,584 nodes). This is the real MVP task the
context pack was built for, re-measured with CodeGraph on the source side.

```text
Task:                fix mq-mcp brain writer paths
Repo:                mq-mcp (+ mqobsidian schemas, mq-agent vault docs)
With context pack:   pack names exact writer/wrapper/test/contract files (orientation)
With pack + CodeGraph: codegraph node learning_store_path + store_learn_record
Files read:          0 full files (verbatim symbol source returned inline)
Grep/find avoided:   broad read of server.py (5,524 lines) to find brain_* wrappers
Tool calls avoided:  multi-file Read pass across learn_engine/obsidian_writer/server
Result:              68 lines vs 6,922-line broad baseline (~99% fewer)
```

| Context path | First-read lines | What it yields |
| --- | ---: | --- |
| Context pack only | 213 | Which repos/files/decisions — no call structure |
| Pack + CodeGraph (2 `codegraph node`) | 68 | Verbatim writer source + exact callers + a no-tests warning |
| Broad source-scan baseline | 6,922 | `learn_engine.py` + `obsidian_writer.py` + `server.py` read in full |

CodeGraph returned the writer path in **68 lines vs 6,922** (~99% fewer) and
surfaced edges grep cannot — `learning_store_path` is `Called by ← record_learning,
load_learnings`; `store_learn_record` `Calls → validate_learn_record, make_learning,
record_learning` — plus a `⚠️ no covering tests found` blast-radius flag on the
writer-path symbol, exactly the safety signal you want before moving a write path.

This confirms the cross-repo payoff: the pack still does orientation (which repos,
which files, the `memory/reviews/` vs `memory/learn/` decision), and CodeGraph
collapses the source-discovery step from thousands of lines to tens.

## Delivery D — structured measurement records

Phase 4.5's narrative measurements above are now also captured as structured
`codegraph-measurement.v1` records (`schemas/codegraph-measurement.v1.json`,
`templates/codegraph-measurement.md`), so a measurement is queryable and its
correctness claim is machine-checked. `examples/codegraph-measurement.example.json`
holds three reproducible MQ measurements:

| Task | Type | CodeGraph | Baseline | Verification |
| --- | --- | ---: | ---: | --- |
| trace `render_pack` | python | 66 lines | 321 lines (full file) | `python3 -m unittest discover -s tests` → pass |
| trace `export_repo_review` (repo-review.v1) | cross-repo-contract | 35 lines | 103 lines (full file) | `pytest tests/test_review_export.py` → pass |
| find shell `log` helper | unsupported-shell | 0 (miss) | grep fallback | n/a — no correctness asserted |

The third record is the honest fallback case: `codegraph query log` in
`macos-scripts` returned only unrelated Python symbols while the shell `log()`
helper lives in 53 unindexed shell files, so the measurement records the CodeGraph
miss and a grep fallback rather than a fabricated reduction.

Two rules the records encode (per `decisions/ADR-009-codegraph-memory-boundary.md`):
measured facts stay separate from inferred savings, and a record may claim
correctness only when its source tests pass (enforced by `validate-export.py`).
These are measurement records only — CodeGraph output does not feed the
observation → scoring → curated-learn pipeline.

The `mq-agent` measurement command is deferred until this record contract has
settled in use (roadmap Delivery D).

## Next action

Continue Phase 2 by tightening card content from verified repo boundaries, then
rerun:

```bash
python3 scripts/measure-context-effect.py --format markdown
python3 scripts/check-token-budget.py
python3 scripts/validate-export.py
```
