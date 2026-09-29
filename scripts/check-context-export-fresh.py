#!/usr/bin/env python3
"""Fail when this repo's own `.mq/context` export has drifted from the generator.

CI already diffs `examples/repo-context-exports` on every push, so the published
copy of every repo's context export stays fresh. Nothing checked the original:
this repo's root `.mq/context/` is tracked, is what an agent actually reads
first, and drifted from 2026-06-17 to 2026-09-29 — three of its five owned files
disagreed with the generator — while the published copy stayed green. Gating the
copy and not the original is the defect this closes.

Read-only, unlike the `examples/` step: it renders into a temporary directory
and compares, so it runs in the local gate as well as in CI and needs no
CI-only exemption.

`task-pack.md` is mq-agent's per-task file and is not compared.
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

from context_budgets import EXPORTED_CONTEXT_FILES

REPO_ROOT = Path(__file__).resolve().parent.parent
GENERATOR = REPO_ROOT / "scripts" / "generate-repo-context-export.py"
SELF_REPO = "mqobsidian"


def drifted_files(root: Path = REPO_ROOT) -> list[str]:
    """Return the owned filenames whose on-disk copy differs from the generator."""
    live = root / ".mq" / "context"
    with tempfile.TemporaryDirectory() as tmp:
        result = subprocess.run(
            [sys.executable, str(GENERATOR), "--repo", SELF_REPO, "--output-dir", tmp],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(f"generator failed: {result.stderr.strip()}")
        fresh = Path(tmp) / SELF_REPO / ".mq" / "context"
        drifted = []
        for name in EXPORTED_CONTEXT_FILES:
            expected = (fresh / name).read_text(encoding="utf-8")
            actual = (live / name).read_text(encoding="utf-8") if (live / name).exists() else None
            if actual != expected:
                drifted.append(name)
    return drifted


def main() -> int:
    try:
        drifted = drifted_files()
    except (RuntimeError, OSError) as exc:
        print(f"context export check failed: {exc}")
        return 1

    if drifted:
        print("this repo's own .mq/context is stale:")
        for name in drifted:
            print(f"  - .mq/context/{name}")
        print(
            "regenerate into a scratch directory and copy the owned files in:\n"
            "  python3 scripts/generate-repo-context-export.py --repo mqobsidian "
            "--output-dir <scratch>\n"
            "Do not point --output-dir at the parent directory: the generator "
            "writes <output-dir>/<repo>/.mq/context for every target repo."
        )
        return 1

    print("this repo's own .mq/context matches the generator")
    return 0


if __name__ == "__main__":
    sys.exit(main())
