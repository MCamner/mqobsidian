# Agent-Entrypoint Lineage Policy

`mqobsidian` owns the `AGENTS.md` / `CLAUDE.md` template and generator surface.
This note is the durable policy for **which lineage each repo's entrypoints
follow** and **the one rule that must never be broken when regenerating them**.

Decision record: `ADR-005` (agent-entrypoint lineage, V1). Enforced by
[`scripts/agent_entrypoints.py`](../scripts/agent_entrypoints.py) and
[`scripts/check-agent-entrypoints.py`](../scripts/check-agent-entrypoints.py)
(wired into `public-safe-check` CI).

## One template, one lineage

There is a single canonical lineage: **`superset-v1`**. The earlier split between
a *thin* template (Read First / Rules / Durable Memory / Source Intelligence / MQ
Skills) and a *rich* template (which additionally carried mqobsidian Location,
full Read Order, Low-Token Rules, the secrets-handling Writing Rules, and the
Fallback Rule) has been **converged**: the rich content is now first-class in the
one template.

There is therefore **no "thin" output left to generate**. Every repo regenerates
to the same superset; the only per-repo variation is the `<REPO_NAME>`
substitution. `templates/CLAUDE.md` inherits the contract via `@AGENTS.md`.

Rendered output carries the marker `mq-template-lineage: superset-v1`.

## The canonical contract (must survive every regeneration)

These `AGENTS.md` sections are the contract. Losing any of them is a **semantic
regression, not a cosmetic edit** — the generator blocks the write rather than
shipping a downgrade. The list is authoritative in
[`scripts/agent_entrypoints.py`](../scripts/agent_entrypoints.py)
(`CANONICAL_SECTIONS`):

* `## mqobsidian Location`
* `## Read First`
* `## Low-Token Rules`
* `## Rules`
* `## Durable Memory`
* `## Source Intelligence`
* `## Writing Rules`
* `## MQ Skills`
* `## Fallback Rule`

Two content canaries must also remain present (`CANONICAL_CANARIES`):

* `memory/learn/repos/` — the repo-scoped learn read step
* `Do not store or copy secrets` — the secrets / private-path safety rule

`CLAUDE.md` is not re-checked section-by-section: it must carry the lineage
marker and the `@AGENTS.md` include, and it inherits the sections from there.

## Migration invariant

**No repo may be moved from the rich/superset lineage back to a thinner one by
accident.** A regeneration is only ever a refresh *within* `superset-v1`, never a
content downgrade. This is not a soft guideline:

* `check_rendered()` fails the write if any canonical section, canary, or the
  lineage marker is missing, or if a literal `<REPO_NAME>` /
  `<MQOBSIDIAN_VAULT_PATH>` placeholder leaks. **`--force` does not bypass this.**
* `check-agent-entrypoints.py` runs the same check across all core repos in CI,
  so a template edit that would strip the contract fails the PR.

## Per-repo state

| Repo | Entrypoint state | Notes |
| --- | --- | --- |
| `mq-hal` | superset-v1, tracked | Reference rollout (proves no semantic loss). |
| `mq-agent` | tracked, pre-marker | Predates the marker; converges to superset on next regeneration. |
| `mq-mcp` | tracked, pre-marker | Regenerate only when its feature-branch WIP is parked. |
| `mq-ums` | untracked, local-only | Deliberately not tracked/published this cycle. |
| `repo-signal` | untracked, local-only | Same — local-only by decision. |
| `mq-image-analyze` | untracked, local-only | Same — local-only by decision. |

"Local-only" is a deliberate state, not an unfinished one: publishing a repo's
committed agent contract is a separate product/boundary decision, taken when a
repo actually needs a public agent contract — not for symmetry.

## Regenerating safely (maintainer note)

Regeneration is permitted **only when the canonical sections are preserved** —
which the tooling enforces, so the safe path is simply to use it:

1. Dry-run first: `python3 scripts/generate-agents-md.py --repo <repo> --check`
   (and the `generate-claude-md.py` equivalent). `--check` writes nothing and
   reports `new file` / `in sync` / `would change`.
2. The generator refuses to overwrite a **dirty** or **untracked** target unless
   `--force` is passed (git-state guard — overridable). It refuses a **content
   regression** unconditionally (contract guard — not overridable).
3. Generated output must stay machine-independent: embed `$MQ_OBSIDIAN_DIR`
   (resolved by the reader), never a resolved absolute path. The generator
   defaults to that placeholder; pass `--vault-path` only for a throwaway local
   copy.
4. One repo per PR, separate commits, with a message that makes the lineage
   convergence explicit. Do not batch multiple repos into one commit.

`mqobsidian` owns the contract, template, generators, and checks; each target
repo owns its committed entrypoints' freshness, CI, and publication (see
[context-export-contract.md](context-export-contract.md), "Ownership of
generated agent surfaces").
