# mqobsidian

[![Public Safe Check](https://github.com/MCamner/mqobsidian/actions/workflows/public-safe-check.yml/badge.svg)](https://github.com/MCamner/mqobsidian/actions/workflows/public-safe-check.yml)
[![Version](https://img.shields.io/badge/version-0.2.1-blue)](CHANGELOG.md)

Durable memory layer for the MQ stack.

`mqobsidian` stores reviewed, reusable, agent-readable knowledge. It is optimized
to reduce token usage through better read order, smaller context surfaces, and
clearer truth boundaries.

It is **not**:

- the execution runtime
- the orchestration engine
- the source of live code truth
- the place to dump raw logs by default

## What this repo is for

Use `mqobsidian` to:

- store durable memory from verified work
- keep compact context surfaces for agents
- reduce repeated broad scans of repo docs
- separate memory from live runtime truth
- define schemas, templates, and context rules for the stack

Use source repos and tools for current code behavior, current tests, current CLI
behavior, live review execution, and contracts in motion.

## Read order

When the task touches MQ memory, context, or prior stack work, read the smallest
useful surface first and stop once the task is grounded:

1. `.mq/context/task-pack.md`
2. `memory/learn/agent/mqobsidian.md`
3. `systems/mqobsidian/hot.md`
4. `systems/mqobsidian/index.md`
5. relevant context cards or docs only when the pack is insufficient

The full reading and truth-boundary rules live in
[docs/CONTEXT_CONTRACT.md](docs/CONTEXT_CONTRACT.md).

## Truth boundary

`mqobsidian` stores durable memory. It does not replace live truth from
`mq-agent`, `mq-mcp`, `mq-hal`, `repo-signal`, `mq-ums`, or `mq-image-analyze`.
If the task depends on current runtime state, file behavior, tests, or review
execution, verify in the source repo or tool.

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

## Context Compression

The token-reduction path is:

```text
task -> memory query -> context-pack.v1 -> Codex / Claude Code
```

Current measured effect:

```text
context pack + cards: 222 lines
broad first-read baseline: 4797 lines
reduction: 95.4%
```

See [docs/context-effect.md](docs/context-effect.md).

## Public-Safe Rules

Safe to publish: architecture notes, ADRs and decisions, schemas and templates,
sanitized reviews, examples, and truth exports.

Do not publish: secrets, tokens, or API keys; customer names or internal
hostnames; IP addresses or raw enterprise logs; machine-specific private paths;
unsanitized review output.

## Key docs

- [docs/CONTEXT_CONTRACT.md](docs/CONTEXT_CONTRACT.md) — how agents should read and use mqobsidian
- [docs/TOKEN_BUDGET.md](docs/TOKEN_BUDGET.md) — size limits for agent-readable context surfaces
- [docs/CONTEXT_CARDS.md](docs/CONTEXT_CARDS.md) — small reusable context-card model
- [docs/context-export-contract.md](docs/context-export-contract.md) — `.mq/context` export ownership and budget source
- [docs/memory-model.md](docs/memory-model.md) — durable memory layers and ownership
- [docs/truth-export.md](docs/truth-export.md) — export and truth-boundary rules
- [docs/roadmap-token-reduction.md](docs/roadmap-token-reduction.md) — longer roadmap
- [schemas/context-pack.v1.json](schemas/context-pack.v1.json) — task-pack schema
- [templates/context-pack.md](templates/context-pack.md) — task-pack template

## Validation

```bash
python3 scripts/validate-export.py
python3 scripts/check-sensitive-content.py
python3 scripts/check-token-budget.py
python3 scripts/measure-context-effect.py
```

## Design rule

The value of `mqobsidian` is not more memory. The value is better selection.
Agents should read the smallest useful surface first.

## License

Apache-2.0
