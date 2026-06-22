#!/usr/bin/env python3
"""Guard the agent-entrypoint templates against semantic regression.

Renders both templates for every core MQ repo in memory and fails if the
canonical contract, the lineage marker, or placeholder substitution regresses.
Writes nothing. Wired into the public-safe CI workflow.
"""

from __future__ import annotations

from pathlib import Path
import sys

from agent_entrypoints import check_rendered, render_agents, render_claude
from mq_repos import CORE_MQ_REPOS

ROOT = Path(__file__).resolve().parents[1]
AGENTS_TEMPLATE = ROOT / "templates" / "AGENTS.md"
CLAUDE_TEMPLATE = ROOT / "templates" / "CLAUDE.md"


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

    if failures:
        print(f"agent-entrypoint check FAILED: {failures} rendering(s) regressed")
        return 1
    print(
        f"agent-entrypoint check passed: {len(CORE_MQ_REPOS)} repos x 2 entrypoints, "
        "canonical contract intact"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
