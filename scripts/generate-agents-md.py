#!/usr/bin/env python3
"""Generate a small MQ-aware AGENTS.md entrypoint."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path
import sys

from agent_entrypoints import render_agents, write_entrypoint
from mq_repos import CORE_MQ_REPOS


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TEMPLATE = ROOT / "templates" / "AGENTS.md"


def parse_args() -> ArgumentParser:
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--repo", help="Target repo name")
    parser.add_argument("--all", action="store_true", help="Generate AGENTS.md for all core MQ repos")
    parser.add_argument(
        "--vault-path",
        default="$MQ_OBSIDIAN_DIR",
        help=(
            "mqobsidian vault path to embed in read-order instructions. "
            "Defaults to the portable '$MQ_OBSIDIAN_DIR' placeholder so generated, "
            "committed output stays machine-independent; pass an absolute path only "
            "for a throwaway local copy."
        ),
    )
    parser.add_argument("--template", type=Path, default=DEFAULT_TEMPLATE)
    parser.add_argument("--output", "--out", type=Path, help="Write to this path instead of stdout")
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="With --all, write <repo>/AGENTS.md files under this directory",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite a target even if it is dirty or untracked in its repo",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Dry-run: validate and report drift vs the on-disk file, write nothing",
    )
    return parser


def main() -> int:
    parser = parse_args()
    args = parser.parse_args()

    template = args.template.read_text(encoding="utf-8")

    if args.all:
        if args.output or not args.output_dir:
            parser.error("--all requires --output-dir and cannot be combined with --output")
        rc = 0
        for repo in CORE_MQ_REPOS:
            content = render_agents(template, repo, args.vault_path)
            path = args.output_dir / repo / "AGENTS.md"
            rc |= write_entrypoint(path, content, kind="agents", force=args.force, check=args.check)
        return rc

    if not args.repo:
        parser.error("--repo is required unless --all is used")

    content = render_agents(template, args.repo, args.vault_path)

    if args.output:
        return write_entrypoint(args.output, content, kind="agents", force=args.force, check=args.check)

    sys.stdout.write(content)
    return 0


if __name__ == "__main__":
    sys.exit(main())
