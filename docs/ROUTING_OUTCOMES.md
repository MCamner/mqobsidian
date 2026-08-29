# Verified routing outcomes

`mqobsidian` stores contract-validated model-routing evidence as local,
append-only JSONL.
It does not classify tasks, run models, approve candidates, or calculate routing
policy. Those responsibilities remain in `mq-agent`.

## Contract boundary

- Producer and schema owner: `mq-agent`
- Authoritative schema: `schemas/model_route_outcome.schema.json` in `mq-agent`
- Durable local surface: `routing/outcomes.jsonl` in `mqobsidian`
- **The surface is not filled automatically.** `mq-agent` writes its own
  outcomes to `~/.mq-agent/route-outcomes.jsonl` (or `MQ_AGENT_ROUTE_OUTCOMES`).
  Nothing copies them here — the write gate below must be run. A vault with
  no `routing/` directory means the transfer has never happened, not that no
  routing has occurred.
- Consumer: `mq-agent route report`
- Public surface: this contract document and one sanitized example only

The durable file is gitignored. Each line remains an exact
`mq.model-route-outcome.v1` object so the mq-agent report command can consume it
without a second schema or translation layer.

## Write gate

`scripts/record-routing-outcome.py` accepts a record only when:

- it validates against mq-agent's authoritative schema;
- a `PASS` record names deterministic checks, is schema-valid, and is not escalated;
- a `FAIL`, `SKIPPED`, or `UNAVAILABLE` record preserves its escalation and is
  never marked accepted;
- no obvious credential or machine-specific path is present.

Unknown fields are rejected by the authoritative schema. This prevents raw model
output or a candidate payload from entering durable history. Negative outcomes
are retained because evidence review must prove malformed-output escalation and
the Ollama-unavailable path, not only count successful candidates. Only `PASS`
counts as verified success in `mq-agent route report`; acceptance remains a
separate signal.

## Record one outcome

Pass only the `outcome` object from shadow mode:

```bash
mq-agent route shadow "Review README documentation" --json |
  jq '.outcome' |
  python3 scripts/record-routing-outcome.py
```

Preview validation without writing:

```bash
python3 scripts/record-routing-outcome.py \
  examples/model-route-outcome.example.json \
  --dry-run
```

The writer validates against the canonical contract in this repo,
`schemas/mq.model-route-outcome.v1.json`. mq-agent vendors that file and a gate
there proves its copy matches (mq-agent #216), so validation no longer depends
on a sibling mq-agent checkout. `MQ_AGENT_ROUTE_OUTCOME_SCHEMA`, `--schema` and
`--output` exist for tests and explicit local overrides.

Identical retries are idempotent. A malformed existing JSONL line blocks future
appends instead of silently extending corrupt history.

## Read the durable evidence

Point mq-agent's read-only report at the vault-owned file:

```bash
MQ_AGENT_ROUTE_OUTCOMES="$MQ_OBSIDIAN_DIR/routing/outcomes.jsonl" \
  mq-agent route report --json
```

To transfer outcomes mq-agent has already recorded locally:

```bash
while IFS= read -r line; do
  echo "$line" | python3 scripts/record-routing-outcome.py
done < ~/.mq-agent/route-outcomes.jsonl
```

Identical records are idempotent, so re-running is safe.

Reports must continue to distinguish attempted, schema-valid, verified,
agent-accepted, operator-accepted, and escalated outcomes. Stored evidence does
not enable automatic routing; promotion still requires the separate evidence
gate and explicit operator approval.
