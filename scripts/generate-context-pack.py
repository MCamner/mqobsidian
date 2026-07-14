#!/usr/bin/env python3
"""Generate a small Markdown context pack for Codex or Claude Code."""

from __future__ import annotations

from argparse import ArgumentParser
from datetime import datetime, timezone
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TEMPLATE = ROOT / "templates" / "context-pack.md"


def bullet_lines(items: list[str], fallback: str) -> str:
    if not items:
        return f"* {fallback}"
    return "\n".join(f"* {item}" for item in items)


# Signals that a task is about source-code structure, where CodeGraph
# (callers/callees, impact, code-flow, symbol search) beats broad grep/read.
CODEGRAPH_TASK_HINTS = (
    "caller",
    "callee",
    "impact",
    "blast radius",
    "call graph",
    "code flow",
    "code-flow",
    "refactor",
    "rename",
    "trace",
    "symbol",
    "where is",
    "implement",
    "writer path",
    "wire ",
    "fix ",
)

# Doc-shaped tasks never need CodeGraph; suppress even if a hint also matches so
# non-source packs stay clean.
CODEGRAPH_TASK_SUPPRESS = (
    "readme",
    "roadmap",
    "release note",
    "changelog",
    "docstring",
    "doc ",
    "docs ",
    "docs/",
)


# Source extensions CodeGraph can index; a `node` query only makes sense for
# these. Shell/PowerShell are unsupported (see docs/integrations/codegraph.md).
SOURCE_EXTS = (".py", ".js", ".ts", ".tsx", ".jsx")

# Hard cap so CodeGraph guidance can never become a token sink in the pack.
MAX_CODEGRAPH_QUERIES = 5


def task_is_source_heavy(task: str) -> bool:
    key = task.lower()
    if any(token in key for token in CODEGRAPH_TASK_SUPPRESS):
        return False
    return any(token in key for token in CODEGRAPH_TASK_HINTS)


def _sanitize_query(task: str) -> str:
    return " ".join(task.split()).replace('"', "'")[:80]


def _repo_relative(path: str, repo: str) -> str:
    prefix = f"{repo}/"
    while path.startswith(prefix):
        path = path[len(prefix):]
    return path


def build_codegraph_queries(
    task: str,
    repo: str | None,
    relevant_repos: list[str],
    relevant_files: list[str],
    symbols: list[str],
    mode: str,
) -> list[str]:
    """Concrete, bounded, copy-pasteable CodeGraph commands for a source task.

    `mode` is auto (heuristic), on (force), or off (suppress). Returns an empty
    list when suppressed, when the task is doc-shaped, or when no target repo is
    known — so a documentation pack carries no CodeGraph noise. Every query
    passes an explicit `-p <repo>` project path, and the list is capped at
    `MAX_CODEGRAPH_QUERIES` so it can never become a token sink.
    """
    if mode == "off":
        return []
    if mode == "auto" and not task_is_source_heavy(task):
        return []
    target = repo or (relevant_repos[0] if relevant_repos else None)
    if not target:
        return []

    queries = [f'codegraph explore "{_sanitize_query(task)}" -p {target} --max-files 8']
    for symbol in symbols:
        symbol = symbol.strip()
        if not symbol:
            continue
        queries.append(f"codegraph callers {symbol} -p {target} -l 20")
        queries.append(f"codegraph impact {symbol} -p {target} -d 2")
    for path in relevant_files:
        if path.split("/", 1)[0] == target and path.lower().endswith(SOURCE_EXTS):
            queries.append(f"codegraph node {_repo_relative(path, target)} -p {target}")

    bounded: list[str] = []
    for query in queries:
        if query not in bounded:
            bounded.append(query)
        if len(bounded) >= MAX_CODEGRAPH_QUERIES:
            break
    return bounded


def codegraph_section(queries: list[str]) -> str:
    """Render the optional `## CodeGraph queries` section, or empty when none."""
    if not queries:
        return ""
    body = "\n".join(queries)
    return (
        "\n## CodeGraph queries\n\n"
        "Bounded source-structure queries for this task; run from your MQ repos "
        "root. Fall back to targeted source reads if the index is missing, "
        "unsupported (shell/PowerShell), locked, or stale. CodeGraph never "
        "replaces source tests or CLI verification.\n\n"
        f"```bash\n{body}\n```\n"
    )


