#!/usr/bin/env python3
"""Basic validation pass for public-safe mqobsidian exports."""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
import sys
from typing import Any


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


def _schema_lite_errors(data: Any, schema: dict[str, Any], where: str) -> list[str]:
    """Shallow JSON-Schema check: type, required, const, enum, closed objects.

    Enough to validate the truth-surface manifest examples against their schemas
    without a full JSON-Schema dependency. Ignores format/pattern by design.
    """
    errs: list[str] = []
    schema_type = schema.get("type")
    if schema_type == "object":
        if not isinstance(data, dict):
            return [f"{where}: expected object"]
        props = schema.get("properties", {})
        for key in schema.get("required", []) or []:
            if key not in data:
                errs.append(f"{where}: missing required `{key}`")
        if schema.get("additionalProperties") is False:
            for key in data:
                if key not in props:
                    errs.append(f"{where}: unknown key `{key}`")
        for key, value in data.items():
            if key in props:
                errs.extend(_schema_lite_errors(value, props[key], f"{where}.{key}"))
    elif schema_type == "array":
        if not isinstance(data, list):
            return [f"{where}: expected array"]
        items = schema.get("items", {})
        for index, element in enumerate(data):
            errs.extend(_schema_lite_errors(element, items, f"{where}[{index}]"))
    if "const" in schema and data != schema["const"]:
        errs.append(f"{where}: must equal {schema['const']!r}")
    if "enum" in schema and data not in schema["enum"]:
        errs.append(f"{where}: must be one of {schema['enum']}")
    return errs


