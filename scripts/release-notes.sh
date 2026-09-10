#!/usr/bin/env bash
# Print one version's section of CHANGELOG.md, for use as GitHub release notes.
#
# The notes come from the changelog section, not from the commit range. Where a
# tag was placed late, the range is misleading: mq-hal's v2.2.0 tag sits five
# days after the work it names, so `v2.2.0..v2.3.0` is a single chore commit
# while the changelog describes a routing control room. The section is the
# deliberate description of what a version means; the range is only where
# someone happened to put a tag.
#
# Exit 3 when the version has no section, so a tag pushed without a changelog
# entry fails loudly instead of publishing an empty release.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VERSION="${1:?usage: release-notes.sh <version> [changelog]}"
CHANGELOG="${2:-$ROOT/CHANGELOG.md}"

python3 - "${VERSION#v}" "$CHANGELOG" <<'PY'
import re
import sys

version, path = sys.argv[1], sys.argv[2]
try:
    text = open(path, encoding="utf-8").read()
except OSError as exc:
    print(f"cannot read {path}: {exc}", file=sys.stderr)
    sys.exit(5)

# Three heading shapes live across the MQ repos; a reader that knows only one
# of them finds nothing and publishes an empty release:
#     ## [2.0.2] - 2026-07-19
#     ## [v1.27.0] — 2026-09-06
#     ## 1.4.0 — 2026-06-03
heading = re.compile(r"^##\s+\[?v?(\d+\.\d+\.\d+)\]?\s*[-—–]?.*$", re.M)

spans = [(m.start(), m.end(), m.group(1)) for m in heading.finditer(text)]
for i, (start, end, name) in enumerate(spans):
    if name != version:
        continue
    stop = spans[i + 1][0] if i + 1 < len(spans) else len(text)
    # Any heading ends the section, not just a version one — an "## Unreleased"
    # or a trailing link block below must not be pulled in.
    body = text[end:stop]
    cut = re.search(r"^## ", body, re.M)
    if cut:
        body = body[: cut.start()]
    body = body.strip("\n")
    if not body.strip():
        print(f"section for {version} in {path} is empty", file=sys.stderr)
        sys.exit(4)

    # A GitHub release body is capped at 125,000 characters and MQ changelog
    # sections get large: macos-scripts' 2.1.0 entry is 111,768. Truncating
    # would publish something that is not the canonical description, which is
    # the one thing this script exists to guarantee. An oversized section is a
    # loud failure instead, and the rule holds in every direction: what gets
    # published is exactly the section, or nothing is.
    LIMIT = 120_000
    if len(body) > LIMIT:
        print(
            f"release notes for {version} are {len(body):,} characters; a "
            f"GitHub release body is capped at 125,000 and a truncated "
            f"section would not be the changelog",
            file=sys.stderr,
        )
        sys.exit(6)

    print(body)
    sys.exit(0)

print(f"no section for {version} in {path}", file=sys.stderr)
sys.exit(3)
PY
