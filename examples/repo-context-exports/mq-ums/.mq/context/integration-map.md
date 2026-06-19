# Integration Map: mq-ums

## Reads From

* UMS connection configuration
* PSIGEL command output
* local allowlist configuration
* mq-agent or mqlaunch operator requests

## Writes To

* local browser UI responses
* command history and audit outputs
* structured UMS summaries
* no MQ durable memory unless exported by another layer

## Use When

* task involves UMS device operations
* task involves PowerShell safety boundaries
* task touches browser operator workflows
* task needs to separate UMS UI from MQ orchestration

## Avoid Reading First

* unrelated MQ release notes
* old browser UI experiments
* raw enterprise logs
* full stack architecture docs
