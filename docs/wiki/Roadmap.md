# mqobsidian Roadmap

`mqobsidian` is the MQ stack durable memory and context-compression layer.

It stores reviewed knowledge, public-safe examples, portable schemas,
templates, compact context cards, and stack-truth notes. It does not execute
workflows or own live runtime truth.

## Current Status

Current public release:

```text
v0.2.1 - context-card seeds and agent read-order grounding
```

Current product direction:

```text
v0.2.x - Token Reduction MVP
```

## Completed Foundation

- Public-safe memory repo structure.
- Truth, review, learn, and decision export schemas.
- Reusable note and export templates.
- Sanitized examples.
- Context-pack schema and template.
- Token budget checks.
- Seeded system hot/index notes for agent read-order.

## Next Focus

Prove that a small task context pack reduces repeated Codex and Claude Code
context reads for one real MQ task.

Target flow:

```text
mqobsidian memory/context
  -> context-pack.v1
  -> .mq/context/task-pack.md
  -> Codex / Claude Code reads only the pack
```

## Ownership Rule

```text
mqobsidian -> stores schemas, templates, examples and durable memory
mq-agent   -> selects and generates context packs
mq-hal     -> shows operator status
mq-mcp     -> owns bounded runtime/review tools
```

See also [Context Packs](Context-Packs).
