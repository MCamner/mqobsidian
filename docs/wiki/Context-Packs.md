# Context Packs

Context packs are small, task-scoped bundles for Codex and Claude Code.

The goal is to replace broad reads of full READMEs, old release notes, large
vault notes, or unrelated repo history with focused context.

## Target Flow

```text
task
  -> memory query
  -> context-pack.v1
  -> Codex / Claude Code reads only the pack
```

## Current MVP Command

```bash
python3 scripts/generate-context-pack.py \
  --task "fix mq-mcp brain writer paths" \
  --repo mq-mcp \
  --target codex \
  --out .mq/context/task-pack.md
```

## Budget Rule

Generated context should stay small. The current budget check is:

```bash
python3 scripts/check-token-budget.py
```

## Ownership

- `mqobsidian` owns schemas, templates, examples, and durable memory.
- `mq-agent` should own context selection, generation, and export.
- Target MQ repos should keep `AGENTS.md` and `CLAUDE.md` thin.

## Related Repository Files

- `schemas/context-pack.v1.json`
- `templates/context-pack.md`
- `examples/sanitized-context-pack.md`
- `docs/context-budget.md`
- `docs/roadmap-token-reduction.md`
