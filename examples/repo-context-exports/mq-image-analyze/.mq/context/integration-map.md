# Integration Map: mq-image-analyze

## Reads From

* screenshots and visual artifacts
* local or cloud vision model outputs
* schema and validation inputs
* mq-agent or mq-mcp requests for visual context

## Writes To

* structured perception results
* visual analysis reports
* validated JSON context
* no source-repo changes by default

## Use When

* task involves screenshots, diagrams, or UI states
* task needs visual context for mq-agent or mq-mcp
* task must preserve the analyze-only boundary
* task compares local and cloud vision modes

## Avoid Reading First

* unrelated release notes
* non-visual repo docs
* raw images with sensitive content
* full MQ-stack architecture docs
