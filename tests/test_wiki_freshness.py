"""Contract tests for the published-wiki freshness gate."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))
SPEC = importlib.util.spec_from_file_location(
    "check_wiki_freshness",
    SCRIPTS / "check-wiki-freshness.py",
)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def build_repo(root: Path, *, version: str = "1.2.3") -> None:
    """Write the smallest tree the check reads: a fresh, passing repo."""
    (root / ".mq").mkdir()
    (root / "docs" / "wiki").mkdir(parents=True)
    (root / "VERSION").write_text(f"{version}\n", encoding="utf-8")
    (root / "CHANGELOG.md").write_text(
        f"# Changelog\n\n## [Unreleased]\n\n## [{version}] - 2026-08-14\n\n### Added\n\n- thing\n",
        encoding="utf-8",
    )
    (root / ".mq" / "repo-contract.json").write_text(
        json.dumps({"contracts": ["memory_score.v1", "promotion_event.v1"]}),
        encoding="utf-8",
    )
    wiki = root / "docs" / "wiki"
    (wiki / "Roadmap.md").write_text(f"# Roadmap\n\nCurrent release: {version}\n", encoding="utf-8")
    (wiki / "Changelog.md").write_text(f"# Changelog\n\n## {version} - 2026-08-14\n", encoding="utf-8")
    (wiki / "Memory-Model.md").write_text(
        "# Memory Model\n\n- `memory-score.v1`\n- `promotion-event.v1`\n",
        encoding="utf-8",
    )


class WikiFreshnessTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)
        build_repo(self.tmp)

    def test_fresh_repo_passes(self) -> None:
        self.assertEqual(MODULE.check(self.tmp), [])

    def test_roadmap_missing_current_version_fails(self) -> None:
        (self.tmp / "docs" / "wiki" / "Roadmap.md").write_text(
            "# Roadmap\n\nCurrent release: 0.9.0\n", encoding="utf-8"
        )
        failures = MODULE.check(self.tmp)
        self.assertEqual(len(failures), 1)
        self.assertIn("1.2.3", failures[0])

    def test_changelog_missing_newest_release_fails(self) -> None:
        (self.tmp / "docs" / "wiki" / "Changelog.md").write_text(
            "# Changelog\n\n## 0.9.0 - 2026-01-01\n", encoding="utf-8"
        )
        failures = MODULE.check(self.tmp)
        self.assertEqual(len(failures), 1)
        self.assertIn("newest release 1.2.3", failures[0])

    def test_unreleased_heading_is_not_read_as_the_newest_release(self) -> None:
        """[Unreleased] carries no version, so it must not shadow the real one."""
        self.assertEqual(MODULE.latest_changelog_version(self.tmp), "1.2.3")

    def test_undocumented_contract_fails_and_is_named(self) -> None:
        (self.tmp / ".mq" / "repo-contract.json").write_text(
            json.dumps({"contracts": ["memory_score.v1", "memory_query.v1"]}),
            encoding="utf-8",
        )
        failures = MODULE.check(self.tmp)
        self.assertEqual(len(failures), 1)
        self.assertIn("memory-query.v1", failures[0])

    def test_real_repo_is_fresh(self) -> None:
        """The gate must hold for the checked-in wiki, not just fixtures."""
        self.assertEqual(MODULE.check(ROOT), [])


if __name__ == "__main__":
    unittest.main()
