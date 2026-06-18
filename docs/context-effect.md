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
| Broad first-read baseline | 4497 |
| Avoided first-read lines | 4284 |
| Reduction | 95.3% |

## Interpretation

The context layer is already giving practical effect for the first real MQ task.
Instead of reading broad README, changelog, roadmap, and docs surfaces across
three repos, an agent can start with one task pack and three compact context
cards.

This does not prove every future task will get the same reduction. It does prove
that the current MVP path is useful enough to continue Phase 2.

## Next action

Continue Phase 2 by adding context cards one repo at a time, then rerun:

```bash
python3 scripts/measure-context-effect.py --format markdown
python3 scripts/check-token-budget.py
python3 scripts/validate-export.py
```
