# Feedback loop (Phase 11c)

Phases 1–10 made packs *small*; Phase 11a/11b made them *right* at selection
time (explicit exclusions, block metadata). The feedback loop closes the cycle:
let **real usage** improve selection over time, **without ever publishing
local-rich material**.

`mqobsidian` owns the *vocabulary and policy* below. `mq-agent` owns the
*mechanism* — emitting signals during pack generation and acting on them. This
doc is the contract between the two; it does not move selection logic here.

## What we capture

One `feedback-signal.v1` record per pack-usage event
([`schemas/feedback-signal.v1.json`](../schemas/feedback-signal.v1.json),
worked shape in
[`examples/feedback-signal.example.json`](../examples/feedback-signal.example.json)):

| Field | Meaning |
| --- | --- |
| `task` | the task the pack was built for |
| `generated_at` | when the pack was used |
| `repo` | primary repo (optional) |
| `outcome` | `sufficient` / `insufficient` — did the pack carry the task |
| `judgments[]` | per-block verdicts: `{ block, judgment, reason? }` |

`judgment` is the core signal:

- `useful` — the block earned its place; **promotion** candidate.
- `noise` — selected but wasted tokens; **downgrade** candidate.
- `missing` — needed but not selected; promote into a card/template.
- `stale` — content was out of date; `freshness` downgrade signal.

These map directly onto the 11b metadata mq-agent already consumes
(`freshness` / `scope` / `publishability`), so the loop adjusts the same knobs
selection reads — it does not invent a parallel model.

## Where the signals live

Live records are appended to a **local-only, gitignored** surface: `feedback/`
(see [`.gitignore`](../.gitignore)). Records are machine-emitted by mq-agent,
not hand-authored — there is no template. Only the **schema** and a single
**sanitized example** are public; raw signal logs never enter git history.

## Promotion and downgrade

The loop turns accumulated judgments into *proposals*, never edits:

- **Promote** — a block repeatedly judged `useful` across tasks is a candidate
  to strengthen its card or lift detail into a template/example. A recurring
  `missing` is a candidate to create or widen a card.
- **Downgrade** — a block repeatedly judged `noise` is a candidate to demote in
  selection (or add as a `fallback`/`forbidden` exclusion for that task-type). A
  recurring `stale` is a candidate to flip the card's `freshness`.

Promotion and downgrade are **suggestions surfaced for review** (e.g. via the
existing inbox / research-triage flow), routed through the normal
template-based note-creation path. The loop proposes; a human or an explicit
command commits.

## Measuring selection quality

Accumulated judgments are also a **gold label set**, not only a source of
proposals. `scripts/eval-retrieval.py` reads the same records and reports whether
selection picked the *right* blocks:

```bash
python3 scripts/eval-retrieval.py --format markdown
python3 scripts/eval-retrieval.py --repo mq-mcp
```

The mapping onto the retrieval confusion matrix is exactly the vocabulary above:

| Judgment | Meaning for scoring |
| --- | --- |
| `useful` | true positive — selected and earned its place |
| `noise` | false positive — selected and wasted tokens |
| `missing` | false negative — needed but not selected |
| `stale` | **not** a relevance signal; reported as its own `stale_rate` |

So `precision = useful / (useful + noise)` and
`recall = useful / (useful + missing)`. `stale` stays out of both because it is a
freshness verdict on a correctly selected block, and this repo keeps the
freshness and relevance axes separate on purpose.

Rank metrics (Recall@K, MRR) are **not** reported. `feedback-signal.v1` records
judgments as an unordered set with no rank field; a rank number derived from list
order would measure serialization, not retrieval.

This complements [`context-effect.md`](context-effect.md), which measures how
*small* a pack is. A pack can be 96% smaller and still wrong — reduction and
quality are different questions, and only the pair is meaningful.

The per-block verdicts (`keep` / `downgrade` / `widen-or-create` / `refresh`)
restate the promotion and downgrade rules above; they remain proposals for
review, and a block with fewer than three judgments is reported as
`insufficient-data` rather than acted on.

## No-publish guarantee

The loop must never auto-publish:

1. Signal data is gitignored (`feedback/`) and is never force-added.
2. Promotion/downgrade produce proposals, not commits — no step writes a
   tracked file unattended.
3. Anything that would cross the publish boundary (a `local-rich` /
   `local-only` block, per [`docs/CONTEXT_CARDS.md`](CONTEXT_CARDS.md)) is
   excluded from any public artifact the loop suggests, exactly as selection
   already enforces.

This is recorded as a local decision in
`decisions/ADR-007-feedback-loop-no-auto-publish.md`.

## Ownership boundary

| Concern | Owner |
| --- | --- |
| Signal vocabulary, surface convention, promotion/downgrade policy, no-publish guarantee | **mqobsidian** (this) |
| Emitting signals during pack generation; computing and surfacing proposals | **mq-agent** |

mq-agent reads this contract and produces/consumes the records; it does not
define the schema or relocate the policy into runtime.
