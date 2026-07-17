from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _validator_module():
    spec = importlib.util.spec_from_file_location("validate_export", ROOT / "scripts" / "validate-export.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module


class StrictEnforcementTests(unittest.TestCase):
    """DEC: mqobsidian takes a jsonschema dependency for real enforcement.

    The hand-rolled `_schema_lite_errors` recursed only through `properties`.
    Every keyed manifest (`scores`, `evidence`) declares its records under
    `additionalProperties: {<subschema>}` — a schema, not `false` — so the
    records inside were never inspected at all. Not shallowly: not at all.
    That is how `ebms_state` reached the published bundle (see #45).
    """

    def test_a_garbage_score_record_is_rejected(self) -> None:
        module = _validator_module()
        schema = json.loads((ROOT / "schemas" / "memory-score-manifest.v1.json").read_text())
        garbage = {
            "schema": "memory-score-manifest.v1", "source": "x",
            "generated_at": "2026-07-16T00:00:00Z",
            "scores": {"m-1": {"TOTAL": "GARBAGE", "not_even_a_score": True}},
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "memory-score-manifest.json"
            path.write_text(json.dumps(garbage), encoding="utf-8")
            module.ROOT = Path(directory)
            problems = module.validate_manifest_example(path, schema)
        self.assertTrue(problems, "a record of pure garbage must not validate")

    def test_an_undeclared_field_in_a_keyed_record_is_rejected(self) -> None:
        """The exact bug from #45, now caught by the validator itself."""
        module = _validator_module()
        schema = json.loads((ROOT / "schemas" / "memory-score-manifest.v1.json").read_text())
        payload = {
            "schema": "memory-score-manifest.v1", "source": "x",
            "generated_at": "2026-07-16T00:00:00Z",
            "scores": {"m-1": {
                "schema": "memory-score.v1", "memory_id": "m-1",
                "timestamp": "2026-07-16T00:00:00Z", "status": "observed", "score": 0.9,
                "ebms_state": "scratch",
            }},
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "memory-score-manifest.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            module.ROOT = Path(directory)
            problems = module.validate_manifest_example(path, schema)
        self.assertTrue(any("ebms_state" in p for p in problems),
                        f"undeclared field must be named in the error; got {problems}")

    def test_a_conforming_record_still_validates(self) -> None:
        module = _validator_module()
        schema = json.loads((ROOT / "schemas" / "memory-score-manifest.v1.json").read_text())
        payload = {
            "schema": "memory-score-manifest.v1", "source": "x",
            "generated_at": "2026-07-16T00:00:00Z",
            "scores": {"m-1": {
                "schema": "memory-score.v1", "memory_id": "m-1",
                "timestamp": "2026-07-16T00:00:00Z", "status": "observed", "score": 0.9,
            }},
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "memory-score-manifest.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            module.ROOT = Path(directory)
            self.assertEqual(module.validate_manifest_example(path, schema), [])

    def test_jsonschema_is_a_hard_dependency_not_an_optional_one(self) -> None:
        """It must be declared, or CI silently skips the only real check."""
        requirements = (ROOT / "requirements.txt").read_text(encoding="utf-8")
        self.assertIn("jsonschema", requirements)
        workflow = (ROOT / ".github" / "workflows" / "public-safe-check.yml").read_text(encoding="utf-8")
        self.assertIn("requirements.txt", workflow,
                      "CI must install the dependency it now relies on")


class PromotionContractTests(unittest.TestCase):
    def test_new_schemas_are_valid_draft_2020_12_and_examples_validate(self) -> None:
        # This used to skip when jsonschema was absent — which was always, in CI.
        # It is a hard dependency now (requirements.txt), so the check must run
        # or fail; a check that quietly opts out is not a check.
        import jsonschema

        for stem in ("memory-score-manifest", "memory-evidence-manifest", "promotion-policy"):
            schema = json.loads((ROOT / "schemas" / f"{stem}.v1.json").read_text())
            example = json.loads((ROOT / "examples" / f"{stem}.example.json").read_text())
            jsonschema.Draft202012Validator.check_schema(schema)
            jsonschema.Draft202012Validator(
                schema, format_checker=jsonschema.FormatChecker()
            ).validate(example)

    def test_score_map_key_must_match_nested_memory_id(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            module = _validator_module()
            module.ROOT = root
            schema = json.loads((ROOT / "schemas/memory-score-manifest.v1.json").read_text())
            data = json.loads((ROOT / "examples/memory-score-manifest.example.json").read_text())
            data["scores"]["wrong"] = data["scores"].pop("obs-0001")
            path = root / "score.json"
            path.write_text(json.dumps(data))
            self.assertTrue(module.validate_keyed_manifest(path, schema, "scores", "memory_id"))

    def test_evidence_map_key_must_match_nested_ref(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            module = _validator_module()
            module.ROOT = root
            schema = json.loads((ROOT / "schemas/memory-evidence-manifest.v1.json").read_text())
            data = json.loads((ROOT / "examples/memory-evidence-manifest.example.json").read_text())
            data["evidence"]["wrong"] = data["evidence"].pop("observation:obs-0001")
            path = root / "evidence.json"
            path.write_text(json.dumps(data))
            self.assertTrue(module.validate_keyed_manifest(path, schema, "evidence", "ref"))

    def test_policy_freshness_exact_boundary(self) -> None:
        module = _validator_module()
        cases = [
            ("2026-07-15T23:59:01Z", True),
            ("2026-07-15T23:59:00Z", True),
            ("2026-07-15T23:58:59Z", False),
        ]
        for generated, expected in cases:
            with self.subTest(generated=generated):
                self.assertIs(
                    module.manifest_is_fresh(generated, "2026-07-16T00:00:00Z", 60), expected
                )

    def test_future_manifest_is_not_fresh(self) -> None:
        module = _validator_module()
        self.assertFalse(module.manifest_is_fresh(
            "2026-07-16T00:00:01Z", "2026-07-16T00:00:00Z", 60
        ))

    def test_promotion_index_mapping_is_exact(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            module = _validator_module()
            module.ROOT = root
            data = json.loads((ROOT / "examples/truth-export-index.example.json").read_text())
            next(entry for entry in data["surfaces"] if entry["key"] == "scores")["schema"] = "memory-evidence-manifest.v1"
            path = root / "index.json"
            path.write_text(json.dumps(data))
            self.assertTrue(module.validate_promotion_index_mapping(path))

    def test_promotion_index_mapping_handles_malformed_surfaces(self) -> None:
        for surfaces in ("bad", ["bad"]):
            with self.subTest(surfaces=surfaces), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                module = _validator_module()
                module.ROOT = root
                path = root / "index.json"
                path.write_text(json.dumps({"surfaces": surfaces}))
                self.assertTrue(module.validate_promotion_index_mapping(path))


if __name__ == "__main__":
    unittest.main()
