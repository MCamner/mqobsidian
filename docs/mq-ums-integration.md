# mq-ums Integration

`mq-ums` is the enterprise endpoint-management use case in the MQ stack.

## Relationship

Its strongest long-term role in mqobsidian is as a source of endpoint truth:

* UMS read-only validation status
* endpoint readiness snapshots
* sanitized audit summaries

## Target direction

```text
mq-ums live validation
-> ums_status.v1
-> sanitized endpoint-truth.v1 export
-> mqobsidian memory
```

## Rule

mqobsidian should never store raw enterprise logs or unsanitized environment
details.
