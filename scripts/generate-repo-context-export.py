#!/usr/bin/env python3
"""Generate deterministic per-repo .mq/context exports from context cards."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path
import shutil
import sys

from mq_repos import CORE_MQ_REPOS


ROOT = Path(__file__).resolve().parents[1]
CARDS = ROOT / "memory" / "context-cards"


def section_body(text: str, heading: str) -> str:
    marker = f"## {heading}"
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() != marker:
            continue
        body: list[str] = []
        for next_line in lines[index + 1 :]:
            if next_line.startswith("## "):
                break
            body.append(next_line)
        return "\n".join(body).strip()
    return ""


def section_items(text: str, heading: str) -> list[str]:
    items: list[str] = []
    for raw_line in section_body(text, heading).splitlines():
        line = raw_line.strip()
        if line.startswith(("* ", "- ")):
            items.append(line[2:].strip())
    return items


def bullet_lines(items: list[str], fallback: str) -> str:
    if not items:
        return f"* {fallback}"
    return "\n".join(f"* {item}" for item in items)


def card_path(repo: str) -> Path:
    candidates = [
        CARDS / f"{repo}-card.md",
        CARDS / f"{repo}.md",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise FileNotFoundError(f"missing context card for {repo}")


def read_card(repo: str) -> tuple[Path, str]:
    path = card_path(repo)
    return path, path.read_text(encoding="utf-8")


def render_active_contract(repo: str, card_text: str) -> str:
    owns = section_items(card_text, "Owns")
    does_not_own = section_items(card_text, "Does not own")
    return f"""# Active Contract: {repo}

## Owns

{bullet_lines(owns, "No ownership items defined.")}

## Does Not Own

{bullet_lines(does_not_own, "No boundary items defined.")}

## Rules

* Treat this file as routing context, not runtime truth.
* Verify current code, tests, CLI behavior, and contracts in the target repo.
* Do not duplicate behavior owned by another MQ repo.
"""


def render_integration_map(repo: str, card_text: str) -> str:
    reads_from = section_items(card_text, "Reads from")
    writes_to = section_items(card_text, "Writes to")
    use_when = section_items(card_text, "Use this card when")
    avoid = section_items(card_text, "Avoid reading unless needed")
    return f"""# Integration Map: {repo}

## Reads From

{bullet_lines(reads_from, "No read dependencies defined.")}

## Writes To

{bullet_lines(writes_to, "No write surfaces defined.")}

## Use When

{bullet_lines(use_when, "Use when repo-local context is insufficient.")}

## Avoid Reading First

{bullet_lines(avoid, "Broad docs unless the compact export is insufficient.")}
"""


def render_current_blockers(repo: str) -> str:
    return f"""# Current Blockers: {repo}

## Known Blockers

* No repo-specific blocker exported in this Phase 4 seed.

## Check Before Acting

* Read `.mq/context/repo-card.md`.
* Read `.mq/context/active-contract.md`.
* Read `.mq/context/integration-map.md`.
* Verify live repo state before making runtime or release claims.
"""


def render_token_budget(repo: str) -> str:
    return f"""# Token Budget: {repo}

## Generated Context Budgets

| File | Budget |
| --- | ---: |
| `repo-card.md` | 60 lines |
| `active-contract.md` | 80 lines |
| `current-blockers.md` | 80 lines |
| `integration-map.md` | 120 lines |
| `task-pack.md` | 200 lines |

## Rule

If a generated context file exceeds its budget, tighten the export instead of
copying broad README, changelog, release-note, or vault history into it.
"""


def export_repo(repo: str, output_root: Path, clean: bool = False) -> list[Path]:
    card_file, card_text = read_card(repo)
    context_dir = output_root / repo / ".mq" / "context"
    if clean and context_dir.exists():
        shutil.rmtree(context_dir)
    context_dir.mkdir(parents=True, exist_ok=True)

    outputs = {
        "repo-card.md": card_file.read_text(encoding="utf-8"),
        "active-contract.md": render_active_contract(repo, card_text),
        "current-blockers.md": render_current_blockers(repo),
        "integration-map.md": render_integration_map(repo, card_text),
        "token-budget.md": render_token_budget(repo),
    }

    written: list[Path] = []
    for filename, content in outputs.items():
        path = context_dir / filename
        path.write_text(content, encoding="utf-8")
        written.append(path)
    return written


def parse_args() -> ArgumentParser:
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--repo", help="Repo name to export")
    parser.add_argument("--all", action="store_true", help="Export all core MQ repos")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "examples" / "repo-context-exports",
        help="Output root. Writes <repo>/.mq/context under this directory.",
    )
    parser.add_argument("--clean", action="store_true", help="Remove existing generated context for each target repo first")
    return parser


def main() -> int:
    parser = parse_args()
    args = parser.parse_args()

    if args.all:
        repos = CORE_MQ_REPOS
    elif args.repo:
        repos = [args.repo]
    else:
        parser.error("use --repo or --all")

    written: list[Path] = []
    for repo in repos:
        written.extend(export_repo(repo=repo, output_root=args.output_dir, clean=args.clean))

    for path in written:
        print(path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
