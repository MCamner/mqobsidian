"""Contract tests for notebook-corpus-index.v1."""

from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "notebook-corpus-index.v1.json"
EXAMPLE_PATH = ROOT / "examples" / "notebook-corpus-index.example.json"


class NotebookCorpusIndexContract(unittest.TestCase):
    def setUp(self):
        self.schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        self.example = json.loads(EXAMPLE_PATH.read_text(encoding="utf-8"))
        self.validator = Draft202012Validator(self.schema)

    def validate(self, candidate):
        return list(self.validator.iter_errors(candidate))

    def test_sanitized_example_matches_schema(self):
        self.assertEqual(self.validate(self.example), [])

    def test_unknown_role_is_first_class(self):
        candidate = copy.deepcopy(self.example)
        candidate["items"][0]["classification"] = {
            "role": "unknown",
            "method": "unknown",
        }
        self.assertEqual(self.validate(candidate), [])

    def test_override_requires_provenance(self):
        candidate = copy.deepcopy(self.example)
        candidate["items"][0]["classification"] = {
            "role": "source",
            "method": "override",
        }
        self.assertTrue(self.validate(candidate))

    def test_hash_is_optional_but_when_present_is_sha256(self):
        candidate = copy.deepcopy(self.example)
        candidate["items"][0].pop("content_sha256")
        self.assertEqual(self.validate(candidate), [])
        candidate["items"][0]["content_sha256"] = "bad"
        self.assertTrue(self.validate(candidate))

    def test_no_file_body_field_is_allowed(self):
        candidate = copy.deepcopy(self.example)
        candidate["items"][0]["body"] = "raw corpus content"
        self.assertTrue(self.validate(candidate))

    def test_notebook_and_item_identity_are_not_titles(self):
        candidate = copy.deepcopy(self.example)
        candidate["notebooks"][0]["title"] = "Renamed notebook"
        self.assertEqual(self.validate(candidate), [])
        self.assertEqual(candidate["notebooks"][0]["notebook_id"], "nb-001")

    def test_example_is_deterministically_ordered_and_referentially_sound(self):
        notebook_ids = [n["notebook_id"] for n in self.example["notebooks"]]
        item_ids = [i["item_id"] for i in self.example["items"]]
        self.assertEqual(notebook_ids, sorted(notebook_ids))
        self.assertEqual(item_ids, sorted(item_ids))
        self.assertEqual(len(notebook_ids), len(set(notebook_ids)))
        self.assertEqual(len(item_ids), len(set(item_ids)))
        known = set(notebook_ids)
        self.assertTrue(all(i["notebook_id"] in known for i in self.example["items"]))

    def test_same_hash_is_sufficient_to_reconstruct_duplicate_relationship(self):
        candidate = copy.deepcopy(self.example)
        candidate["items"][1]["content_sha256"] = candidate["items"][0]["content_sha256"]
        self.assertEqual(self.validate(candidate), [])
        grouped = {}
        for item in candidate["items"]:
            digest = item.get("content_sha256")
            if digest:
                grouped.setdefault(digest, []).append(item["item_id"])
        duplicates = [ids for ids in grouped.values() if len(ids) > 1]
        self.assertEqual(duplicates, [["item-001", "item-002"]])


if __name__ == "__main__":
    unittest.main()
