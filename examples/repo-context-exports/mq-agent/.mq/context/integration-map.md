# Integration Map: mq-agent

## Reads From

* mqobsidian durable memory
* mq-mcp tool surface
* repo-signal repo assessments
* MQ source repos for live code truth

## Writes To

* `.mq/context/`
* `memory/learn/agent/*.md`
* stack truth exports
* operator-facing command output

## Use When

* task involves orchestration or stack gates
* task involves memory query or context export
* task involves agent-view rebuild or drift checks
* task involves safe execution through `mq-agent`

## Avoid Reading First

* old release notes
* unrelated dashboard docs
* archived experiment notes
* full repo README files
