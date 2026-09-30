#!/usr/bin/env python3
"""Fail when published docs contradict the repo's own release and contract truth.

The primary target is `docs/memory-model.md`. It is consumed, not just read:
mq-mcp's build_semantic_memory_pack.sh feeds it to agents as this repo's memory
model. It drifted to 6 documented contracts against 23 declared ones before this
check existed.

`docs/wiki/` is checked only while those pages exist. They are a legacy surface
scheduled for consolidation into `docs/`; each check skips when its page is gone,
so removing the pages needs no change here.

It also checks the read-order surface's contract count. That claim drifted twice:
the register grew to 32 and hot.md/index.md said 31, and a day after that was
fixed by hand the register grew to 33 and they said 32 — green gates both times,
because contract coverage was only ever asserted for docs/memory-model.md. A
hand-corrected number is not a gate.

Only the present tense is checked. `deklarerade då 31 kontrakt` inside a dated
log entry records what was true then; demanding that history be rewritten on
every contract addition would be the opposite of freshness.

This check does not verify prose. A claim about another repo's API — the class of
error that put two non-existent mq-mcp tools on this wiki — is out of scope and
still needs review against the source repo.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

CHANGELOG_HEADING = re.compile(r"^##\s*\[?(\d+\.\d+\.\d+)\]?", re.MULTILINE)

# The compressed surfaces an agent reads before anything else (read-order steps
# 1 and 2). Absent for most systems, since systems/ is gitignored.
READ_ORDER_PAGES = (
    Path("systems") / "mqobsidian" / "hot.md",
    Path("systems") / "mqobsidian" / "index.md",
)

# Present tense only: "deklarerar N kontrakt" / "deklarerar nu N kontrakt".
# `deklarerade` is past tense and deliberately does not match.
CONTRACT_COUNT_CLAIM = re.compile(r"\bdeklarerar(?:\s+nu)?\s+(\d+)\s+kontrakt")


def read_version(root: Path) -> str:
    return (root / "VERSION").read_text(encoding="utf-8").strip()


def latest_changelog_version(root: Path) -> str | None:
    text = (root / "CHANGELOG.md").read_text(encoding="utf-8")
    match = CHANGELOG_HEADING.search(text)
    return match.group(1) if match else None


def declared_contracts(root: Path) -> list[str]:
    contract = json.loads((root / ".mq" / "repo-contract.json").read_text(encoding="utf-8"))
    return [name.replace("_", "-") for name in contract["contracts"]]


def missing_contracts(page: Path, contracts: list[str]) -> list[str]:
    documented = page.read_text(encoding="utf-8")
    return [name for name in contracts if name not in documented]


def check(root: Path = REPO_ROOT) -> list[str]:
    """Return one message per stale claim. Empty list means fresh."""
    failures: list[str] = []
    contracts = declared_contracts(root)

    def report_contract_gaps(page: Path) -> None:
        missing = missing_contracts(page, contracts)
        if missing:
            failures.append(
                f"{page.relative_to(root)} is missing {len(missing)} declared "
                f"contract(s): {', '.join(missing)}."
            )

    report_contract_gaps(root / "docs" / "memory-model.md")

    declared = len(contracts)
    for rel in READ_ORDER_PAGES:
        page = root / rel
        if not page.exists():
            continue
        for match in CONTRACT_COUNT_CLAIM.finditer(page.read_text(encoding="utf-8")):
            claimed = int(match.group(1))
            if claimed != declared:
                failures.append(
                    f"{rel} claims {claimed} contract(s); "
                    f".mq/repo-contract.json declares {declared}."
                )

    wiki = root / "docs" / "wiki"

    roadmap = wiki / "Roadmap.md"
    if roadmap.exists():
        version = read_version(root)
        if version not in roadmap.read_text(encoding="utf-8"):
            failures.append(
                f"{roadmap.relative_to(root)} does not mention the current VERSION {version}."
            )

    changelog = wiki / "Changelog.md"
    if changelog.exists():
        released = latest_changelog_version(root)
        if released is None:
            failures.append("CHANGELOG.md has no parsable release heading.")
        elif not re.search(
            rf"^##.*{re.escape(released)}", changelog.read_text(encoding="utf-8"), re.MULTILINE
        ):
            failures.append(
                f"{changelog.relative_to(root)} has no heading for the newest release {released}."
            )

    wiki_memory_model = wiki / "Memory-Model.md"
    if wiki_memory_model.exists():
        report_contract_gaps(wiki_memory_model)

    return failures


def main() -> int:
    failures = check()
    if failures:
        for message in failures:
            print(f"error: {message}", file=sys.stderr)
        print(
            "\ndocs/ is a published surface and docs/memory-model.md is fed to "
            "agents by mq-mcp; hot.md and index.md are what an agent reads "
            "first. Update the pages above, then re-run this check.",
            file=sys.stderr,
        )
        return 1
    print("docs freshness checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
