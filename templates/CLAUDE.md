<!--
Generated from mqobsidian agent-entrypoint templates for <REPO_NAME>.
Do not hand-edit this file directly; edit the mqobsidian templates and regenerate.

Ownership model:
- mqobsidian owns the contract, templates, schemas, and generators.
- this repo owns this committed agent surface once published.

Regenerate with:
  MQ_OBSIDIAN_DIR=<path-to-mqobsidian> \
    python3 "$MQ_OBSIDIAN_DIR"/scripts/generate-claude-md.py --repo <REPO_NAME> --out CLAUDE.md
-->

# CLAUDE.md

@AGENTS.md

## Claude Code Notes

Use generated context files before reading large docs.

For cross-repo work:

1. Read `.mq/context/task-pack.md` if it exists and matches the task.
2. Read `.mq/context/repo-card.md` if it exists.
3. Read `.mq/context/integration-map.md` if it exists.
4. Only then inspect source files.

Do not expand scope unless the task requires it.

Claude Code auto-loads skills from `.claude/skills/`; see **MQ Skills** in
AGENTS.md for routing.
