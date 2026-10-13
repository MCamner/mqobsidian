# Measured execution completeness

`mq.execution-outcome.v1` optionally carries executor coverage in `completeness`.
mqobsidian owns this schema; runtime producers own measurement and aggregation.
The addition preserves all historical records. Absence means unmeasured and
must never be interpreted as complete. Older closed-schema readers reject the
new field until they vendor the updated canonical schema.

Each step has its original positive `step` index and a measured `status`:

| Status | Meaning |
| --- | --- |
| `complete` | Step succeeded and every declared fan-out item executed |
| `partial` | Declared fan-out did not finish |
| `failed` | Executor reported a failed step |
| `skipped` | Executor skipped the step |
| `not-executed` | Step remained pending or running when coverage was assessed |
| `unmeasured` | Fan-out completion could not be established |

For fan-out, `source_item_count` and `executed_call_count` are emitted together
only when both were measured. Producers must check equal counts and the executor
completion flag before claiming `complete`. The JSON schema validates types and
paired presence; it cannot compare two arbitrary integer properties for equality.
Per-step records carry no file paths, prompts, quotations or raw material.

Aggregate `complete` requires a nonempty plan consisting entirely of complete
steps. Aggregate `partial` requires an incomplete step or an empty plan. It
requires execution `result: FAIL` and `exit_status: error` or `aborted`. A complete
execution may still fail verification: completeness establishes coverage, not
correctness. Neither route verification nor an LLM may override these facts.

Example of a partial execution measurement, not a production observation:

```json
{
  "status": "partial",
  "steps": [
    {
      "step": 1,
      "status": "partial",
      "source_item_count": 91,
      "executed_call_count": 25
    }
  ]
}
```

An applied route can remain a real routing observation during a partial
execution. Routing history must be preserved. A quality comparison claiming
complete audit quality must independently resolve the exact linked execution
and require measured complete coverage and a successful result. Readiness is
neither that quality judgment nor permission to enable automatic routing.

The runtime quality era opens only after the consumer fix merges, using its
actual merge identity and timestamp. A schema-only merge does not change what
the producer emitted and cannot establish that era.
