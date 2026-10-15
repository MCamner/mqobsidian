# MCP contracts and launchd handover — 2026-10-15

Status: verified for current session; login/reboot persistence **NOT YET VERIFIED**.

## Evidence and outcome

- `mq-agent` PR [#412](https://github.com/MCamner/mq-agent/pull/412) adds repeatable `stack compatibility --repo-path NAME=PATH` for parallel Git worktrees.
- `mq-mcp` PR [#105](https://github.com/MCamner/mq-mcp/pull/105) registers bounded `risk_review_repo` and updates the published tool surface to 139 tools.
- The operator ran a live compatibility check with the correct mq-mcp main checkout. Result: **PASS**, 4 of 4 relationships agree; no MQC019, MQC023 or MQC024 findings reported.
- Two macOS user LaunchAgents, `se.mq.mcp` and `se.mq.image`, were subsequently observed in `state = running` with their own PIDs.
- Initial launchd crash loops were **port conflicts**, not contract mismatches: old manually launched processes already held TCP 8765 and 8766. Transfer ownership from manual starts to launchd; never blindly start duplicates.
- `mq-mcp` defaults to MCP stdio transport if `MQ_MCP_TRANSPORT` is unset. The HTTP service requires explicitly setting `MQ_MCP_TRANSPORT=streamable-http` and `MQ_MCP_PORT=8765`.
- The OpenAI secret is managed in macOS Keychain. Do not write it to public memory, plist, repository files or logs. A successful compatibility check does **not** prove a live OpenAI API call succeeds.
- A `direnv` declaration may refer to a missing local `.env`; this is separate from Keychain-based authentication.

## Lessons

1. Verify both static contract agreement and live tool surface before closing MCP drift.
2. Preserve checkout selection: the older secondary worktree may not contain the new manifest.
3. Port ownership and process supervision must be inspected before enabling `KeepAlive`, or launchd will repeatedly collide with manual services.
4. `launchctl print` showing `running` proves supervision **now**, not after logout or system reboot.
5. Avoid treating a previous `last exit code = 143` as a current failure when the job is running; it commonly records a SIGTERM during handover.

## Deferred follow-up — do not interrupt current work

After the operator finishes other work, test logout/login or Mac reboot persistence; then reconfirm both LaunchAgents are running, their ports listen, and live compatibility remains PASS. No reboot or logout has been performed for this record. See [operations commands](../commands/mcp-launchd-operations.md).
