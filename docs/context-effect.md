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
| Context pack + available cards | 213 |
| Broad first-read baseline | 4114 |
| Avoided first-read lines | 3901 |
| Reduction | 94.8% |

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

## Next action

Continue Phase 2 by tightening card content from verified repo boundaries, then
rerun:

```bash
python3 scripts/measure-context-effect.py --format markdown
python3 scripts/check-token-budget.py
python3 scripts/validate-export.py
```
