"""Contract tests for mq.semantic-refresh.v1."""

from __future__ import annotations

import copy
import importlib.util
import json
import sys
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "mq.semantic-refresh.v1.json"
EXAMPLE_PATH = ROOT / "examples" / "semantic-refresh.example.json"
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))
SPEC = importlib.util.spec_from_file_location(
    "validate_export",
    SCRIPTS / "validate-export.py",
)
assert SPEC and SPEC.loader
VALIDATE_EXPORT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATE_EXPORT)


class SemanticRefreshContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        self.example = json.loads(EXAMPLE_PATH.read_text(encoding="utf-8"))
        self.validator = Draft202012Validator(self.schema)

    def validate(self, candidate):
        return list(self.validator.iter_errors(candidate))

    def test_public_safe_example_matches_schema_and_export_invariants(self):
        self.assertEqual(self.validate(self.example), [])
        self.assertEqual(
            VALIDATE_EXPORT.validate_semantic_refresh(EXAMPLE_PATH, self.schema),
            [],
        )

    def test_source_revision_is_required(self):
        candidate = copy.deepcopy(self.example)
        candidate["source"].pop("source_revision")
        self.assertTrue(self.validate(candidate))

    def test_pass_requires_exactly_one_authoritative_generation(self):
        candidate = copy.deepcopy(self.example)
        candidate["postcondition"]["authoritative_active_count"] = 2
        self.assertTrue(self.validate(candidate))

    def test_pass_requires_zero_non_authoritative_retrieval_generations(self):
        candidate = copy.deepcopy(self.example)
        candidate["postcondition"]["non_authoritative_retrieval_count"] = 1
        self.assertTrue(self.validate(candidate))

    def test_fail_can_describe_a_broken_postcondition(self):
        candidate = copy.deepcopy(self.example)
        candidate["postcondition"].update(
            status="FAIL",
            authoritative_active_count=2,
            non_authoritative_retrieval_count=1,
        )
        self.assertEqual(self.validate(candidate), [])

    def test_append_is_not_a_refresh_mode(self):
        candidate = copy.deepcopy(self.example)
        candidate["refresh_semantics"]["replacement"] = "append"
        self.assertTrue(self.validate(candidate))

    def test_authoritative_stores_are_nonempty_and_unique(self):
        empty = copy.deepcopy(self.example)
        empty["authority"]["authoritative_stores"] = []
        self.assertTrue(self.validate(empty))

        duplicated = copy.deepcopy(self.example)
        duplicated["authority"]["authoritative_stores"] = [
            "vs_example_canonical",
            "vs_example_canonical",
        ]
        self.assertTrue(self.validate(duplicated))

    def test_generation_store_must_be_declared_authoritative(self):
        candidate = copy.deepcopy(self.example)
        candidate["generation"]["store_id"] = "vs_example_legacy"
        tmp = EXAMPLE_PATH.parent / ".semantic-refresh-invalid.example.json"
        try:
            tmp.write_text(json.dumps(candidate), encoding="utf-8")
            errors = VALIDATE_EXPORT.validate_semantic_refresh(tmp, self.schema)
        finally:
            tmp.unlink(missing_ok=True)
        self.assertTrue(any("generation.store_id" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
