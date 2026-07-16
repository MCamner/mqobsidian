from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import jsonschema
import pytest


ROOT = Path(__file__).resolve().parents[1]


def _validator_module():
    spec = importlib.util.spec_from_file_location("validate_export", ROOT / "scripts" / "validate-export.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module


def test_new_schemas_are_valid_draft_2020_12_and_examples_validate() -> None:
    for stem in ("memory-score-manifest", "memory-evidence-manifest", "promotion-policy"):
        schema = json.loads((ROOT / "schemas" / f"{stem}.v1.json").read_text())
        example = json.loads((ROOT / "examples" / f"{stem}.example.json").read_text())
        jsonschema.Draft202012Validator.check_schema(schema)
        jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker()).validate(example)


def test_score_map_key_must_match_nested_memory_id(tmp_path: Path) -> None:
    module = _validator_module()
    module.ROOT = tmp_path
    schema = json.loads((ROOT / "schemas/memory-score-manifest.v1.json").read_text())
    data = json.loads((ROOT / "examples/memory-score-manifest.example.json").read_text())
    data["scores"]["wrong"] = data["scores"].pop("obs-0001")
    path = tmp_path / "score.json"
    path.write_text(json.dumps(data))
    assert module.validate_keyed_manifest(path, schema, "scores", "memory_id")


def test_evidence_map_key_must_match_nested_ref(tmp_path: Path) -> None:
    module = _validator_module()
    module.ROOT = tmp_path
    schema = json.loads((ROOT / "schemas/memory-evidence-manifest.v1.json").read_text())
    data = json.loads((ROOT / "examples/memory-evidence-manifest.example.json").read_text())
    data["evidence"]["wrong"] = data["evidence"].pop("observation:obs-0001")
    path = tmp_path / "evidence.json"
    path.write_text(json.dumps(data))
    assert module.validate_keyed_manifest(path, schema, "evidence", "ref")


@pytest.mark.parametrize("generated,expected", [
    ("2026-07-15T23:59:01Z", True),
    ("2026-07-15T23:59:00Z", True),
    ("2026-07-15T23:58:59Z", False),
])
def test_policy_freshness_exact_boundary(generated: str, expected: bool) -> None:
    module = _validator_module()
    assert module.manifest_is_fresh(generated, "2026-07-16T00:00:00Z", 60) is expected


def test_future_manifest_is_not_fresh() -> None:
    module = _validator_module()
    assert not module.manifest_is_fresh("2026-07-16T00:00:01Z", "2026-07-16T00:00:00Z", 60)


def test_promotion_index_mapping_is_exact(tmp_path: Path) -> None:
    module = _validator_module()
    module.ROOT = tmp_path
    data = json.loads((ROOT / "examples/truth-export-index.example.json").read_text())
    next(entry for entry in data["surfaces"] if entry["key"] == "scores")["schema"] = "memory-evidence-manifest.v1"
    path = tmp_path / "index.json"
    path.write_text(json.dumps(data))
    assert module.validate_promotion_index_mapping(path)


@pytest.mark.parametrize("surfaces", ["bad", ["bad"]])
def test_promotion_index_mapping_handles_malformed_surfaces(tmp_path: Path, surfaces: object) -> None:
    module = _validator_module()
    module.ROOT = tmp_path
    path = tmp_path / "index.json"
    path.write_text(json.dumps({"surfaces": surfaces}))
    assert module.validate_promotion_index_mapping(path)
