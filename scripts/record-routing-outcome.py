#!/usr/bin/env python3
"""Persist one contract-validated mq-agent routing outcome in durable memory."""

from __future__ import annotations

import argparse
import fcntl
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = Path(os.environ.get("MQ_OBSIDIAN_DIR", ROOT)) / "routing" / "outcomes.jsonl"
SENSITIVE_PATTERNS = (
    re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
    re.compile(r"(?i)bearer\s+[A-Za-z0-9._-]+"),
    re.compile(r"(?i)(?:api[_-]?key|token|secret|password)\s*[:=]"),
    re.compile(r"(?:^|\s)/Users/[^\s]+"),
    re.compile(r"(?:^|\s)[A-Za-z]:\\Users\\[^\s]+"),
)


def default_schema_path() -> Path:
    explicit = os.environ.get("MQ_AGENT_ROUTE_OUTCOME_SCHEMA")
    if explicit:
        return Path(explicit).expanduser()
    agent_dir = Path(os.environ.get("MQ_AGENT_DIR", Path.home() / "mq-agent")).expanduser()
    return agent_dir / "schemas" / "model_route_outcome.schema.json"


def load_json(path: Path | None) -> Any:
    if path is None:
        return json.load(sys.stdin)
    return json.loads(path.read_text(encoding="utf-8"))


def load_validator(path: Path) -> Draft202012Validator:
    if not path.is_file():
        raise ValueError(f"mq-agent outcome schema not found: {path}")
    try:
        schema = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid mq-agent outcome schema: {exc}") from exc
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema, format_checker=FormatChecker())


def _strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        return [text for item in value.values() for text in _strings(item)]
    if isinstance(value, list):
        return [text for item in value for text in _strings(item)]
    return []


def validate_outcome(data: Any, validator: Draft202012Validator) -> dict[str, Any]:
    errors = sorted(validator.iter_errors(data), key=lambda error: list(error.absolute_path))
    if errors:
        details = "; ".join(error.message for error in errors[:3])
        raise ValueError(f"outcome does not match mq-agent schema: {details}")
    if not isinstance(data, dict):
        raise ValueError("outcome must be a JSON object")

    verification = data["verification"]
    if verification["status"] == "PASS":
        if not verification["checks"]:
            raise ValueError("PASS outcome must name at least one deterministic check")
        for field in ("attempted", "model_output_received", "schema_valid"):
            if data[field] is not True:
                raise ValueError(f"PASS outcome requires {field}=true")
        if data["escalated"] is not False or data["escalation_reason"] is not None:
            raise ValueError("PASS outcome must not also be escalated")
    else:
        if data["escalated"] is not True or data["escalation_reason"] is None:
            raise ValueError("non-PASS outcome must preserve its escalation")
        if data["accepted_by_agent"] or data["accepted_by_operator"]:
            raise ValueError("non-PASS outcome must not be accepted")

    for text in _strings(data):
        if any(pattern.search(text) for pattern in SENSITIVE_PATTERNS):
            raise ValueError("outcome contains sensitive or machine-specific material")
    return data


def canonical(record: dict[str, Any]) -> str:
    return json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def append_verified(
    record: dict[str, Any],
    path: Path,
    validator: Draft202012Validator,
) -> bool:
    path.parent.mkdir(parents=True, exist_ok=True)
    wanted = canonical(record)
    with path.open("a+", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        handle.seek(0)
        for number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                existing = json.loads(line)
                validate_outcome(existing, validator)
            except (json.JSONDecodeError, ValueError) as exc:
                raise ValueError(f"existing history line {number} is invalid: {exc}") from exc
            if canonical(existing) == wanted:
                return False
        handle.seek(0, os.SEEK_END)
        handle.write(wanted + "\n")
        handle.flush()
        os.fsync(handle.fileno())
    return True


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Validate one mq.model-route-outcome.v1 record against mq-agent's "
            "authoritative schema and append only contract-validated, public-safe evidence."
        )
    )
    parser.add_argument(
        "input",
        nargs="?",
        type=Path,
        help="outcome JSON file; omit to read one JSON object from stdin",
    )
    parser.add_argument("--schema", type=Path, default=default_schema_path())
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--dry-run", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        validator = load_validator(args.schema.expanduser())
        record = validate_outcome(load_json(args.input), validator)
        if args.dry_run:
            print(json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True))
            return 0
        appended = append_verified(record, args.output.expanduser(), validator)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"invalid routing outcome: {exc}", file=sys.stderr)
        return 2

    if appended:
        print(f"recorded routing outcome: {record['decision_id']}")
    else:
        print(f"already recorded: {record['decision_id']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
