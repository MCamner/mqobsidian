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


def _snapshot(directory: Path) -> dict[str, str | None]:
    """Map every name in the directory to its content, for before/after comparison."""
    return {
        entry.name: entry.read_text(encoding="utf-8")
        for entry in sorted(directory.iterdir())
        if entry.is_file()
    }


class ExportOwnershipInvariantTests(unittest.TestCase):
    """An export run may only touch names in `EXPORTED_CONTEXT_FILES`.

    Asserted over the whole directory rather than per known file, because
    `--output-dir` can point at a live repo whose `.mq/context` holds files this
    exporter has never heard of. A per-file test protects the files someone
    thought of; the invariant protects the contract, including names added
    later.

    This is also the guard against the defect's root cause: the five owned
    filenames were duplicated in `outputs` while `EXPORTED_CONTEXT_FILES` sat
    unused, so contract and implementation could drift silently.
    """

    def _seed_foreign_files(self, root: Path, repo: str) -> Path:
        context = root / repo / ".mq" / "context"
        context.mkdir(parents=True)
        (context / "task-pack.md").write_text("per-task, owned by mq-agent\n", encoding="utf-8")
        (context / "local-notes.md").write_text("unknown file\n", encoding="utf-8")
        (context / "future-surface.json").write_text('{"not": "ours"}\n', encoding="utf-8")
        return context

    def _assert_only_owned_changed(
        self, before: dict[str, str | None], after: dict[str, str | None]
    ) -> None:
        owned = set(EXPORTED_CONTEXT_FILES)
        for name in set(before) | set(after):
            if name in owned:
                continue
            self.assertIn(name, after, f"export deleted {name}, which it does not own")
            self.assertIn(name, before, f"export created {name}, which is not in the contract")
            self.assertEqual(
                before[name], after[name], f"export modified {name}, which it does not own"
            )

    def test_export_touches_only_owned_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            context = self._seed_foreign_files(root, "mq-agent")
            before = _snapshot(context)

            MODULE.export_repo(repo="mq-agent", output_root=root, clean=False)

            self._assert_only_owned_changed(before, _snapshot(context))

    def test_clean_export_touches_only_owned_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            context = self._seed_foreign_files(root, "mq-agent")
            for name in EXPORTED_CONTEXT_FILES:
                (context / name).write_text("stale\n", encoding="utf-8")
            before = _snapshot(context)

            MODULE.export_repo(repo="mq-agent", output_root=root, clean=True)

            self._assert_only_owned_changed(before, _snapshot(context))

    def test_written_set_is_exactly_the_ownership_contract(self) -> None:
        # Kills the duplicated truth directly: if `outputs` gains or loses a file
        # without the contract list following, this fails.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            written = MODULE.export_repo(repo="mq-agent", output_root=root)

            self.assertEqual(
                sorted(path.name for path in written),
                sorted(EXPORTED_CONTEXT_FILES),
                "the files the exporter writes have drifted from EXPORTED_CONTEXT_FILES",
            )


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
