#!/usr/bin/env python3
"""Fail when the built skill copies do not match `skills-src/`.

`tools/build-skills.sh` copies every `skills-src/<name>/` into three agent
locations, so Claude Code and Codex read the same skills:

    .claude/skills/<name>/    .codex/skills/<name>/    .agents/skills/<name>/

Nothing checked that they still match. The build is a plain copy, so drift is
silent and easy to cause: editing a built copy instead of the source, or adding
a skill to `skills-src/` and not re-running the build. The three surfaces were
byte-identical when this check was written -- that was luck confirmed by hand,
not a property anything enforced.

The build is a copy, so this compares the trees directly rather than building
into a temporary directory. It writes nothing.

Local-only: `.gitignore` keeps `skills-src/` and all three built trees out of
the repo apart from two force-added source skills, so CI has almost nothing to
compare. `scripts/check-gate-parity.py` declares it LOCAL_ONLY with that reason.

A fresh checkout is not drift. In CI, `skills-src/` exists -- two source skills
are force-added -- while all three built trees are absent, because they are
gitignored. Reading that as "the build is stale" made this check fail on every
push before the distinction existed. Nothing built means nothing to be
inconsistent with; *some* trees built and others missing is real drift.
"""

from __future__ import annotations

import filecmp
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

SRC = Path("skills-src")
BUILT_DIRS = (
    Path(".claude") / "skills",
    Path(".codex") / "skills",
    Path(".agents") / "skills",
)


def source_skills(root: Path) -> list[str]:
    """Skill names the build would copy: a directory holding a SKILL.md."""
    src = root / SRC
    if not src.is_dir():
        return []
    return sorted(p.name for p in src.iterdir() if p.is_dir() and (p / "SKILL.md").is_file())


def _is_content(path: Path) -> bool:
    """A file the build ships, not Finder's .DS_Store written on browsing a folder."""
    return path.is_file() and path.name != ".DS_Store"


def _tree_differences(source: Path, built: Path, label: str) -> list[str]:
    """Return one message per file that differs, is missing, or is unexpected."""
    problems: list[str] = []
    src_files = {p.relative_to(source) for p in source.rglob("*") if _is_content(p)}
    built_files = {p.relative_to(built) for p in built.rglob("*") if _is_content(p)}

    for rel in sorted(src_files - built_files):
        problems.append(f"{label}: missing {rel}")
    for rel in sorted(built_files - src_files):
        problems.append(f"{label}: unexpected {rel} (not in skills-src)")
    for rel in sorted(src_files & built_files):
        if not filecmp.cmp(source / rel, built / rel, shallow=False):
            problems.append(f"{label}: {rel} differs from skills-src")
    return problems


def stale_built_skills(root: Path = REPO_ROOT) -> list[str]:
    """Return one message per divergence between skills-src and a built tree."""
    names = source_skills(root)
    if not names:
        return []

    present = [d for d in BUILT_DIRS if (root / d).is_dir()]
    if not present:
        # A checkout where the build has never run: the built trees are
        # gitignored, so their absence is the normal state, not staleness.
        return []

    problems: list[str] = []
    for built_dir in BUILT_DIRS:
        built_root = root / built_dir
        if not built_root.is_dir():
            problems.append(
                f"{built_dir} is missing while other built trees exist; "
                "run tools/build-skills.sh"
            )
            continue

        built_names = sorted(p.name for p in built_root.iterdir() if p.is_dir())
        for name in sorted(set(names) - set(built_names)):
            problems.append(f"{built_dir}/{name} was never built")
        for name in sorted(set(built_names) - set(names)):
            problems.append(f"{built_dir}/{name} is not in skills-src (renamed or removed)")

        for name in sorted(set(names) & set(built_names)):
            problems.extend(
                _tree_differences(root / SRC / name, built_root / name, f"{built_dir}/{name}")
            )
    return problems


def main() -> int:
    if not (REPO_ROOT / SRC).is_dir():
        print("skills build check skipped: no local skills-src/")
        return 0
    if not any((REPO_ROOT / d).is_dir() for d in BUILT_DIRS):
        print("skills build check skipped: skills are not built in this checkout")
        return 0

    problems = stale_built_skills()
    if problems:
        print("built skill copies have drifted from skills-src:", file=sys.stderr)
        for message in problems:
            print(f"  - {message}", file=sys.stderr)
        print(
            "\nEdit skills-src/, never a built copy, then run tools/build-skills.sh.",
            file=sys.stderr,
        )
        return 1

    names = source_skills(REPO_ROOT)
    print(f"skills build checks passed: {len(names)} skill(s) match in all three locations")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
