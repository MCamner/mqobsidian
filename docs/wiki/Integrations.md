# Integrations

`mqobsidian` is a memory layer in the MQ stack.

## Stack Boundary

```text
mqlaunch    -> starts commands and menus
mq-agent    -> orchestrates workflows and exports truth
mq-mcp      -> bounded runtime and review tools
repo-signal -> repo health and readiness
mq-hal      -> operator-facing summaries
mqobsidian  -> durable memory and compact context
```

## mq-agent

`mq-agent` should export high-value, durable state into `mqobsidian`, such as:

- stack summaries
- release readiness snapshots
- reviewed action outcomes
- dashboard-ready truth summaries

## mq-mcp

`mq-mcp` provides bounded review, learn, and brain tools. `mqobsidian` stores only
sanitized durable summaries, not raw runtime output.

Current brain-facing tools:

| Tool | Class | Effect |
| --- | --- | --- |
| `brain_status` | read-only | Reports vault availability, top-level folders, and per-folder note counts. |
| `brain_record_decision` | write (approval) | Writes an architecture decision record to `decisions/`. |
| `brain_record_review` | write (approval) | Writes a sanitized code review summary to `reviews/`. |
| `brain_record_session` | write (approval) | Writes a session note to `sessions/`. |
| `brain_record_learning` | write (approval) | Writes a learned engineering pattern to `learn/`; updates in place rather than duplicating. |
| `brain_promote_learning` | write (approval) | Validates required frontmatter and body sections, then promotes `learn/<slug>.md` into `learn/verified/`. |

Every write tool requires user approval and targets the local vault. `mq-mcp`
never writes to the tracked repository surface.

### Scoring and promotion are not mq-mcp tools

`mq-mcp` does not score observations or emit promotion events. `mqobsidian` owns
the memory and promotion record contracts — including `memory-score.v1` and
`promotion-event.v1` — and applies them through a local-only memory CLI that is
not part of the published repository surface. `mq-agent` orchestrates ranking and
promotion routing against those contracts but does not own them.

See `docs/TRUTH_SURFACES.md` for the truth-surface boundary and where the
per-contract ownership table is defined.

## repo-signal

`repo-signal` can provide readiness, docs quality, and repo intelligence
signals. Memory export is opt-in and failure-isolated: when enabled, a real
`inspect` run maps its top issue to one `memory-observation.v1` record appended
to `memory/observations/repo-signal.observations.jsonl` in the vault. Exported
records should stay compact and public-safe.

An observation is a proposal, not a memory. Producing one does not promote it —
scoring and promotion stay with `mqobsidian`.

## mq-hal

`mq-hal` should show operator status and route next actions. It should not own
context-pack generation or write durable memory directly.
