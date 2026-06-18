# MQ Wiki Status — 2026-06-18

Manual stack-truth summary generated from GitHub Wiki remotes on
2026-06-18 02:40 +0200.

## Result

Status: **ATTENTION**

Most MQ repos have a GitHub Wiki, but the wiki snapshots are old relative to
current repo work. `mqobsidian` did not have a wiki repository before this page
was published.

## Facts

| Repo | Wiki remote | Latest wiki commit | Local docs surface | Status |
| --- | --- | --- | --- | --- |
| mq-agent | yes | 2026-06-03 | `docs/index.html` | stale |
| mq-mcp | yes | 2026-06-03 | `docs/index.html` | stale |
| mq-hal | yes | 2026-06-03 | `docs/index.html` | stale |
| repo-signal | yes | 2026-06-03 | `docs/index.html`, `docs/wiki/` | stale |
| macos-scripts | yes | 2026-06-03 | `docs/index.html` | stale |
| mq-image-analyze | yes | 2026-06-03 | `docs/index.md` | stale |
| atlas-one | yes | 2026-06-03 | `docs/index.html` | stale |
| mq-ums | yes | 2026-06-03 | `docs/index.html` | stale |
| mqobsidian | created 2026-06-18 | this page | README + vault docs | new |

## Interpretation

- Wiki coverage now exists for the MQ stack including `mqobsidian`.
- Wiki freshness is still stale for repos with post-2026-06-03 work.
- `mq-hal` v2.1.0 Context Pack Status is not reflected in its wiki yet.
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

1. Refresh GitHub Wiki exports for repos that changed after 2026-06-03.
2. Add a repeatable `wiki-status` or `docs-freshness` check to the MQ stack flow.
3. Keep wiki-status compact; do not copy complete wiki pages into mqobsidian.
