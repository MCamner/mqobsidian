#!/usr/bin/env python3
"""Check conservative line budgets for instruction and context surfaces."""

from __future__ import annotations

from pathlib import Path
import fnmatch
import sys

from context_budgets import (
    CONTEXT_BUDGETS,
    EXPORTED_CONTEXT_FILES,
    LOCAL_CONTEXT_FILES,
)


ROOT = Path(__file__).resolve().parents[1]

BUDGETS = {
    "README.md": 160,
    "docs/context-budget.md": 120,
    "templates/context-pack.md": 80,
    "templates/context-card.md": 60,
    "templates/AGENTS.md": 120,
    "templates/CLAUDE.md": 120,
    "examples/sanitized-context-pack.md": 120,
}

OPTIONAL_BUDGETS = {
    "AGENTS.md": 120,
    "CLAUDE.md": 120,
    **{f".mq/context/{name}": CONTEXT_BUDGETS[name] for name in LOCAL_CONTEXT_FILES},
}

GLOB_BUDGETS = {
    "systems/*/hot.md": 80,
    "systems/*/index.md": 120,
    "memory/context-cards/*.md": 60,
    "memory/learn/agent/*.md": 120,
    "examples/generated-agent-entrypoints/*/AGENTS.md": 120,
    "examples/generated-agent-entrypoints/*/CLAUDE.md": 120,
    **{
        f"examples/repo-context-exports/*/.mq/context/{name}": CONTEXT_BUDGETS[name]
        for name in EXPORTED_CONTEXT_FILES
    },
}


def line_count(path: Path) -> int:
    return len(path.read_text(encoding="utf-8").splitlines())


def check_budget(rel_path: str, limit: int) -> str | None:
    path = ROOT / rel_path
    if not path.exists():
        return None
    count = line_count(path)
    if count > limit:
        return f"{rel_path}: {count} lines exceeds budget {limit}"
    return None


def check_glob_budget(pattern: str, limit: int) -> list[str]:
    problems: list[str] = []
    for path in sorted(ROOT.glob(pattern)):
        if not path.is_file():
            continue
        rel_path = str(path.relative_to(ROOT))
        if any(fnmatch.fnmatch(rel_path, optional) for optional in OPTIONAL_BUDGETS):
            continue
        problem = check_budget(rel_path, limit)
        if problem:
            problems.append(problem)
    return problems


def main() -> int:
    violations: list[str] = []

    for rel_path, limit in BUDGETS.items():
        path = ROOT / rel_path
        if not path.exists():
            violations.append(f"{rel_path}: missing required file for budget check")
            continue
        problem = check_budget(rel_path, limit)
        if problem:
            violations.append(problem)

    for rel_path, limit in OPTIONAL_BUDGETS.items():
        problem = check_budget(rel_path, limit)
        if problem:
            violations.append(problem)

    for pattern, limit in GLOB_BUDGETS.items():
        violations.extend(check_glob_budget(pattern, limit))

    if violations:
        print("token budget check failed:")
        for item in violations:
            print(f"  - {item}")
        return 1

    print("token budget checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
