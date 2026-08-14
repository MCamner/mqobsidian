# mq-mcp Integration

`mq-mcp` is the execution and validation runtime in the MQ stack.

## Relationship

It is the natural source for:

* review outputs
* learn exports
* architecture decisions
* runtime truth summaries

## Brain-facing tools

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

## Scoring and promotion are not mq-mcp tools

`mq-mcp` does not score observations or emit promotion events. `mqobsidian` owns
the memory and promotion record contracts — including `memory-score.v1` and
`promotion-event.v1` — and applies them through a local-only memory CLI. Any
document listing an `mq-mcp` tool that previews or applies memory scores is
wrong; no such tool exists.

## Rule

`mq-mcp` remains the source of truth for contracts, safety classes, and runtime
behavior. `mqobsidian` stores durable, sanitized memory derived from those
outputs.
