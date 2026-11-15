"""context-pack.v1 provenance: optional frontmatter that lets a reader tell
whether a pack still describes the repo and vault it was built from.

All provenance keys are optional. A pack written before they existed stays
valid, and a missing key means "not recorded", never "unchanged". Stdlib
unittest only, so it runs in public-safe CI with `python3 -m unittest`.
"""
from __future__ import annotations

import importlib.util
import json
import re
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / "schemas" / "context-pack.v1.json").read_text(encoding="utf-8"))

_spec = importlib.util.spec_from_file_location(
    "validate_export", ROOT / "scripts" / "validate-export.py"
)
assert _spec and _spec.loader
ve = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ve)

PROVENANCE = {
    "task_class": "repo-review",
    "source_commit": "0" * 40,
    "source_state": "clean",
    "contract_version": "1.38.0",
    "vault_commit": "f" * 40,
}


def _pack(extra: dict[str, str]) -> str:
    lines = [
        "schema: context-pack.v1",
        "target: both",
        "task: fix something",
        "generated_at: 2026-11-15T00:00:00+00:00",
        "repo: mq-agent",
        "summary: minimum context",
        *(f"{key}: {value}" for key, value in extra.items()),
    ]
    return "---\n" + "\n".join(lines) + "\n---\n\n# Task Context Pack\n"


class ProvenanceFrontmatter(unittest.TestCase):
    def _problems(self, extra: dict[str, str]) -> list[str]:
        with tempfile.TemporaryDirectory(dir=ROOT) as tmp:
            path = Path(tmp) / "task-pack.md"
            path.write_text(_pack(extra), encoding="utf-8")
            return ve.validate_context_pack_frontmatter(path, SCHEMA)

    def test_a_pack_with_provenance_is_valid(self):
        self.assertEqual(self._problems(PROVENANCE), [])

    def test_a_pack_without_provenance_stays_valid(self):
        self.assertEqual(self._problems({}), [])

    def test_unknown_frontmatter_is_still_rejected(self):
        problems = self._problems({"source_branch": "main"})
        self.assertTrue(any("source_branch" in p for p in problems), problems)

    def test_provenance_keys_are_optional(self):
        for key in PROVENANCE:
            self.assertIn(key, SCHEMA["properties"])
            self.assertNotIn(key, SCHEMA["required"])


class ProvenanceShapes(unittest.TestCase):
    """The flat frontmatter is read as strings, so every shape is a string."""

    def test_commits_are_full_hex_shas(self):
        for key in ("source_commit", "vault_commit"):
            pattern = re.compile(SCHEMA["properties"][key]["pattern"])
            self.assertTrue(pattern.fullmatch("a" * 40))
            self.assertFalse(pattern.fullmatch("abc1234"))
            self.assertFalse(pattern.fullmatch("G" * 40))

    def test_source_state_is_clean_or_dirty(self):
        self.assertEqual(SCHEMA["properties"]["source_state"]["enum"], ["clean", "dirty"])


if __name__ == "__main__":
    unittest.main()