def validate_manifest_example(path: Path, schema: dict[str, object]) -> list[str]:
    """Validate a truth-surface manifest example (JSON) against its schema."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"{path.relative_to(ROOT)}: invalid JSON: {exc}"]
    rel = path.relative_to(ROOT)
    problems = [f"{rel}: {msg}" for msg in _schema_lite_errors(data, schema, "<root>")]
    problems.extend(f"{rel}: {hit}" for hit in _abs_path_hits(data))
    return problems


def validate_promotion_policy(path: Path, schema: dict[str, object]) -> list[str]:
    problems = validate_manifest_example(path, schema)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return problems
    review = data.get("review_threshold")
    auto = data.get("auto_threshold")
    if isinstance(review, (int, float)) and isinstance(auto, (int, float)) and auto < review:
        problems.append(f"{path.relative_to(ROOT)}: auto_threshold must be >= review_threshold")
    max_age = data.get("max_manifest_age_seconds")
    if not isinstance(max_age, int) or isinstance(max_age, bool) or max_age < 0:
        problems.append(f"{path.relative_to(ROOT)}: max_manifest_age_seconds must be a non-negative integer")
    weights = data.get("weights")
    if isinstance(weights, dict) and any(isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0 for value in weights.values()):
        problems.append(f"{path.relative_to(ROOT)}: weights must be non-negative numbers")
    return problems


def manifest_is_fresh(generated_at: str, now: str, max_age_seconds: int) -> bool:
    """Policy boundary: exact max age is fresh; only greater age is stale."""
    generated = datetime.fromisoformat(generated_at.replace("Z", "+00:00"))
    current = datetime.fromisoformat(now.replace("Z", "+00:00"))
    age = (current - generated).total_seconds()
    return 0 <= age <= max_age_seconds


def validate_promotion_index_mapping(path: Path) -> list[str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("surfaces"), list):
        return [f"{path.relative_to(ROOT)}: surfaces must be an array"]
    entries = data["surfaces"]
    if not all(isinstance(entry, dict) for entry in entries):
        return [f"{path.relative_to(ROOT)}: each surface must be an object"]
    actual = {entry.get("key"): (entry.get("schema"), entry.get("path")) for entry in entries}
    expected = {
        "scores": ("memory-score-manifest.v1", "exports/memory-score-manifest.json"),
        "evidence": ("memory-evidence-manifest.v1", "exports/memory-evidence-manifest.json"),
        "promotion-policy": ("promotion-policy.v1", "exports/promotion-policy.json"),
    }
    return [f"{path.relative_to(ROOT)}: invalid mapping for `{key}`" for key, value in expected.items() if actual.get(key) != value]


def validate_keyed_manifest(path: Path, schema: dict[str, object], map_key: str,
                            identity_key: str) -> list[str]:
    problems = validate_manifest_example(path, schema)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return problems
    records = data.get(map_key)
    if isinstance(records, dict):
        for key, record in records.items():
            if not isinstance(record, dict) or record.get(identity_key) != key:
                problems.append(
                    f"{path.relative_to(ROOT)}: {map_key} key `{key}` must match nested `{identity_key}`"
                )
    return problems


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


def validate_measurement(path: Path, schema: dict[str, object]) -> list[str]:
    """Validate a Delivery D CodeGraph measurement record (JSON) against schema.

    Enforces the `schema` const, required keys, the `task_type`/`result` enums,
    the rule that correctness may be claimed only when tests pass, and rejects
    absolute private paths — no full JSON-Schema dependency.
    """
    problems: list[str] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"{path.relative_to(ROOT)}: invalid JSON: {exc}"]
    if not isinstance(data, dict):
        return [f"{path.relative_to(ROOT)}: measurement must be a JSON object"]

    properties = schema.get("properties", {})
    if not isinstance(properties, dict):
        return [f"{path.relative_to(ROOT)}: invalid measurement schema shape"]

    if data.get("schema") != "codegraph-measurement.v1":
        problems.append(f"{path.relative_to(ROOT)}: schema must be codegraph-measurement.v1")
    for key in data:
        if key not in properties:
            problems.append(f"{path.relative_to(ROOT)}: unknown key `{key}`")

    item_schema = properties.get("measurements", {}).get("items", {})
    item_required = item_schema.get("required", [])
    item_props = item_schema.get("properties", {})
    type_enum = item_props.get("task_type", {}).get("enum")
    result_enum = item_props.get("verification", {}).get("properties", {}).get("result", {}).get("enum")

    measurements = data.get("measurements")
    if not isinstance(measurements, list) or not measurements:
        problems.append(f"{path.relative_to(ROOT)}: measurements must be a non-empty array")
        measurements = []

    for index, item in enumerate(measurements):
        where = f"{path.relative_to(ROOT)}: measurements[{index}]"
        if not isinstance(item, dict):
            problems.append(f"{where}: must be an object")
            continue
        for key in item_required:
            if isinstance(key, str) and key not in item:
                problems.append(f"{where}: missing required `{key}`")
        for key in item:
            if key not in item_props:
                problems.append(f"{where}: unknown key `{key}`")
        if isinstance(type_enum, list) and item.get("task_type") not in type_enum:
            problems.append(f"{where}: task_type must be one of {type_enum}")
        result = item.get("verification", {}).get("result") if isinstance(item.get("verification"), dict) else None
        if isinstance(result_enum, list) and result not in result_enum:
            problems.append(f"{where}: verification.result must be one of {result_enum}")
        # Exit-gate rule: correctness may be claimed only when tests pass.
        if item.get("correctness_claimed") and result != "pass":
            problems.append(f"{where}: correctness_claimed requires verification.result == pass")

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
        SCHEMAS / "codegraph-measurement.v1.json",
        SCHEMAS / "status-manifest.v1.json",
        SCHEMAS / "inbox-manifest.v1.json",
        SCHEMAS / "memory-score-manifest.v1.json",
        SCHEMAS / "memory-evidence-manifest.v1.json",
        SCHEMAS / "promotion-policy.v1.json",
        SCHEMAS / "views-manifest.v1.json",
        SCHEMAS / "truth-export-index.v1.json",
        SCHEMAS / "promotion-event.v1.json",
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

    measurement_schema = parsed_schemas["codegraph-measurement.v1.json"]
    measurement_example = EXAMPLES / "codegraph-measurement.example.json"
    if measurement_example.exists():
        problems.extend(validate_measurement(measurement_example, measurement_schema))

    manifest_examples = {
        "status-manifest.example.json": "status-manifest.v1.json",
        "inbox-manifest.example.json": "inbox-manifest.v1.json",
        "memory-score-manifest.example.json": "memory-score-manifest.v1.json",
        "memory-evidence-manifest.example.json": "memory-evidence-manifest.v1.json",
        "views-manifest.example.json": "views-manifest.v1.json",
        "truth-export-index.example.json": "truth-export-index.v1.json",
        "promotion-event.example.json": "promotion-event.v1.json",
    }
    for example_name, schema_name in manifest_examples.items():
        example_path = EXAMPLES / example_name
        if example_path.exists():
            problems.extend(validate_manifest_example(example_path, parsed_schemas[schema_name]))

    problems.extend(validate_promotion_policy(
        EXAMPLES / "promotion-policy.example.json", parsed_schemas["promotion-policy.v1.json"]
    ))
    problems.extend(validate_keyed_manifest(
        EXAMPLES / "memory-score-manifest.example.json",
        parsed_schemas["memory-score-manifest.v1.json"], "scores", "memory_id"
    ))
    problems.extend(validate_promotion_index_mapping(EXAMPLES / "truth-export-index.example.json"))
    problems.extend(validate_keyed_manifest(
        EXAMPLES / "memory-evidence-manifest.example.json",
        parsed_schemas["memory-evidence-manifest.v1.json"], "evidence", "ref"
    ))

    if problems:
        print("export validation failed:")
        for problem in problems:
            print(f"  - {problem}")
        return 1

    print("mqobsidian export scaffolding looks structurally valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
