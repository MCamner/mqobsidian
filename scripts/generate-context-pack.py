#!/usr/bin/env python3
"""Generate a small Markdown context pack for Codex or Claude Code."""

from __future__ import annotations

from argparse import ArgumentParser
from datetime import datetime, timezone
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TEMPLATE = ROOT / "templates" / "context-pack.md"


def bullet_lines(items: list[str], fallback: str) -> str:
    if not items:
        return f"* {fallback}"
    return "\n".join(f"* {item}" for item in items)


def render_pack(
    task: str,
    target: str,
    repo: str | None,
    summary: str,
    relevant_repos: list[str],
    relevant_files: list[str],
    relevant_decisions: list[str],
    notes: list[str],
    do_not_read: list[str],
) -> str:
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    repo_line = repo or ""
    return f"""---
schema: context-pack.v1
target: {target}
task: {task}
generated_at: {generated_at}
repo: {repo_line}
summary: {summary}
---

# Task Context Pack

## Relevant repos

{bullet_lines(relevant_repos, "None specified")}

## Relevant files

{bullet_lines(relevant_files, "None specified")}

## Relevant decisions

{bullet_lines(relevant_decisions, "None specified")}

## Notes

{bullet_lines(notes, "Keep the task pack focused on the current change")}

## Do not read first

{bullet_lines(do_not_read, "Broad repo scans unless the pack proves insufficient")}
"""


def parse_args() -> ArgumentParser:
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("task", help="Short task description")
    parser.add_argument("--target", choices=["codex", "claude", "both"], default="both")
    parser.add_argument("--repo", help="Primary repo name for the task")
    parser.add_argument("--summary", required=True, help="One-line summary of the minimum context needed")
    parser.add_argument("--relevant-repo", action="append", default=[], help="Relevant repo name")
    parser.add_argument("--relevant-file", action="append", default=[], help="Relevant file or doc path")
    parser.add_argument("--relevant-decision", action="append", default=[], help="Relevant decision or rule")
    parser.add_argument("--note", action="append", default=[], help="Short operator note")
    parser.add_argument("--do-not-read", action="append", default=[], help="Files or surfaces to avoid at first")
    parser.add_argument("--output", type=Path, help="Write the pack to this path instead of stdout")
    return parser


def main() -> int:
    parser = parse_args()
    args = parser.parse_args()

    content = render_pack(
        task=args.task,
        target=args.target,
        repo=args.repo,
        summary=args.summary,
        relevant_repos=args.relevant_repo,
        relevant_files=args.relevant_file,
        relevant_decisions=args.relevant_decision,
        notes=args.note,
        do_not_read=args.do_not_read,
    )

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(content, encoding="utf-8")
        print(args.output)
        return 0

    sys.stdout.write(content)
    return 0


if __name__ == "__main__":
    sys.exit(main())
