"""Policy tests for the NotebookLM consumer profile."""

from __future__ import annotations

import json
import unittest
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
PROFILE_PATH = ROOT / ".mq" / "notebooks.json"


class NotebookConsumerProfile(unittest.TestCase):
    def setUp(self):
        self.profile = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))

    def test_provider_is_experimental_read_only_consumer(self):
        self.assertEqual(self.profile["provider"], "notebooklm")
        self.assertEqual(self.profile["status"], "experimental")
        self.assertEqual(self.profile["role"], "consumer")
        self.assertFalse(self.profile["write_back"])

    def test_materialized_output_is_local_dot_directory(self):
        self.assertEqual(self.profile["output_root"], ".notebooklm")
        self.assertIn("/.notebooklm/", (ROOT / ".gitignore").read_text(encoding="utf-8"))

    def test_includes_are_relative_and_not_broad_vault_roots(self):
        forbidden = {"*", "**", "systems", "systems/**", "memory", "memory/**"}
        for notebook in self.profile["notebooks"].values():
            self.assertTrue(notebook["include"])
            for item in notebook["include"]:
                with self.subTest(path=item):
                    path = PurePosixPath(item)
                    self.assertFalse(path.is_absolute())
                    self.assertNotIn("..", path.parts)
                    self.assertNotIn("\\", item)
                    self.assertNotIn(item.rstrip("/"), forbidden)

    def test_denylist_covers_private_and_generated_surfaces(self):
        required = {
            ".codegraph/**",
            ".notebooklm/**",
            "inbox/**",
            "memory/observations/**",
            "reviews/**",
            "sessions/**",
        }
        for notebook in self.profile["notebooks"].values():
            self.assertTrue(required.issubset(set(notebook["exclude"])))

    def test_first_notebook_has_reviewed_and_deferred_observed_lanes(self):
        notebook = self.profile["notebooks"]["mq-stack-intelligence"]
        self.assertEqual(notebook["display_name"], "MQ Stack Intelligence")
        self.assertEqual(
            notebook["source_lanes"]["reviewed"],
            {"provider": "mqobsidian", "status": "active"},
        )
        self.assertEqual(
            notebook["source_lanes"]["observed"],
            {
                "provider": "codegraph",
                "status": "deferred",
                "requires_revision": True,
            },
        )


if __name__ == "__main__":
    unittest.main()
