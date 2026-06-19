# Integration Map: repo-signal

## Reads From

* target repo files
* repo configuration and metadata
* local project state
* readiness inputs requested by callers

## Writes To

* structured readiness signals
* `inspect.v1` outputs
* `doctor.v1` outputs
* `report.v1` outputs

## Use When

* task involves repo readiness or health scoring
* task needs structured inspection provenance
* task involves exporting repo signals into mqobsidian
* task needs to separate scoring from orchestration

## Avoid Reading First

* old release notes
* unrelated stack docs
* raw logs
* full repo README files
