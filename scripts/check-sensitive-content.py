#!/usr/bin/env python3
"""Scan public-safe files for obvious secrets or sensitive runtime markers."""

from __future__ import annotations

from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
SCAN_DIRS = ["README.md", "docs", "schemas", "templates", "examples"]
PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
    re.compile(r"(?i)(api[_-]?key|token|secret|password)\\s*[:=]"),
    re.compile(r"(?i)bearer\\s+[A-Za-z0-9._-]+"),
    re.compile(r"\\b(?:\\d{1,3}\\.){3}\\d{1,3}\\b"),
]


def iter_files() -> list[Path]:
    files: list[Path] = []
    for name in SCAN_DIRS:
        path = ROOT / name
        if path.is_file():
            files.append(path)
        elif path.is_dir():
            files.extend(p for p in path.rglob("*") if p.is_file())
    return files


def main() -> int:
    hits: list[str] = []
    for path in iter_files():
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for pattern in PATTERNS:
            if pattern.search(text):
                hits.append(str(path.relative_to(ROOT)))
                break
    if hits:
        print("potentially sensitive content found:")
        for hit in hits:
            print(f"  - {hit}")
        return 1
    print("no obvious sensitive content detected in public-safe surfaces")
    return 0


if __name__ == "__main__":
    sys.exit(main())
