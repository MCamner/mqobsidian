#!/usr/bin/env python3
"""Guard the agent-entrypoint contract against semantic regression.

Renders both templates for every core MQ repo in memory and fails if the
canonical contract, the lineage marker, or placeholder substitution regresses.

It also checks **this repo's own root `AGENTS.md` and `CLAUDE.md`**, under the
same rules and with no repo-name exemption. It did not, and that was the gap:
the check reported "9 repos x 2 entrypoints, canonical contract intact" while
mqobsidian's live root files -- the ones Claude Code and Codex actually load
here -- were a hand-written document outside the lineage, missing all eleven
canonical sections and all ten canaries. A repo that distributes a contract to
nine others is its first consumer, not its exception.

The root files are gitignored, so they are absent in CI and the live check skips
there. That is why it lives in this CI-wired gate rather than a local-only one:
the template half must run everywhere, and the live half runs where the files
exist. `scripts/check-clean-checkout.py` covers what CI can see.

Writes nothing.
"""

from __future__ import annotations

import sys
from pathlib import Path

from agent_entrypoints import check_rendered, render_agents, render_claude
from mq_repos import CORE_MQ_REPOS

ROOT = Path(__file__).resolve().parents[1]
AGENTS_TEMPLATE = ROOT / "templates" / "AGENTS.md"
CLAUDE_TEMPLATE = ROOT / "templates" / "CLAUDE.md"

# This repo's own live entrypoints, checked under the same canonical rules.
LIVE_ENTRYPOINTS = (("agents", "AGENTS.md"), ("claude", "CLAUDE.md"))


def check_live_entrypoints(root: Path = ROOT) -> tuple[list[str], int]:
    """Return findings for this repo's own root entrypoints, and how many existed.

    A missing file is not a finding: `AGENTS.md` and `CLAUDE.md` are gitignored,
    so a fresh checkout has neither.
    """
    findings: list[str] = []
    checked = 0
    for kind, name in LIVE_ENTRYPOINTS:
        path = root / name
        if not path.is_file():
            continue
        checked += 1
        for finding in check_rendered(path.read_text(encoding="utf-8"), kind=kind):
            findings.append(f"{name}: {finding}")
    return findings, checked


def main() -> int:
    agents_tpl = AGENTS_TEMPLATE.read_text(encoding="utf-8")
    claude_tpl = CLAUDE_TEMPLATE.read_text(encoding="utf-8")

    failures = 0
    for repo in CORE_MQ_REPOS:
        rendered = (
            ("agents", render_agents(agents_tpl, repo)),
            ("claude", render_claude(claude_tpl, repo)),
        )
        for kind, content in rendered:
            findings = check_rendered(content, kind=kind)
            if findings:
                failures += 1
                print(f"FAIL {repo} {kind}:")
                for finding in findings:
                    print(f"  - {finding}")

    live_findings, live_checked = check_live_entrypoints()
    if live_findings:
        failures += len(live_findings)
        print("FAIL this repo's own root entrypoints:")
        for finding in live_findings:
            print(f"  - {finding}")
        print(
            "  mqobsidian consumes the contract it distributes. Reassemble with:\n"
            "    python3 scripts/generate-agents-md.py --repo mqobsidian \\\n"
            "      --extension agents-local-extension.md --out AGENTS.md --force\n"
            "    python3 scripts/generate-claude-md.py --repo mqobsidian --out CLAUDE.md --force"
        )

    if failures:
        print(f"agent-entrypoint check FAILED: {failures} regression(s)")
        return 1
    live = f", {live_checked} live root entrypoint(s)" if live_checked else ", no local root files"
    print(
        f"agent-entrypoint check passed: {len(CORE_MQ_REPOS)} repos x 2 entrypoints"
        f"{live}, canonical contract intact"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
