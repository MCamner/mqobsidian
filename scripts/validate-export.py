#!/usr/bin/env python3
"""Basic validation pass for public-safe mqobsidian exports."""

from __future__ import annotations

import json
import re
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "schemas"
TEMPLATES = ROOT / "templates"
EXAMPLES = ROOT / "examples"


def read_frontmatter(path: Path) -> dict[str, object]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0] != "---":
        raise ValueError(f"{path.relative_to(ROOT)}: missing frontmatter")
    try:
        end = lines[1:].index("---") + 1
    except ValueError as exc:
        raise ValueError(f"{path.relative_to(ROOT)}: unterminated frontmatter") from exc

    data: dict[str, object] = {}
    for raw_line in lines[1:end]:
        if not raw_line.strip():
            continue
        key, separator, value = raw_line.partition(":")
        if not separator:
            raise ValueError(f"{path.relative_to(ROOT)}: invalid frontmatter line: {raw_line}")
        data[key.strip()] = value.strip()
    return data


def validate_context_pack_frontmatter(path: Path, schema: dict[str, object]) -> list[str]:
    problems: list[str] = []
    data = read_frontmatter(path)
    required = schema.get("required", [])
    properties = schema.get("properties", {})
    if not isinstance(required, list) or not isinstance(properties, dict):
        return [f"{path.relative_to(ROOT)}: invalid context-pack schema shape"]

    for key in required:
        if isinstance(key, str) and not data.get(key):
            problems.append(f"{path.relative_to(ROOT)}: missing required frontmatter `{key}`")

    allowed = set(properties)
    for key in data:
        if key not in allowed:
            problems.append(f"{path.relative_to(ROOT)}: unknown frontmatter `{key}`")

    schema_value = data.get("schema")
    if schema_value != "context-pack.v1":
        problems.append(f"{path.relative_to(ROOT)}: schema must be context-pack.v1")

    target = data.get("target")
    if target not in {"codex", "claude", "both"}:
        problems.append(f"{path.relative_to(ROOT)}: target must be codex, claude, or both")

    return problems


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
    body = section_body(text, heading)
    items: list[str] = []
    for raw_line in body.splitlines():
        line = raw_line.strip()
        if line.startswith(("* ", "- ")):
            items.append(line[2:].strip())
    return items


def validate_context_card(path: Path, schema: dict[str, object]) -> list[str]:
    problems: list[str] = []
    text = path.read_text(encoding="utf-8")
    try:
        frontmatter = read_frontmatter(path)
    except ValueError as exc:
        return [str(exc)]

    required = schema.get("required", [])
    properties = schema.get("properties", {})
    if not isinstance(required, list) or not isinstance(properties, dict):
        return [f"{path.relative_to(ROOT)}: invalid context-card schema shape"]

    data = {
        "schema": frontmatter.get("schema"),
        "repo": frontmatter.get("repo"),
        "role": frontmatter.get("role") or section_body(text, "Role"),
        "owns": section_items(text, "Owns"),
        "does_not_own": section_items(text, "Does not own"),
        "reads_from": section_items(text, "Reads from"),
        "writes_to": section_items(text, "Writes to"),
        "use_when": section_items(text, "Use this card when"),
        "avoid_reading_unless_needed": section_items(text, "Avoid reading unless needed"),
        "updated_at": frontmatter.get("updated_at"),
    }

    allowed = set(properties)
    for key in frontmatter:
        if key not in allowed:
            problems.append(f"{path.relative_to(ROOT)}: unknown frontmatter `{key}`")

    for key in required:
        if isinstance(key, str) and not data.get(key):
            problems.append(f"{path.relative_to(ROOT)}: missing required context-card `{key}`")

    if data["schema"] != "context-card.v1":
        problems.append(f"{path.relative_to(ROOT)}: schema must be context-card.v1")

    # Block-level metadata (Phase 11b) is optional, but when present it must use
    # the enum values declared in the schema. Read allowed values from the schema
    # so it stays the single source of truth.
    for field in ("freshness", "scope", "publishability"):
        value = frontmatter.get(field)
        if value is None:
            continue
        allowed_values = properties.get(field, {}).get("enum")
        if isinstance(allowed_values, list) and value not in allowed_values:
            problems.append(
                f"{path.relative_to(ROOT)}: {field} must be one of {allowed_values}"
            )

    return problems


