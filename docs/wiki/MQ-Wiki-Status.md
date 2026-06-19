# MQ Wiki Status — 2026-06-18

Stack-truth summary refreshed with `mqlaunch repos wiki-status` on
2026-06-18 03:53 +0200.

## Result

Status: **OK**

All checked MQ repos have a GitHub Wiki remote. Local repo docs now match their
current `VERSION` for the wiki freshness checks.

## Facts

| Repo | VERSION | Wiki remote | Wiki commit | Status |
| --- | --- | --- | --- | --- |
| mq-mcp | 2.0.0 | yes | `cf2f283` | OK |
| mq-agent | 1.18.0 | yes | `d190aab` | OK |
| repo-signal | 1.4.0 | yes | `f7deb20` | OK |
| macos-scripts | 1.0.0 | yes | `ec23b8d` | OK |
| mq-image-analyze | 1.4.0 | yes | `51f8ee5` | OK |
| mq-hal | 2.1.0 | yes | `1c53b42` | OK |
| mq-ums | 0.1.4 | yes | `570b33f` | OK |
| mqobsidian | 0.2.1 | yes | `2830565` | OK |
| atlas-one | 1.4.0 | yes | `4d021f8` | OK |

## Interpretation

- Wiki coverage now exists for every checked MQ repo.
- `mqlaunch repos wiki-status` is the local freshness check for this page.
- `repo-signal` and `atlas-one` README version drift was fixed before this
  refresh.
- `mq-hal` exposes mqobsidian context-pack readiness through
  `mqlaunch hal context`.
- `mqobsidian` should remember wiki freshness as compact durable stack memory,
  but should not duplicate full wiki contents.

## Recommendation

Add a small wiki/docs freshness job owned by `mq-agent` or routed by `mq-hal`:

```text
mq-agent   -> measures wiki freshness and exports truth
mq-hal     -> shows wiki/docs freshness to the operator
mqobsidian -> stores compact wiki-status truth notes
```

## Next action

1. Keep running `mqlaunch repos wiki-status` before treating wikis as fresh.
2. Keep wiki-status compact; do not copy complete wiki pages into mqobsidian.
3. Add a scheduled or operator-triggered wiki/docs freshness job when the stack
   is ready for automation.
