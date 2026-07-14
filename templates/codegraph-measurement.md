# Template: codegraph-measurement.v1

Canonical shape for a CodeGraph discovery measurement (Roadmap: CodeGraph MQ
Integration → Delivery D). Records are JSON validated against
`schemas/codegraph-measurement.v1.json`; this template documents the record shape
and the rules. See `examples/codegraph-measurement.example.json` for three
complete public-safe records and `docs/context-effect.md` for the narrative
measurements.

## Record skeleton

```json
{
  "task": "<short task description>",
  "task_type": "python | cross-repo-contract | unsupported-shell",
  "repos": ["<repo basename>"],
  "queries": ["<codegraph or fallback command actually run>"],
  "returned_symbols": ["<symbol CodeGraph returned>"],
  "measured": {
    "codegraph_lines": 0,
    "baseline_lines": 0,
    "source_reads": 0
  },
  "baseline": { "description": "<the defined broad-read baseline>" },
  "inferred": {
    "reduction_pct": 0.0,
    "note": "<why this is inferred, not measured>"
  },
  "verification": {
    "selected_tests": ["<test path>"],
    "executed_tests": ["<test path>"],
    "command": "<command that runs the tests>",
    "result": "pass | fail | not-run"
  },
  "fallback": { "used": false, "reason": "" },
  "correctness_claimed": false
}
```

## Rules

- **Measured vs inferred.** `measured` holds only counted facts (lines, reads).
  Any token/line saving is `inferred` and lives in its own block — never present a
  computed percentage as a measured fact.
- **Defined baseline.** `baseline.description` states the broad-read baseline the
  CodeGraph path is compared against, so the comparison is reproducible.
- **Correctness needs tests.** `correctness_claimed` may be `true` only when
  `verification.result` is `pass`. `validate-export.py` enforces this. A
  discovery-only or fallback measurement sets `correctness_claimed: false`.
- **Not evidence.** Per `decisions/ADR-009-codegraph-memory-boundary.md`, these
  records are measurement only. CodeGraph output does not feed the
  observation → scoring → curated-learn pipeline.
- **Unsupported surfaces.** For a shell/PowerShell task, record the CodeGraph miss
  honestly and set `fallback.used: true` with a reason — do not fabricate a
  reduction where CodeGraph cannot index the source.
- **Public-safe.** Repo basenames, repo-relative paths, and symbol names only — no
  absolute machine paths, no secrets.
