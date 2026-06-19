# Integration Map: mq-hal

## Reads From

* mq-agent stack and release outputs
* repo-signal readiness signals
* local mq-hal config and allowlist
* MQ repo metadata when commands target a repo

## Writes To

* operator-facing terminal output
* local HAL logs or status files
* command routing decisions
* no durable MQ memory by default

## Use When

* task involves operator UX or HAL command routing
* task involves `mqlaunch hal`
* task needs the observe/recommend/coordinate boundary
* task checks that models cannot execute shell directly

## Avoid Reading First

* old release notes
* full dashboard design history
* unrelated source-repo docs
* raw model transcripts
