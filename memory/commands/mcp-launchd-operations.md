# MQ MCP launchd — safe operational commands

Status: confirmed running in the 2026-10-15 session; **post-login/reboot verification deferred**.

## Read-only checks (safe during other work)

```bash
launchctl print "gui/$(id -u)/se.mq.mcp" | grep -E 'state =|pid =|last exit code'
launchctl print "gui/$(id -u)/se.mq.image" | grep -E 'state =|pid =|last exit code'
lsof -nP -iTCP:8765 -sTCP:LISTEN
lsof -nP -iTCP:8766 -sTCP:LISTEN
```

```bash
cd "$HOME/mq-agent"
uv run mq-agent stack compatibility \
  --repo-path "mq-mcp=$HOME/mq-mcp-main" \
  --live
```

Expected: `Stack compatibility: PASS`, 4 relationship pairs agree, no MQC019/MQC023/MQC024 findings. If the server is missing, the CLI may still report static PASS: always inspect findings and process ownership.

## Diagnose failure without exposing secrets

```bash
tail -40 "$HOME/Library/Logs/MQ/mq-mcp-error.log"
tail -40 "$HOME/Library/Logs/MQ/mq-image-error.log"
```

```bash
mqlaunch auth status
```

Keychain may contain the API key even when `OPENAI_API_KEY` is absent from an interactive shell. Do not paste secrets or dump Keychain values to logs. The mq-mcp LaunchAgent reads the credential at startup; actual API acceptance requires a separate explicit test.

## Deferred service takeover or post-login validation

**Do not run these while other work is in progress.** Before any restart, check `launchctl print` and `lsof` and identify the port owners. If manual server instances occupy the ports, verify their command and parent process before terminating; never kill PIDs copied from a historical log.

```bash
launchctl kickstart -k "gui/$(id -u)/se.mq.mcp"
launchctl kickstart -k "gui/$(id -u)/se.mq.image"
```

After login/reboot, rerun all read-only checks and live compatibility. This step was explicitly deferred by the operator on 2026-10-15.

## Background configuration reference

- `se.mq.mcp`: local HTTP MCP transport, TCP 8765; Keychain-based OpenAI credential; correct mq-mcp main checkout.
- `se.mq.image`: image MCP HTTP transport, TCP 8766.
- Both: per-user launchd jobs with RunAtLoad and KeepAlive. Never commit secrets, raw Keychain data, machine identifiers, or absolute private home directories to public repository history.
