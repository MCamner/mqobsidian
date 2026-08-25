"""Contract tests for the experimental NotebookLM source-pack manifest."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "notebook-pack.v1.json"
EXAMPLE_PATH = ROOT / "examples" / "notebook-pack.example.json"


class NotebookPackContract(unittest.TestCase):
    def setUp(self):
        self.schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        self.validator = Draft202012Validator(self.schema)
        self.example = json.loads(EXAMPLE_PATH.read_text(encoding="utf-8"))

    def test_sanitized_example_matches_schema(self):
        self.assertEqual(list(self.validator.iter_errors(self.example)), [])

    def test_source_paths_must_be_relative_and_vault_bounded(self):
        for unsafe in (
            "/Users/example/private.md",
            "../private.md",
            "systems/mqobsidian/../../private.md",
            r"systems\mqobsidian\hot.md",
        ):
            with self.subTest(path=unsafe):
                candidate = json.loads(json.dumps(self.example))
                candidate["sources"][0]["path"] = unsafe
                self.assertTrue(list(self.validator.iter_errors(candidate)))

    def test_hashes_are_lowercase_sha256(self):
        candidate = json.loads(json.dumps(self.example))
        candidate["content_hash"] = "not-a-sha256"
        self.assertTrue(list(self.validator.iter_errors(candidate)))

    def test_generator_is_mq_agent(self):
        candidate = json.loads(json.dumps(self.example))
        candidate["generator"]["name"] = "mqobsidian"
        self.assertTrue(list(self.validator.iter_errors(candidate)))


if __name__ == "__main__":
    unittest.main()
