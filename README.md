# mqobsidian

[![Public Safe Check](https://github.com/MCamner/mqobsidian/actions/workflows/public-safe-check.yml/badge.svg)](https://github.com/MCamner/mqobsidian/actions/workflows/public-safe-check.yml)
[![Version](https://img.shields.io/badge/version-0.2.1-blue)](CHANGELOG.md)

Durable MQ-stack memory and context compression for Codex and Claude Code.

`mqobsidian` stores reviewed architecture memory, truth exports, decisions,
learn records, schemas, templates, and compact context surfaces. It is the
memory layer, not the runtime or orchestrator.

## Read Order

For agent work, start small:

1. `.mq/context/task-pack.md`
2. `memory/learn/agent/mqobsidian.md`
3. `systems/mqobsidian/hot.md`
4. `systems/mqobsidian/index.md`
5. relevant context cards or docs only when the pack is insufficient

## Quick Start

```bash
python3 scripts/generate-context-pack.py \
  --task "fix mq-mcp brain writer paths" \
  --repo mq-mcp \
  --target codex \
  --out .mq/context/task-pack.md
python3 scripts/check-token-budget.py
python3 scripts/measure-context-effect.py
python3 scripts/generate-agents-md.py --all --output-dir examples/generated-agent-entrypoints
python3 scripts/generate-claude-md.py --all --output-dir examples/generated-agent-entrypoints
python3 scripts/generate-repo-context-export.py --all --clean
```

## Stack Role

```text
signal -> review -> decision -> memory -> next action
```

* `mq-agent` orchestrates workflows and context export.
* `mq-mcp` executes bounded tools and owns runtime contracts.
* `repo-signal` scores repo health and readiness.
* `mq-hal` presents operator-facing summaries.
* `mqobsidian` stores durable, public-safe memory.

## What This Repo Owns

* memory schemas and note templates
* public-safe examples and exports
* context-pack and context-card contracts
* token-budget checks for agent-readable surfaces
* compact agent views such as `hot.md`, `index.md`, and context cards

## What This Repo Does Not Own

* live runtime truth
* workflow orchestration
* MCP tool execution
* repo scoring internals
* source-repo tests, CLI behavior, or release state

## Context Compression

The token-reduction path is:

```text
task -> memory query -> context-pack.v1 -> Codex / Claude Code
```

Current measured effect:

```text
context pack + cards: 213 lines
broad first-read baseline: 4114 lines
reduction: 94.8%
```

See [docs/context-effect.md](docs/context-effect.md).

## Public-Safe Rules

Safe to publish:

* architecture notes
* ADRs and decisions
* schemas and templates
* sanitized reviews, examples, and truth exports

Do not publish:

* secrets, tokens, or API keys
* customer names or internal hostnames
* IP addresses or raw enterprise logs
* machine-specific private paths
* unsanitized review output

## Important Docs

* [docs/memory-model.md](docs/memory-model.md) — memory layers and ownership
* [docs/truth-export.md](docs/truth-export.md) — export requirements
* [docs/context-budget.md](docs/context-budget.md) — line budgets
* [docs/context-export-contract.md](docs/context-export-contract.md) — context-export ownership and budget source
* [docs/context-effect.md](docs/context-effect.md) — measured reduction
* [docs/roadmap-token-reduction.md](docs/roadmap-token-reduction.md) — longer roadmap
* [schemas/context-pack.v1.json](schemas/context-pack.v1.json) — task-pack schema
* [templates/context-pack.md](templates/context-pack.md) — task-pack template

## Validation

```bash
python3 scripts/validate-export.py
python3 scripts/check-sensitive-content.py
python3 scripts/check-token-budget.py
python3 scripts/measure-context-effect.py
```

## License

Apache-2.0
