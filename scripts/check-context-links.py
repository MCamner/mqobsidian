#!/usr/bin/env python3
"""Validate the required front-door context surfaces."""

from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_FRONT_DOORS = (
    "memory/learn/agent/mqobsidian.md",
    "systems/mqobsidian/hot.md",
    "systems/mqobsidian/index.md",
    "docs/CONTEXT_CONTRACT.md",
)


def missing_front_doors(root: Path = ROOT) -> list[str]:
    return [rel_path for rel_path in REQUIRED_FRONT_DOORS if not (root / rel_path).is_file()]


def main() -> int:
    missing = missing_front_doors()
    if missing:
        print("context front-door check failed:")
        for rel_path in missing:
            print(f"  - missing required file: {rel_path}")
        return 1

    print("context front-door checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
