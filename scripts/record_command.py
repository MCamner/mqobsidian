#!/usr/bin/env python3
"""Append one validated command observation to the local ranking inbox."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
COMMANDS = ROOT / "memory" / "commands"
PATTERNS = COMMANDS / "patterns" / "patterns.jsonl"
INBOX = COMMANDS / "inbox" / "observations.jsonl"

AGENTS = {"claude", "codex"}
OUTCOMES = {"worked", "partial", "failed"}
RISK_CLASSES = {"read-only", "mutating"}
TASK_TYPES = {"repo-inspect", "locate", "review", "validate", "diagnose", "generate"}


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_patterns(path: Path) -> dict[str, dict[str, Any]]:
    patterns: dict[str, dict[str, Any]] = {}
    if not path.exists():
        return patterns
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{number}: invalid JSON: {exc}") from exc
        pattern_id = record.get("id")
        if not isinstance(pattern_id, str) or not pattern_id:
            raise ValueError(f"{path}:{number}: pattern is missing id")
        patterns[pattern_id] = record
    return patterns


def build_record(args: argparse.Namespace, patterns: dict[str, dict[str, Any]]) -> dict[str, Any]:
    pattern = patterns.get(args.pattern_id)
    if pattern is None:
        raise ValueError(f"unknown pattern_id: {args.pattern_id!r}")
    if args.agent not in AGENTS:
        raise ValueError(f"agent must be one of {sorted(AGENTS)}")
    if args.repo != "mqobsidian":
        raise ValueError("repo must be 'mqobsidian' in command-library v1")
    if args.task_type not in TASK_TYPES:
        raise ValueError(f"task_type must be one of {sorted(TASK_TYPES)}")
    if args.outcome not in OUTCOMES:
        raise ValueError(f"outcome must be one of {sorted(OUTCOMES)}")
    if args.risk_class not in RISK_CLASSES:
        raise ValueError(f"risk_class must be one of {sorted(RISK_CLASSES)}")

    pattern_tasks = pattern.get("task_tags", [])
    if args.task_type not in pattern_tasks:
        raise ValueError(
            f"task_type {args.task_type!r} is not declared by pattern "
            f"{args.pattern_id!r}: {pattern_tasks}"
        )
    pattern_risk = pattern.get("risk_class")
    if args.risk_class != pattern_risk:
        raise ValueError(
            f"risk_class {args.risk_class!r} does not match pattern "
            f"{args.pattern_id!r}: {pattern_risk!r}"
        )

    command = args.command.strip()
    sanitized = args.sanitized_command.strip()
    if not command:
        raise ValueError("command must not be empty")
    if not sanitized:
        raise ValueError("sanitized-command must not be empty")

    record: dict[str, Any] = {
        "timestamp": args.timestamp or _now(),
        "agent": args.agent,
        "repo": args.repo,
        "task_type": args.task_type,
        "raw_command": command,
        "sanitized_command": sanitized,
        "outcome": args.outcome,
        "risk_class": args.risk_class,
        "promote_candidate": args.promote_candidate,
        "pattern_id": args.pattern_id,
    }
    for key in ("note", "session_ref"):
        value = getattr(args, key).strip()
        if value:
            record[key] = value
    return record


def append_record(record: dict[str, Any], path: Path, *, dry_run: bool = False) -> None:
    if dry_run:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(
            json.dumps(
                record,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            )
            + "\n"
        )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="record_command.py",
        description=(
            "Append one real command event to command ranking. "
            "Validates pattern, task type, risk and outcome; never promotes."
        ),
    )
    parser.add_argument("pattern_id", help="known id from patterns/patterns.jsonl")
    parser.add_argument("--command", required=True, help="command exactly as run; stays local")
    parser.add_argument(
        "--sanitized-command",
        required=True,
        help="portable command with private paths, hosts and secrets replaced",
    )
    parser.add_argument("--agent", required=True, choices=sorted(AGENTS))
    parser.add_argument("--repo", default="mqobsidian")
    parser.add_argument("--task-type", required=True, choices=sorted(TASK_TYPES))
    parser.add_argument("--outcome", default="worked", choices=sorted(OUTCOMES))
    parser.add_argument("--risk-class", required=True, choices=sorted(RISK_CLASSES))
    parser.add_argument("--note", default="", help="short explanation of the outcome")
    parser.add_argument("--session-ref", default="", help="stable session or run reference")
    parser.add_argument(
        "--promote-candidate",
        action="store_true",
        help="flag for later human curation; does not promote",
    )
    parser.add_argument("--dry-run", action="store_true", help="validate and print without appending")
    parser.add_argument("--patterns", type=Path, default=PATTERNS, help=argparse.SUPPRESS)
    parser.add_argument("--inbox", type=Path, default=INBOX, help=argparse.SUPPRESS)
    parser.add_argument("--timestamp", default="", help=argparse.SUPPRESS)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
        patterns = load_patterns(args.patterns)
        record = build_record(args, patterns)
    except ValueError as exc:
        print(f"invalid command observation: {exc}", file=sys.stderr)
        return 2

    append_record(record, args.inbox, dry_run=args.dry_run)
    if args.dry_run:
        print(json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True))
        print(f"dry-run: would append to {args.inbox}", file=sys.stderr)
    else:
        print(f"recorded: {record['pattern_id']} -> {record['outcome']}")
        print("next: python3 memory/commands/build_views.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