def validate_feedback_signal(path: Path, schema: dict[str, object]) -> list[str]:
    """Validate a Phase 11c feedback-signal record (JSON) against the schema.

    Shallow on purpose, like the frontmatter validators: enforce the `schema`
    const, required keys, and the enum fields — reading the allowed values from
    the schema so it stays the single source of truth — without pulling in a
    full JSON-Schema dependency.
    """
    problems: list[str] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"{path.relative_to(ROOT)}: invalid JSON: {exc}"]
    if not isinstance(data, dict):
        return [f"{path.relative_to(ROOT)}: feedback-signal must be a JSON object"]

    required = schema.get("required", [])
    properties = schema.get("properties", {})
    if not isinstance(required, list) or not isinstance(properties, dict):
        return [f"{path.relative_to(ROOT)}: invalid feedback-signal schema shape"]

    if data.get("schema") != "feedback-signal.v1":
        problems.append(f"{path.relative_to(ROOT)}: schema must be feedback-signal.v1")
    for key in required:
        if isinstance(key, str) and not data.get(key):
            problems.append(f"{path.relative_to(ROOT)}: missing required `{key}`")

    allowed = set(properties)
    for key in data:
        if key not in allowed:
            problems.append(f"{path.relative_to(ROOT)}: unknown key `{key}`")

    outcome_enum = properties.get("outcome", {}).get("enum")
    if isinstance(outcome_enum, list) and data.get("outcome") not in outcome_enum:
        problems.append(f"{path.relative_to(ROOT)}: outcome must be one of {outcome_enum}")

    judgment_enum = (
        properties.get("judgments", {})
        .get("items", {})
        .get("properties", {})
        .get("judgment", {})
        .get("enum")
    )
    judgments = data.get("judgments", [])
    if isinstance(judgments, list) and isinstance(judgment_enum, list):
        for entry in judgments:
            if not isinstance(entry, dict):
                problems.append(f"{path.relative_to(ROOT)}: each judgment must be an object")
                continue
            if not entry.get("block"):
                problems.append(f"{path.relative_to(ROOT)}: judgment missing `block`")
            if entry.get("judgment") not in judgment_enum:
                problems.append(
                    f"{path.relative_to(ROOT)}: judgment must be one of {judgment_enum}"
                )

    return problems


def _abs_path_hits(value: object, path: str = "") -> list[str]:
    """Recursively flag string values that leak an absolute/private machine path."""
    hits: list[str] = []
    if isinstance(value, str):
        if (
            value.startswith("/")
            or "/Users/" in value
            or "$HOME" in value
            or "\\Users\\" in value
            or re.match(r"^[A-Za-z]:\\", value)
        ):
            hits.append(f"{path or '<root>'}: absolute/private path `{value}`")
    elif isinstance(value, dict):
        for key, item in value.items():
            hits.extend(_abs_path_hits(item, f"{path}.{key}" if path else str(key)))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            hits.extend(_abs_path_hits(item, f"{path}[{index}]"))
    return hits


