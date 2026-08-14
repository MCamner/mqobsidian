# mqobsidian Wiki

This wiki is a pointer, not a content surface. Every page it used to carry was a
second copy of a file that already had an owner in the repository, and the copies
drifted: between v0.2.1 and v0.3.0 the wiki was edited twice while the repo
shipped two releases.

The repository is the source of truth. Read these instead.

## Orientation

| Question | File |
| --- | --- |
| What is this repo and how do I start? | `README.md` |
| What shipped, and when? | `CHANGELOG.md` |
| What is planned, and what is explicitly a non-goal? | `ROADMAP.md` |
| How is the system structured? | `docs/architecture.md` |

## Memory and truth

| Question | File |
| --- | --- |
| What contracts does this repo own? | `.mq/repo-contract.json`, `docs/memory-model.md` |
| Which surfaces answer "what is true right now"? | `docs/TRUTH_SURFACES.md` |
| How does validated signal become durable memory? | `docs/truth-export.md` |
| How does the context layer stay cheap? | `docs/context-budget.md`, `docs/roadmap-token-reduction.md` |
| Is it actually reducing reads? | `docs/context-effect.md` |

## Integrations

| Repo | File |
| --- | --- |
| `mq-agent` | `docs/mq-agent-integration.md` |
| `mq-mcp` | `docs/mq-mcp-integration.md` |
| `repo-signal` | `docs/repo-signal-integration.md` |
| `mq-ums` | `docs/mq-ums-integration.md` |

## Why this page is nearly empty

`docs/wiki/` had no machine consumers. The published landing page
(`docs/index.html`) never linked it, GitHub Pages serves these files unrendered,
and no MQ tool reads the directory — `mqlaunch repos wiki-status` checks the wiki
remote first and only falls back to this directory when the network check fails.

This page is kept so that fallback still resolves, and so anyone arriving here
lands on the real docs.

`scripts/check-docs-freshness.py` gates the contract list in
`docs/memory-model.md` against `.mq/repo-contract.json` in CI, so the surface that
replaced this one cannot drift the same way unnoticed.
