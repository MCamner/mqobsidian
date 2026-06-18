#!/usr/bin/env python3
"""Generate a small MQ-aware CLAUDE.md entrypoint."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path
import sys

from mq_repos import CORE_MQ_REPOS


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TEMPLATE = ROOT / "templates" / "CLAUDE.md"


def parse_args() -> ArgumentParser:
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--repo", help="Target repo name")
    parser.add_argument("--all", action="store_true", help="Generate CLAUDE.md for all core MQ repos")
    parser.add_argument("--template", type=Path, default=DEFAULT_TEMPLATE)
    parser.add_argument("--output", "--out", type=Path, help="Write to this path instead of stdout")
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="With --all, write <repo>/CLAUDE.md files under this directory",
    )
    return parser


def main() -> int:
    parser = parse_args()
    args = parser.parse_args()

    content = args.template.read_text(encoding="utf-8")

    if args.all:
        if args.output or not args.output_dir:
            parser.error("--all requires --output-dir and cannot be combined with --output")
        for repo in CORE_MQ_REPOS:
            path = args.output_dir / repo / "CLAUDE.md"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            print(path)
        return 0

    if not args.repo and args.output:
        parser.error("--repo is required when writing a single CLAUDE.md")

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(content, encoding="utf-8")
        print(args.output)
        return 0

    sys.stdout.write(content)
    return 0


if __name__ == "__main__":
    sys.exit(main())
