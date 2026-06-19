#!/usr/bin/env python3
"""Basic validation pass for public-safe mqobsidian exports."""

from __future__ import annotations

import json
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
        SCHEMAS / "repo-memory-index.v1.json",
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

    if problems:
        print("export validation failed:")
        for problem in problems:
            print(f"  - {problem}")
        return 1

    print("mqobsidian export scaffolding looks structurally valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
