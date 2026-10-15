# Bridge security review and E2E evidence boundary — 2026-10-16

## Verified evidence

- mq-stack status reached 8/8 VERIFIED and 35/35 required CI scopes on the operator's exact local HEADs (October 2026 snapshot). This measures CI, not all runtime behavior.
- After an actual machine restart, launchd user jobs for MCP 8765 and image MCP 8766 were observed running and listening; live MCP compatibility returned PASS.
- An actual local `risk_review_repo(mode="security", receipt=False)` invocation successfully reviewed five Python files. Two reported no security findings; `bridge.py` produced six warnings and nine notes. This confirms the AI review path executes, **not** that its findings are proven vulnerabilities.
- The operator observed missing contextual artifacts: `Context status unavailable; reason artifact-missing` for two files. No root cause has been established.
- The concrete code issue was unfiltered `os.environ.copy()` passed to a stdio MCP subprocess and a globally set shell-exec flag in `--do` mode. A scoped allowlist and non-global child flag were proposed in mq-mcp PR [#107](https://github.com/MCamner/mq-mcp/pull/107); this note does **not** assert that PR is merged or locally installed.

## Findings requiring separate validation

- Model/tool output prompt-injection boundary.
- Asset-directory and image-path trust boundary.
- Terminal escape/ANSI handling for model output.
- Cause and effect of `artifact-missing` contextual provenance.
- Full observation → candidate → durable memory → retrieval E2E is **not yet verified**.

## Commands and evidence handling

```bash
mqlaunch stack status --json
mqlaunch auth status
mqlaunch auth test openai
lsof -nP -iTCP:8765 -sTCP:LISTEN
lsof -nP -iTCP:8766 -sTCP:LISTEN
```

For a repository risk review, invoke the registered MCP `risk_review_repo` tool only on an authorized allowlisted test repository. It may send selected file contents to an AI API and write review history even with `receipt=False`; do not treat it as side-effect-free. Record sanitized observations before promotion and use the established mq-agent/mqobsidian review pipeline. Never promote AI findings automatically. Do not claim memory E2E PASS without observing successful retrieval of the same artifact.
