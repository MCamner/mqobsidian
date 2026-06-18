#!/usr/bin/env python3
"""Measure line-count impact of a task context pack.

This is intentionally conservative: it compares the generated task pack plus
available context cards against a broad first-read baseline of common repo docs.
It does not estimate tokenizer-specific costs.
"""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PACK = ROOT / ".mq" / "context" / "task-pack.md"
DEFAULT_BASELINE_FILES = ["README.md", "CHANGELOG.md", "ROADMAP.md", "docs/ROADMAP.md"]


def line_count(path: Path) -> int:
    return len(path.read_text(encoding="utf-8").splitlines())


def section_items(text: str, heading: str) -> list[str]:
    lines = text.splitlines()
    marker = f"## {heading}"
    for index, line in enumerate(lines):
        if line.strip() != marker:
            continue
        items: list[str] = []
        for next_line in lines[index + 1 :]:
            if next_line.startswith("## "):
                break
            stripped = next_line.strip()
            if stripped.startswith(("* ", "- ")):
                items.append(stripped[2:].strip())
        return items
    return []


def read_pack_repos(pack: Path) -> list[str]:
    if not pack.exists():
        raise FileNotFoundError(f"{pack}: missing task pack")
    text = pack.read_text(encoding="utf-8")
    repos = section_items(text, "Relevant repos")
    return [repo for repo in repos if repo and repo != "None specified"]


def repo_candidates(repo: str, workspace_root: Path) -> list[Path]:
    candidates = [
        workspace_root / repo,
        workspace_root / "repos" / repo,
        ROOT if repo == "mqobsidian" else ROOT.parent / repo,
    ]
    if repo == "macos-scripts":
        candidates.append(Path.home() / "macos-scripts")
    return candidates


def resolve_repo(repo: str, workspace_root: Path) -> Path | None:
    for candidate in repo_candidates(repo, workspace_root):
        if (candidate / ".git").exists() or (candidate / "README.md").exists():
            return candidate
    return None


def collect_baseline_files(repos: list[str], workspace_root: Path, baseline_files: list[str]) -> list[Path]:
    files: list[Path] = []
    for repo in repos:
        repo_path = resolve_repo(repo, workspace_root)
        if not repo_path:
            continue
        for rel_path in baseline_files:
            path = repo_path / rel_path
            if path.exists() and path.is_file():
                files.append(path)
    return files


def collect_context_files(pack: Path, repos: list[str]) -> list[Path]:
    files = [pack]
    for repo in repos:
        card = ROOT / "memory" / "context-cards" / f"{repo}-card.md"
        if card.exists():
            files.append(card)
    return files


def rel_display(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        try:
            return str(path.relative_to(ROOT.parent))
        except ValueError:
            return path.name


def render_table(title: str, files: list[Path]) -> list[str]:
    rows = [f"## {title}", "", "| Lines | File |", "| ---: | --- |"]
    for path in files:
        rows.append(f"| {line_count(path)} | `{rel_display(path)}` |")
    rows.append("")
    return rows


def main() -> int:
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--pack", type=Path, default=DEFAULT_PACK)
    parser.add_argument("--workspace-root", type=Path, default=ROOT.parent)
    parser.add_argument("--baseline-file", action="append", default=[])
    parser.add_argument("--format", choices=["text", "markdown"], default="text")
    args = parser.parse_args()

    baseline_files = args.baseline_file or DEFAULT_BASELINE_FILES
    repos = read_pack_repos(args.pack)
    context_files = collect_context_files(args.pack, repos)
    broad_files = collect_baseline_files(repos, args.workspace_root.expanduser(), baseline_files)

    context_lines = sum(line_count(path) for path in context_files)
    broad_lines = sum(line_count(path) for path in broad_files)
    saved_lines = max(0, broad_lines - context_lines)
    reduction = round((saved_lines / broad_lines) * 100, 1) if broad_lines else 0.0

    if args.format == "markdown":
        lines = [
            "# Context Effect Measurement",
            "",
            f"Task pack: `{rel_display(args.pack)}`",
            f"Relevant repos: {', '.join(repos) if repos else 'none'}",
            "",
            "## Summary",
            "",
            "| Context path | Lines |",
            "| --- | ---: |",
            f"| Context pack + available cards | {context_lines} |",
            f"| Broad first-read baseline | {broad_lines} |",
            f"| Avoided first-read lines | {saved_lines} |",
            f"| Reduction | {reduction}% |",
            "",
        ]
        lines.extend(render_table("Context files", context_files))
        lines.extend(render_table("Broad baseline files", broad_files))
        sys.stdout.write("\n".join(lines).rstrip() + "\n")
        return 0

    print(f"task_pack={rel_display(args.pack)}")
    print(f"relevant_repos={','.join(repos)}")
    print(f"context_lines={context_lines}")
    print(f"broad_baseline_lines={broad_lines}")
    print(f"avoided_first_read_lines={saved_lines}")
    print(f"reduction_percent={reduction}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
