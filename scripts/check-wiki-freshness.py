#!/usr/bin/env python3
"""Fail when docs/wiki/ contradicts the repo's own release and contract truth.

docs/wiki/ is a published surface: GitHub Pages deploys docs/** on main. Between
v0.2.1 and v0.3.0 it was edited in two commits total, so it kept claiming an old
release and an old contract count while the repo moved on. This check pins the
three claims that can be compared mechanically:

1. the wiki roadmap names the current VERSION
2. the wiki changelog has a heading for the newest CHANGELOG.md release
3. the wiki memory model lists every contract in .mq/repo-contract.json

It does not verify prose. A claim about another repo's API — the class of error
that put two non-existent mq-mcp tools on this wiki — is out of scope here and
still needs review against the source repo.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

CHANGELOG_HEADING = re.compile(r"^##\s*\[?(\d+\.\d+\.\d+)\]?", re.MULTILINE)


def read_version(root: Path) -> str:
    return (root / "VERSION").read_text(encoding="utf-8").strip()


def latest_changelog_version(root: Path) -> str | None:
    text = (root / "CHANGELOG.md").read_text(encoding="utf-8")
    match = CHANGELOG_HEADING.search(text)
    return match.group(1) if match else None


def declared_contracts(root: Path) -> list[str]:
    contract = json.loads((root / ".mq" / "repo-contract.json").read_text(encoding="utf-8"))
    return [name.replace("_", "-") for name in contract["contracts"]]


def check(root: Path = REPO_ROOT) -> list[str]:
    """Return one message per stale wiki claim. Empty list means fresh."""
    failures: list[str] = []
    wiki = root / "docs" / "wiki"

    version = read_version(root)
    roadmap = wiki / "Roadmap.md"
    if version not in roadmap.read_text(encoding="utf-8"):
        failures.append(
            f"{roadmap.relative_to(root)} does not mention the current VERSION {version}."
        )

    released = latest_changelog_version(root)
    if released is None:
        failures.append("CHANGELOG.md has no parsable release heading.")
    else:
        changelog = wiki / "Changelog.md"
        if not re.search(rf"^##.*{re.escape(released)}", changelog.read_text(encoding="utf-8"), re.MULTILINE):
            failures.append(
                f"{changelog.relative_to(root)} has no heading for the newest release {released}."
            )

    memory_model = wiki / "Memory-Model.md"
    documented = memory_model.read_text(encoding="utf-8")
    missing = [name for name in declared_contracts(root) if name not in documented]
    if missing:
        failures.append(
            f"{memory_model.relative_to(root)} is missing {len(missing)} declared "
            f"contract(s): {', '.join(missing)}."
        )

    return failures


def main() -> int:
    failures = check()
    if failures:
        for message in failures:
            print(f"error: {message}", file=sys.stderr)
        print(
            "\ndocs/wiki is published via GitHub Pages. Update the pages above, "
            "then re-run this check.",
            file=sys.stderr,
        )
        return 1
    print("wiki freshness checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
