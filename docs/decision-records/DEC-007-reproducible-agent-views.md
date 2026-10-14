---
schema: decision-record.v1
decision_id: DEC-007
created_at: 2026-10-13T00:00:00Z
title: A committed agent view is built from committed sources only
status: accepted
---

# Decision

## Context

`memory/learn/agent/mqobsidian.md` is read-order step 0. It is tracked:
`scripts/check-context-links.py` requires it as a front door, and the README
lists it second in the read order. The other agent views under
`memory/learn/agent/` are local and gitignored.

mq-agent's `agent-views rebuild` built that view from three sources:
`systems/mqobsidian/hot.md`, `systems/mqobsidian/index.md` and
`memory/learn/repos/mqobsidian.md`. The first two are tracked. The third is
gitignored output of the learn export and exists only in an operator's vault.
The view also stamped `generated:` with the day of the rebuild.

So the committed file could not be reproduced:

- an operator vault and a clean clone rebuilt it differently, since only the
  operator vault had lessons to quote;
- the view changed whenever the local lessons store changed, and showed up as a
  modified tracked file in the operator checkout;
- `agent-views check` reported it stale on any day after the rebuild, because
  the date was part of the content.

## Decision

1. **Generated, committed agent views are reproducible from committed sources.**
   A view is either local or versioned, never a mix.
2. **A system opts in with `agent_view: versioned` in its own `index.md`.** The
   declaration sits in the tracked source the view is built from, so no
   separate registry can disagree with it. The generator also accepts it in
   `hot.md`. `index.md` is preferred because it is the stable description of
   the system, while `hot.md` is a volatile cache with no line budget to spare.
3. **A versioned view is built from `hot.md` and `index.md` only.** It does not
   quote `memory/learn/repos/`, not even when an operator vault has it.
4. **Local lessons stay local.** `memory/learn/repos/*.md` remains gitignored,
   and local views keep their "Relevant lessons" section.
5. **`generated:` is the newest `updated:` date among the sources** (today only
   when no source carries one), so a rebuild is a pure function of the sources.
6. **CI rebuilds and compares.** Public Safe Check runs
   `mq-agent agent-views check --system mqobsidian` on a clean checkout.
   `tests/test_versioned_agent_view.py` is the local guard that needs no
   mq-agent install.

The generator lives in mq-agent (`mq_agent/tools/agent_views.py`,
`docs/AGENT_VIEW_CONTRACT.md` rule 6). This repo owns the declaration and the
committed output.

## Consequences

- The mqobsidian front door loses its "Relevant lessons" section. Lessons were
  never reproducible there, and they are still in the local vault and in the
  local views.
- `agent-views check` now reports a stale view only when its sources changed.
- The CI step installs mq-agent at a release tag (first `v1.34.0`), not
  `main`. A generator change reaches this repo only when the tag is bumped here,
  and the view is rebuilt in the same change. Until 2026-10-15 the step used
  `main`, which would have turned this repo red on an unrelated mq-agent merge.
- Making another view versioned means adding the marker to that system's
  `index.md`, tracking the view, and adding it to the CI step.

## Verified basis

- `.gitignore` ignores `memory/*`. `memory/learn/agent/mqobsidian.md` is the only
  tracked file under `memory/learn/agent/` (`git ls-files`).
- On 2026-10-13, a rebuild from a clean worktree of `origin/main` dropped the
  `memory/learn/repos/mqobsidian.md` source and the lessons section. The same
  rebuild in the operator vault kept both and changed the lessons.
- With the marker and the mq-agent change, the operator vault (including local
  lessons) and a clean copy produce byte-identical views. `agent-views check`
  reports `fresh` on a later day. The generator on mq-agent `main` before the
  change reports the same view `stale`.

## Related

- DEC-002: mqobsidian owns the truth surfaces it publishes.
- `scripts/check-context-links.py` lists the required front doors.
- `scripts/check-learn-namespace.py` covers the learn export's own namespace. It
  is the other half of keeping generated and authored memory apart.
- mq-agent `docs/AGENT_VIEW_CONTRACT.md` is the generator contract.
