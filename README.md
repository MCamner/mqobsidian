# mqobsidian

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
scripts/    validation and sensitive-content checks
```

## Current focus

The first public-safe scope is:

* explain the memory model
* define portable schemas
* provide sanitized examples
* document how MQ repos export into the memory layer

## Integration surfaces

See:

* [docs/architecture.md](docs/architecture.md)
* [docs/memory-model.md](docs/memory-model.md)
* [docs/truth-export.md](docs/truth-export.md)
* [docs/mq-agent-integration.md](docs/mq-agent-integration.md)
* [docs/mq-mcp-integration.md](docs/mq-mcp-integration.md)
* [docs/repo-signal-integration.md](docs/repo-signal-integration.md)
* [docs/mq-ums-integration.md](docs/mq-ums-integration.md)

## Validation

Run the public-safe checks with:

```bash
python3 scripts/validate-export.py
python3 scripts/check-sensitive-content.py
```

## License

Apache-2.0
