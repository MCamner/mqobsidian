#!/usr/bin/env python3
"""Basic validation pass for public-safe mqobsidian exports."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "schemas"
EXAMPLES = ROOT / "examples"


def main() -> int:
    required = [
        SCHEMAS / "stack-truth.v1.json",
        SCHEMAS / "repo-review.v1.json",
        SCHEMAS / "learn-record.v1.json",
        SCHEMAS / "decision-record.v1.json",
        SCHEMAS / "endpoint-truth.v1.json",
        SCHEMAS / "context-pack.v1.json",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.exists()]
    if missing:
        print("missing schema file(s):")
        for item in missing:
            print(f"  - {item}")
        return 1

    for path in required:
        json.loads(path.read_text(encoding="utf-8"))

    example_files = sorted(EXAMPLES.glob("*.md"))
    if not example_files:
        print("no example Markdown files found")
        return 1

    print("mqobsidian export scaffolding looks structurally valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
