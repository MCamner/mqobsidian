#!/usr/bin/env python3
"""Generate a small MQ-aware CLAUDE.md entrypoint."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TEMPLATE = ROOT / "templates" / "CLAUDE.md"


def parse_args() -> ArgumentParser:
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--template", type=Path, default=DEFAULT_TEMPLATE)
    parser.add_argument("--output", "--out", type=Path, help="Write to this path instead of stdout")
    return parser


def main() -> int:
    parser = parse_args()
    args = parser.parse_args()

    content = args.template.read_text(encoding="utf-8")

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(content, encoding="utf-8")
        print(args.output)
        return 0

    sys.stdout.write(content)
    return 0


if __name__ == "__main__":
    sys.exit(main())