def apply_task_defaults(
    task: str,
    repo: str | None,
    relevant_repos: list[str],
    relevant_files: list[str],
    relevant_decisions: list[str],
    notes: list[str],
    do_not_read: list[str],
) -> tuple[list[str], list[str], list[str], list[str], list[str]]:
    """Add the first MVP defaults while keeping explicit CLI input additive."""
    task_key = task.lower()
    repo_key = (repo or "").lower()

    if repo and repo not in relevant_repos:
        relevant_repos.insert(0, repo)

    if "brain writer paths" in task_key and repo_key in {"", "mq-mcp"}:
        for item in ["mq-mcp", "mqobsidian", "mq-agent"]:
            if item not in relevant_repos:
                relevant_repos.append(item)
        for item in [
            "mqobsidian/schemas/repo-review.v1.json",
            "mqobsidian/schemas/learn-record.v1.json",
            "mq-agent/docs/VAULT_STRUCTURE.md",
            "mq-mcp/mq-mcp/runtime/memory/obsidian_writer.py",
            "mq-mcp/mq-mcp/server.py brain_* wrappers",
            "mq-mcp/tests/test_obsidian_writer.py",
            "mq-mcp/docs/TOOL_SAFETY.md",
            "mq-mcp/docs/ORCHESTRATION_CONTRACT.md",
            "mq-mcp/docs/tool_contracts.json",
        ]:
            if item not in relevant_files:
                relevant_files.append(item)
        for item in [
            "Durable review memory should use `memory/reviews/`.",
            "Durable learn memory should use `memory/learn/`.",
            "Legacy root-level `reviews/` and `learn/` paths should remain readable during migration.",
        ]:
            if item not in relevant_decisions:
                relevant_decisions.append(item)
        for item in [
            "Keep mq-mcp as the writer/runtime owner.",
            "Use mqobsidian schemas as durable-memory contracts, not live execution logic.",
        ]:
            if item not in notes:
                notes.append(item)
        for item in [
            "full README files",
            "old release notes",
            "unrelated UMS docs",
        ]:
            if item not in do_not_read:
                do_not_read.append(item)

    return relevant_repos, relevant_files, relevant_decisions, notes, do_not_read


def render_pack(
    task: str,
    target: str,
    repo: str | None,
    summary: str,
    relevant_repos: list[str],
    relevant_files: list[str],
    relevant_decisions: list[str],
    notes: list[str],
    do_not_read: list[str],
    codegraph_queries: list[str] | None = None,
) -> str:
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    repo_line = repo or ""
    return f"""---
schema: context-pack.v1
target: {target}
task: {task}
generated_at: {generated_at}
repo: {repo_line}
summary: {summary}
---

# Task Context Pack

## Relevant repos

{bullet_lines(relevant_repos, "None specified")}

## Relevant files

{bullet_lines(relevant_files, "None specified")}

## Relevant decisions

{bullet_lines(relevant_decisions, "None specified")}

## Notes

{bullet_lines(notes, "Keep the task pack focused on the current change")}
{codegraph_section(codegraph_queries or [])}
## Do not read first

{bullet_lines(do_not_read, "Broad repo scans unless the pack proves insufficient")}
"""


def parse_args() -> ArgumentParser:
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("task", nargs="?", help="Short task description")
    parser.add_argument("--task", dest="task_option", help="Short task description")
    parser.add_argument("--target", choices=["codex", "claude", "both"], default="both")
    parser.add_argument("--repo", help="Primary repo name for the task")
    parser.add_argument("--summary", help="One-line summary of the minimum context needed")
    parser.add_argument("--relevant-repo", action="append", default=[], help="Relevant repo name")
    parser.add_argument("--relevant-file", action="append", default=[], help="Relevant file or doc path")
    parser.add_argument("--relevant-decision", action="append", default=[], help="Relevant decision or rule")
    parser.add_argument("--symbol", action="append", default=[], help="Named symbol for a CodeGraph callers/impact query")
    parser.add_argument("--note", action="append", default=[], help="Short operator note")
    parser.add_argument("--do-not-read", action="append", default=[], help="Files or surfaces to avoid at first")
    parser.add_argument(
        "--codegraph",
        choices=["auto", "on", "off"],
        default="auto",
        help="Add CodeGraph guidance to notes: auto (source-heavy tasks only), on, or off",
    )
    parser.add_argument("--output", "--out", type=Path, help="Write the pack to this path instead of stdout")
    return parser


def main() -> int:
    parser = parse_args()
    args = parser.parse_args()

    task = args.task_option or args.task
    if not task:
        parser.error("provide a task argument or --task")
    summary = args.summary or f"Minimum context needed for: {task}"

    relevant_repos, relevant_files, relevant_decisions, notes, do_not_read = apply_task_defaults(
        task=task,
        repo=args.repo,
        relevant_repos=args.relevant_repo,
        relevant_files=args.relevant_file,
        relevant_decisions=args.relevant_decision,
        notes=args.note,
        do_not_read=args.do_not_read,
    )

    codegraph_queries = build_codegraph_queries(
        task=task,
        repo=args.repo,
        relevant_repos=relevant_repos,
        relevant_files=relevant_files,
        symbols=args.symbol,
        mode=args.codegraph,
    )

    content = render_pack(
        task=task,
        target=args.target,
        repo=args.repo,
        summary=summary,
        relevant_repos=relevant_repos,
        relevant_files=relevant_files,
        relevant_decisions=relevant_decisions,
        notes=notes,
        do_not_read=do_not_read,
        codegraph_queries=codegraph_queries,
    )

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(content, encoding="utf-8")
        print(args.output)
        return 0

    sys.stdout.write(content)
    return 0


if __name__ == "__main__":
    sys.exit(main())
