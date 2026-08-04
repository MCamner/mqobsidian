# Model Routing in Codex and Claude Code

Codex and Claude Code use the same `mq-mcp` server, routing tools, and
versioned contracts in VS Code. The local Ollama candidate is advisory; the
active coding agent remains authoritative.

## Codex example

For `Review the mq-hal route status implementation`:

1. Codex calls `mq_route_inspect` with the task.
2. For cross-repo evidence, Codex calls `mq_context_pack`.
3. Codex may call `mq_route_shadow`, but never treats its candidate as accepted.
4. Codex verifies findings against source and tests.
5. Codex escalates when the decision contains an escalation condition.

## Claude Code example

Claude Code follows the same sequence because `CLAUDE.md` imports `@AGENTS.md`:

1. Call `mq_route_inspect` before planning the non-trivial change.
2. Call `mq_context_pack` when the task crosses repository boundaries.
3. Use `mq_route_shadow` only as additional evidence.
4. Keep Claude authoritative for medium/high-risk work.
5. Verify against source and tests; escalate on the same reason codes.

## Boundaries

- Do not replace either agent's model backend.
- Do not intercept every editor prompt.
- Do not execute or persist a shadow candidate automatically.
- Do not implement separate routing policy for Codex and Claude.

The tools are documented by `mq-mcp`; routing policy and decision/outcome
contracts are owned by `mq-agent`.