def validate_contract_map(path: Path, schema: dict[str, object]) -> list[str]:
    """Validate a Delivery B cross-repo contract map (JSON) against the schema.

    Shallow like the other validators: enforce the `schema` const, required keys,
    the `verification.status` enum, and reject absolute private paths — without a
    full JSON-Schema dependency or any local CodeGraph installation.
    """
    problems: list[str] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"{path.relative_to(ROOT)}: invalid JSON: {exc}"]
    if not isinstance(data, dict):
        return [f"{path.relative_to(ROOT)}: contract map must be a JSON object"]

    properties = schema.get("properties", {})
    if not isinstance(properties, dict):
        return [f"{path.relative_to(ROOT)}: invalid contract-map schema shape"]

    if data.get("schema") != "codegraph-contract-map.v1":
        problems.append(f"{path.relative_to(ROOT)}: schema must be codegraph-contract-map.v1")

    allowed_top = set(properties)
    for key in data:
        if key not in allowed_top:
            problems.append(f"{path.relative_to(ROOT)}: unknown key `{key}`")

    contract_schema = properties.get("contracts", {}).get("items", {})
    contract_required = contract_schema.get("required", [])
    contract_props = contract_schema.get("properties", {})
    status_enum = (
        contract_props.get("verification", {})
        .get("properties", {})
        .get("status", {})
        .get("enum")
    )

    contracts = data.get("contracts")
    if not isinstance(contracts, list) or not contracts:
        problems.append(f"{path.relative_to(ROOT)}: contracts must be a non-empty array")
        contracts = []

    for index, contract in enumerate(contracts):
        where = f"{path.relative_to(ROOT)}: contracts[{index}]"
        if not isinstance(contract, dict):
            problems.append(f"{where}: must be an object")
            continue
        for key in contract_required:
            if isinstance(key, str) and not contract.get(key):
                problems.append(f"{where}: missing required `{key}`")
        for key in contract:
            if key not in contract_props:
                problems.append(f"{where}: unknown key `{key}`")
        status = contract.get("verification", {}).get("status") if isinstance(contract.get("verification"), dict) else None
        if isinstance(status_enum, list) and status not in status_enum:
            problems.append(f"{where}: verification.status must be one of {status_enum}")

    problems.extend(f"{path.relative_to(ROOT)}: {hit}" for hit in _abs_path_hits(data))
    return problems


def main() -> int:
    required_schemas = [
        SCHEMAS / "stack-truth.v1.json",
        SCHEMAS / "repo-review.v1.json",
        SCHEMAS / "learn-record.v1.json",
        SCHEMAS / "decision-record.v1.json",
        SCHEMAS / "endpoint-truth.v1.json",
        SCHEMAS / "context-pack.v1.json",
        SCHEMAS / "context-card.v1.json",
        SCHEMAS / "feedback-signal.v1.json",
        SCHEMAS / "repo-memory-index.v1.json",
        SCHEMAS / "codegraph-contract-map.v1.json",
    ]
    required_templates = [
        TEMPLATES / "context-pack.md",
        TEMPLATES / "context-card.md",
        TEMPLATES / "AGENTS.md",
        TEMPLATES / "CLAUDE.md",
    ]
    required = required_schemas + required_templates
    missing = [str(path.relative_to(ROOT)) for path in required if not path.exists()]
    if missing:
        print("missing required export file(s):")
        for item in missing:
            print(f"  - {item}")
        return 1

    parsed_schemas = {}
    for path in required_schemas:
        parsed_schemas[path.name] = json.loads(path.read_text(encoding="utf-8"))

    example_files = sorted(EXAMPLES.glob("*.md"))
    if not example_files:
        print("no example Markdown files found")
        return 1

    problems: list[str] = []
    context_pack_schema = parsed_schemas["context-pack.v1.json"]
    for path in [EXAMPLES / "sanitized-context-pack.md", ROOT / ".mq" / "context" / "task-pack.md"]:
        if path.exists():
            try:
                problems.extend(validate_context_pack_frontmatter(path, context_pack_schema))
            except ValueError as exc:
                problems.append(str(exc))

    context_card_schema = parsed_schemas["context-card.v1.json"]
    for path in sorted((ROOT / "memory" / "context-cards").glob("*.md")):
        problems.extend(validate_context_card(path, context_card_schema))

    feedback_schema = parsed_schemas["feedback-signal.v1.json"]
    feedback_example = EXAMPLES / "feedback-signal.example.json"
    if feedback_example.exists():
        problems.extend(validate_feedback_signal(feedback_example, feedback_schema))

    contract_map_schema = parsed_schemas["codegraph-contract-map.v1.json"]
    contract_map_example = EXAMPLES / "codegraph-contract-map.example.json"
    if contract_map_example.exists():
        problems.extend(validate_contract_map(contract_map_example, contract_map_schema))

    if problems:
        print("export validation failed:")
        for problem in problems:
            print(f"  - {problem}")
        return 1

    print("mqobsidian export scaffolding looks structurally valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
