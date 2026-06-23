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
