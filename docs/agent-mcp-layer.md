---
type: index
title: Agent & MCP layer — how Claude and Codex use this vault
status: active
tags: [docs, agent, mcp, skills, process]
updated: 2026-06-16
links_to: [../AGENTS.md, ../CLAUDE.md, ../decisions/ADR-002-note-creation-and-ingest]
---

# Agent & MCP layer

How Claude Code and Codex are wired to this vault and the MQ stack. The vault is the **knowledge layer**; behavior lives in skills; live operations live in MCP.

## Layers

| Layer | Lives in | Notes |
| --- | --- | --- |
| Stored knowledge | `systems/`, `summaries/`, `learn/`, `research/`, `templates/` | The vault itself |
| Project rules | `AGENTS.md` (Codex), `CLAUDE.md` (Claude) | Read order, output rules, failure rule |
| Reusable method | `.codex/skills/` and `.agents/skills/` (Codex), `.claude/skills/` (Claude) | **Generated** — see below |
| Live operation | MCP server `mq-mcp` | `.mcp.json` (Claude), `.codex/config.toml` (Codex) |

## Skills — single source, two targets

Edit the **source**, never the built copies:

```text
skills-src/<name>/SKILL.md      ← edit here
        │  tools/build-skills.sh
        ▼
.claude/skills/<name>/SKILL.md   (Claude)
.codex/skills/<name>/SKILL.md    (Codex project-local)
.agents/skills/<name>/SKILL.md   (legacy Codex compatibility)
```

Run after any change:

```bash
./tools/build-skills.sh
```

The build wipes and regenerates all generated skill trees, so renamed/removed skills do not linger.

### Current skills

- `mq-analysis` — entry/router for raw MQ material; decides summary vs research node, then hands off.
- `mq-summary` — structured summary from raw/log input via `templates/summary-template.md`.
- `mq-research-triage` — capture weak-evidence questions as a research node.
- `mq-hot-refresh` — compress a system's state into `hot.md` (≤500 words).
- `mq-index-refresh` — sync a system's `index.md` to verified reality.
- `mq-roadmap-update` — update the roadmap to reflect what actually shipped.

## MCP — only mq-mcp is a real server

- **mq-mcp** ✅ wired in `.mcp.json` and `.codex/config.toml` with the real command:
  `uv --directory /Users/mansys/mq-mcp/mq-mcp run mcp run server.py`
- **repo-signal** — a CLI, not an MCP server. Its functions are already exposed through mq-mcp (`repo_signal_*` tools). Kept as a disabled placeholder.
- **mqobsidian** — no MCP server exists (the vault is plain Markdown). Disabled placeholder.

`tools/mcp/start-*.sh` are generic launcher bridges; they read a `*_START_CMD` env var. Only mq-mcp has one set.

## Verify loading (run in the vault repo)

- Claude: `What project instructions, skills, and MCP tools are active for this repo?`
- Codex: `Summarize the loaded instructions and list the MQ skills available.`

## Related

- [[../decisions/ADR-002-note-creation-and-ingest]] — note-creation + ingest rules
- [[../skills/index]] — skill catalog
- [[../templates/README]] — template pack design
