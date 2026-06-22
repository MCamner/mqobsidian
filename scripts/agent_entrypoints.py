#!/usr/bin/env python3
"""Shared helpers and guardrails for the MQ agent-entrypoint generators.

Holds the canonical AGENTS.md contract (the sections that must survive any
template change, per ADR-005), the lineage marker, template rendering, and
write-time safety checks so a generator cannot silently regress content or
clobber uncommitted / untracked agent files in a target repo.
"""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys

LINEAGE = "superset-v1"
LINEAGE_MARKER = f"mq-template-lineage: {LINEAGE}"

# Section headings that MUST survive any AGENTS.md template change. Losing any
# of these is a semantic regression, not a cosmetic edit (rich lineage, ADR-005).
CANONICAL_SECTIONS = [
    "## mqobsidian Location",
    "## Read First",
    "## Low-Token Rules",
    "## Rules",
    "## Durable Memory",
    "## Source Intelligence",
    "## Writing Rules",
    "## MQ Skills",
    "## Fallback Rule",
]

# Content canaries: rendered output must still carry these exact substrings.
CANONICAL_CANARIES = [
    "memory/learn/repos/",            # repo-scoped learn read step
    "Do not store or copy secrets",   # secrets / private-path safety rule
]

LITERAL_PLACEHOLDERS = ["<REPO_NAME>", "<MQOBSIDIAN_VAULT_PATH>"]


def render_agents(template: str, repo: str, vault_path: str = "$MQ_OBSIDIAN_DIR") -> str:
    return template.replace("<REPO_NAME>", repo).replace("<MQOBSIDIAN_VAULT_PATH>", vault_path)


def render_claude(template: str, repo: str) -> str:
    return template.replace("<REPO_NAME>", repo)


def check_rendered(content: str, *, kind: str) -> list[str]:
    """Return regression findings for a rendered entrypoint. Empty list == OK.

    kind="agents" enforces the full canonical contract. kind="claude" only
    checks the lineage marker, the ``@AGENTS.md`` include (canonical sections
    are inherited from AGENTS.md), and that no literal placeholders leak.
    """
    findings: list[str] = []
    if LINEAGE_MARKER not in content:
        findings.append(f"missing lineage marker '{LINEAGE_MARKER}'")
    for placeholder in LITERAL_PLACEHOLDERS:
        if placeholder in content:
            findings.append(f"unsubstituted placeholder '{placeholder}'")
    if kind == "agents":
        for section in CANONICAL_SECTIONS:
            if section not in content:
                findings.append(f"missing canonical section '{section}'")
        for canary in CANONICAL_CANARIES:
            if canary not in content:
                findings.append(f"missing canonical content '{canary}'")
    elif kind == "claude":
        if "@AGENTS.md" not in content:
            findings.append("CLAUDE.md must include '@AGENTS.md' to inherit canonical sections")
    else:
        findings.append(f"unknown entrypoint kind '{kind}'")
    return findings


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)


def _target_lineage(path: Path) -> str | None:
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            if "mq-template-lineage:" in line:
                return line.split("mq-template-lineage:", 1)[1].strip()
    except (OSError, UnicodeDecodeError):
        return None
    return None


def target_safety(path: Path) -> tuple[list[str], list[str]]:
    """Inspect an existing target file. Returns (blockers, warnings).

    Blockers: the file is git-tracked-and-dirty, or untracked in its repo —
    overwriting would clobber uncommitted work. Warnings: lineage mismatch.
    A path that does not exist, or one outside any git repo, is safe.
    """
    blockers: list[str] = []
    warnings: list[str] = []
    if not path.exists():
        return blockers, warnings
    repo = path.parent
    inside = _git(repo, "rev-parse", "--is-inside-work-tree")
    if inside.returncode != 0 or inside.stdout.strip() != "true":
        return blockers, warnings  # loose file, not under git
    rel = path.name
    status = _git(repo, "status", "--porcelain", "--", rel)
    tracked = _git(repo, "ls-files", "--error-unmatch", rel).returncode == 0
    if status.stdout.strip():
        blockers.append(
            f"{path}: tracked but has uncommitted changes" if tracked
            else f"{path}: untracked (never committed)"
        )
    existing = _target_lineage(path)
    if existing and existing != LINEAGE:
        warnings.append(f"{path}: lineage '{existing}' != current '{LINEAGE}'")
    return blockers, warnings


def write_entrypoint(path: Path, content: str, *, kind: str, force: bool = False, check: bool = False) -> int:
    """Validate, then write (or dry-run) one entrypoint. Returns 0 on success.

    Regression findings always block — ``force`` does not bypass them. Git-state
    blockers (dirty / untracked target) can be overridden with ``force``. With
    ``check=True`` nothing is written; drift vs the on-disk file is reported.
    """
    findings = check_rendered(content, kind=kind)
    if findings:
        print(f"REGRESSION blocked for {path}:", file=sys.stderr)
        for finding in findings:
            print(f"  - {finding}", file=sys.stderr)
        return 1

    blockers, warnings = target_safety(path)
    for warning in warnings:
        print(f"WARNING {warning}", file=sys.stderr)

    if check:
        if not path.exists():
            drift = "new file"
        else:
            drift = "in sync" if path.read_text(encoding="utf-8") == content else "would change"
        print(f"[check] {path}: {drift}")
        return 0

    if blockers and not force:
        print(f"refusing to overwrite {path} (pass --force to override):", file=sys.stderr)
        for blocker in blockers:
            print(f"  - {blocker}", file=sys.stderr)
        return 1
    for blocker in blockers:  # force is set if we reach here with blockers
        print(f"WARNING forced overwrite — {blocker}", file=sys.stderr)

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(path)
    return 0
