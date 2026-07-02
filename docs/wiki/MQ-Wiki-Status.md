# MQ Wiki Status — 2026-06-29

Stack-truth summary checked with `mqlaunch repos wiki-status` on
2026-06-29 after fixing the local wiki-status fallback. A direct GitHub Wiki remote check for `mqobsidian` also resolved `HEAD` at `e85435a`.

## Result

Status: **MIXED**

`mqobsidian` is now reported as **OK** from its local `docs/wiki` surface. The
stack-level result is still not globally green because several GitHub Wiki
remotes could not be verified from the current execution environment.

## Facts

| Repo | VERSION | Local wiki status | Wiki signal | Note |
| --- | --- | --- | --- | --- |
| mq-mcp | 2.0.0 | UNKNOWN | unknown | remote check unavailable |
| mq-agent | 1.18.0 | UNKNOWN | unknown | remote check unavailable |
| repo-signal | 1.4.0 | OK | local-docs (9 files) | remote unverified |
| macos-scripts | 1.0.0 | OK | local (`4e83642`) | remote unverified |
| mq-image-analyze | 1.4.0 | UNKNOWN | unknown | remote check unavailable |
| mq-hal | 2.1.0 | UNKNOWN | unknown | remote check unavailable |
| mq-ums | 0.1.4 | UNKNOWN | unknown | remote check unavailable |
| mqobsidian | 0.2.1 | OK | local-docs (10 files) | remote HEAD `e85435a` verified directly |
| atlas-one | 1.4.0 | UNKNOWN | unknown | remote check unavailable |

## Fix Applied

- `mqlaunch repos wiki-status` no longer treats DNS/network failure as `wiki missing`.
- Local wiki fallbacks are recognized:
  - `~/REPO.wiki`
  - `~/REPO.wiki-remote`
  - `REPO/docs/wiki`
- The recommendations resolver no longer emits `BASH_SOURCE[0]: parameter not set`
  when launched from shell contexts that do not populate `BASH_SOURCE`.

## Additional Findings

- `mqobsidian/docs/wiki/Memory-Model.md` documents `memory-observation.v1`,
  `memory-score.v1`, and `promotion-event.v1`.
- `mqobsidian/docs/wiki/Integrations.md` documents the `mq-mcp` brain tools for
  previewing and applying memory scores.

## mqobsidian Repo Boundary

`mqobsidian` is a GitHub repo, but it is intentionally not a full mirror of the
local vault. The repo tracks portable/public-safe surfaces such as:

- `docs/` and `docs/wiki/`
- `schemas/`
- `examples/`
- selected `memory/context-cards/`
- selected `systems/*/index.md` and `systems/*/hot.md`

Many operational vault folders are local-only and gitignored, including
`sessions/`, `reviews/`, `learn/`, `raw_logs/`, `projects/`, `inbox/`, and most
of `memory/`. These folders should not count as wiki or repo freshness failures.

## Interpretation

The mqobsidian wiki is locally updated for the memory-scoring model, passes the local wiki-status fallback, and has a reachable GitHub Wiki remote. This means the tracked wiki/docs surface is current enough for local use. It does not mean every local vault folder should be
published to GitHub. Several other MQ GitHub Wiki remotes still need a network/auth-capable check before marking the whole MQ stack as fresh.

## Recommendation

1. Treat `mqobsidian` local wiki docs as current for memory scoring.
2. Keep local-only vault folders out of wiki/repo freshness gates unless a specific
   public-safe export is produced.
3. Re-run `mqlaunch repos wiki-status` from a normal networked terminal before
   publishing a stack-wide OK claim for all MQ repos.
4. Sync or clone missing repo wiki remotes if the UNKNOWN repos should have local
   wiki coverage.
