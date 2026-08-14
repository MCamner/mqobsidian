# mqobsidian Roadmap

`mqobsidian` is the MQ stack durable memory and context-compression layer.

It stores reviewed knowledge, public-safe examples, portable schemas,
templates, compact context cards, and stack-truth notes. It does not execute
workflows or own live runtime truth.

## Current Status

Current version:

```text
0.3.0 - Explicit Truth Contracts and Consumer Readiness
```

`v0.3.0` is a release candidate: the truth/memory contract implementation and
the local release metadata are complete, and no implementation work is open.
Tagging and publishing remain explicit release actions gated on green CI.

## Completed Foundation

- Public-safe memory repo structure.
- Truth, review, learn, and decision export schemas.
- Reusable note and export templates.
- Sanitized examples.
- Context-pack schema, template, and generator with structured exclusion proof.
- Token budget checks.
- Seeded system hot/index notes for agent read-order.
- 23 owned contracts declared explicitly in `.mq/repo-contract.json`, each
  backed by a `schemas/<name>.v1.json` file.
- `release-check.sh` — read-only releasability entrypoint emitting
  `repo_release_check.v1`, so `mq-agent` can read this repo's release verdict.
- Atomic promotion transitions with a write-ahead journal and deterministic
  recovery, exposed as bounded local-only commands.

## Token Reduction — Measured

The context-pack path is no longer a proposal. Measured in
`docs/context-effect.md` for a real MQ task:

| Context path | Lines |
| --- | ---: |
| Context pack + available cards | 222 |
| Broad first-read baseline | 4797 |
| Reduction | 95.4% |

This proves the MVP path for one measured task. It does not promise the same
reduction for every future task.

## Next Focus

Tag and publish `v0.3.0`, then hold the line the contracts already draw:

- keep the published `docs/` surface consistent with the declared contracts
- accumulate verified routing outcomes per task class for a separate evidence
  review
- add memory categories only when a consumer need is declared

Explicit non-goals: do not fork the frozen promotion axis, do not rebuild the
consumer read contract or the public-safe guard, and do not move orchestration,
review execution, or terminal UX into this repo.

## Ownership Rule

```text
mqobsidian -> owns schemas, templates, examples, durable memory,
              scoring and promotion
mq-agent   -> selects and generates context packs; orchestrates ranking and
              promotion routing against mqobsidian contracts
mq-hal     -> shows operator status
mq-mcp     -> owns bounded runtime/review tools
```

See [Context Packs](Context-Packs) and [Memory Model](Memory-Model).
