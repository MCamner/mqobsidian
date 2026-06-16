# mq-mcp Integration

`mq-mcp` is the execution and validation runtime in the MQ stack.

## Relationship

It is the natural source for:

* review outputs
* learn exports
* architecture decisions
* runtime truth summaries

## Rule

`mq-mcp` remains the source of truth for contracts, safety classes, and runtime
behavior. `mqobsidian` stores durable, sanitized memory derived from those
outputs.
