# mqobsidian

[![Public Safe Check](https://github.com/MCamner/mqobsidian/actions/workflows/public-safe-check.yml/badge.svg)](https://github.com/MCamner/mqobsidian/actions/workflows/public-safe-check.yml)
[![Version](https://img.shields.io/badge/version-0.2.1-blue)](CHANGELOG.md)

Architecture memory layer for MQ-stack truth exports, repo reviews, decisions,
learning records, and operational knowledge.

`mqobsidian` is the local-first knowledge layer in the MQ ecosystem. It stores
durable architectural context, reviewed findings, truth exports, sanitized
examples, and reusable note templates. It does not execute workflows, route
commands, or replace `mq-agent` or `mq-mcp`.

## Role

In the MQ stack:

```text
signal -> review -> decision -> memory -> next action
```

The responsibility split is:

* `mq-agent` orchestrates workflows
* `mq-mcp` executes bounded tools and owns runtime/review contracts
* `repo-signal` scores repo health and readiness
* `mq-hal` presents operator-facing summaries
* `mq-ums` provides enterprise endpoint signals
* `mqobsidian` keeps the durable memory layer

## Example memory flow

```text
mq-agent stack truth-export
  -> schemas/stack-truth.v1.json
  -> templates/stack-truth.md
  -> mqobsidian memory note
```

This repo defines the contracts and note formats used when MQ tools export
durable architecture memory.

## Example context flow

```text
user task
  -> mq-agent memory query
  -> select relevant notes
  -> context-pack.v1
  -> Codex or Claude reads only the task pack
```

The next layer for `mqobsidian` is context compression: short, durable context
packs that replace broad repo or vault reads when a task only needs a focused
slice of MQ knowledge.

## Token reduction layer

`mqobsidian` reduces repeated Codex and Claude Code context by turning durable
MQ-stack memory into small, task-specific context packs:

```text
task -> memory query -> context-pack.v1 -> Codex / Claude Code
```

Next milestone: `v0.2.0 — Token Reduction MVP`, not the whole roadmap at
once. Generate one useful pack for one real MQ task and prove the agent reads
less.

```bash
python3 scripts/generate-context-pack.py \
  --task "fix mq-mcp brain writer paths" \
  --repo mq-mcp \
  --target codex \
  --out .mq/context/task-pack.md
```

See [docs/roadmap-token-reduction.md](docs/roadmap-token-reduction.md).

For MQ repos where Codex or Claude Code should use this memory layer, add the
small reusable block from
[templates/agent-memory-block.md](templates/agent-memory-block.md) to
`AGENTS.md` and `CLAUDE.md`. Keep it additive: repo-specific build, test,
safety, and release rules still live in the target repo.

## What belongs here

Safe to publish:

* architecture notes
* ADRs and decision records
* truth-export schemas
* sanitized review examples
* integration docs
* reusable Markdown templates
* validation scripts for public-safe exports

Do not publish:

* customer names
* server names or internal hostnames
* IP addresses
* tokens or API keys
* real UMS, Citrix, or Intune logs
* unsanitized review output
* machine-specific private paths

## Repo layout

```text
docs/       architecture, memory model, and integration docs
schemas/    JSON contracts for truth, review, learn, and decision exports
templates/  reusable Markdown note/export templates
examples/   sanitized example exports
scripts/    validation, context-pack generation, and safety checks
```

## Current focus

Current public-safe scope:

* explain the memory model
* define portable schemas
* provide sanitized examples
* document how MQ repos export into the memory layer
* add context-pack scaffolding for lower-token AI workflows

## Integration surfaces

See:

* [docs/architecture.md](docs/architecture.md)
* [docs/memory-model.md](docs/memory-model.md)
* [docs/truth-export.md](docs/truth-export.md)
* [docs/context-budget.md](docs/context-budget.md)
* [docs/roadmap-token-reduction.md](docs/roadmap-token-reduction.md)
* [docs/mq-agent-integration.md](docs/mq-agent-integration.md)
* [docs/mq-mcp-integration.md](docs/mq-mcp-integration.md)
* [docs/repo-signal-integration.md](docs/repo-signal-integration.md)
* [docs/mq-ums-integration.md](docs/mq-ums-integration.md)

## Validation

Run the public-safe checks with:

```bash
python3 scripts/validate-export.py
python3 scripts/check-sensitive-content.py
python3 scripts/check-token-budget.py
```

## License

Apache-2.0
