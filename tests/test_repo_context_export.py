"""Contract tests for the reference repo-context exporter."""
from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))
SPEC = importlib.util.spec_from_file_location(
    "generate_repo_context_export",
    SCRIPTS / "generate-repo-context-export.py",
)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

from context_budgets import EXPORTED_CONTEXT_FILES  # noqa: E402


class ExportCleanTests(unittest.TestCase):
    """`--clean` must remove only the files this exporter owns.

    `systems/mqobsidian/hot.md:32` documents that clean "tar nu bara bort
    exportens fem ägda filer och bevarar `task-pack.md` samt okända filer".
    That describes mq-agent's exporter. This reference exporter can be pointed
    at a live repo with `--output-dir`, where wiping the whole directory
    destroys a per-task `task-pack.md` mq-agent owns, plus anything else the
    target repo keeps there.
    """

    def _seed(self, root: Path, repo: str) -> Path:
        context = root / repo / ".mq" / "context"
        context.mkdir(parents=True)
        for name in EXPORTED_CONTEXT_FILES:
            (context / name).write_text("stale export\n", encoding="utf-8")
        (context / "task-pack.md").write_text("per-task, owned by mq-agent\n", encoding="utf-8")
        (context / "local-notes.md").write_text("unknown file\n", encoding="utf-8")
        return context

    def test_clean_preserves_task_pack_and_unknown_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            context = self._seed(root, "mq-agent")

            MODULE.export_repo(repo="mq-agent", output_root=root, clean=True)

            self.assertTrue(
                (context / "task-pack.md").exists(),
                "clean deleted task-pack.md, which this exporter does not own",
            )
            self.assertEqual(
                (context / "task-pack.md").read_text(encoding="utf-8"),
                "per-task, owned by mq-agent\n",
                "clean rewrote task-pack.md instead of leaving it alone",
            )
            self.assertTrue(
                (context / "local-notes.md").exists(),
                "clean deleted an unknown file in the target directory",
            )

    def test_clean_still_replaces_the_files_it_owns(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            context = self._seed(root, "mq-agent")

            MODULE.export_repo(repo="mq-agent", output_root=root, clean=True)

            for name in EXPORTED_CONTEXT_FILES:
                self.assertNotEqual(
                    (context / name).read_text(encoding="utf-8"),
                    "stale export\n",
                    f"{name} kept its stale content instead of being regenerated",
                )


class RepoContextExportTests(unittest.TestCase):
    def test_current_blockers_come_from_repo_card(self) -> None:
        card = """# Context Card: mq-agent

## Current blockers

* repo-specific test blocker
"""

        rendered = MODULE.render_current_blockers("mq-agent", card)

        self.assertIn("* repo-specific test blocker", rendered)
        self.assertNotIn("Phase 4 seed", rendered)

    def test_current_blockers_fallback_is_explicit(self) -> None:
        rendered = MODULE.render_current_blockers("mq-agent", "# Context Card: mq-agent\n")

        self.assertIn("No blockers are declared in the source context card.", rendered)
        self.assertIn("Verify live repo state before making runtime or release claims.", rendered)


if __name__ == "__main__":
    unittest.main()
