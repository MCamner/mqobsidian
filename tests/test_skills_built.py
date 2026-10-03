"""Contract tests for the skills-build freshness gate."""
from __future__ import annotations

import importlib.util
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))
SPEC = importlib.util.spec_from_file_location("check_skills_built", SCRIPTS / "check-skills-built.py")
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

BUILT_DIRS = (".claude/skills", ".codex/skills", ".agents/skills")


def build_repo(root: Path, *, skills=("alpha", "beta")) -> None:
    """Write a repo where skills-src and all three built trees agree."""
    for name in skills:
        src = root / "skills-src" / name
        src.mkdir(parents=True)
        (src / "SKILL.md").write_text(f"# {name}\n", encoding="utf-8")
        (src / "reference.md").write_text("detail\n", encoding="utf-8")
        for built in BUILT_DIRS:
            dest = root / built / name
            dest.mkdir(parents=True)
            shutil.copytree(src, dest, dirs_exist_ok=True)


class SkillsBuiltTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)
        build_repo(self.tmp)

    def test_matching_trees_pass(self) -> None:
        self.assertEqual(MODULE.stale_built_skills(self.tmp), [])

    def test_edited_built_copy_is_caught_in_every_location(self) -> None:
        """The likely mistake: editing a built copy instead of the source."""
        for built in BUILT_DIRS:
            (self.tmp / built / "alpha" / "SKILL.md").write_text("# edited\n", encoding="utf-8")
        problems = MODULE.stale_built_skills(self.tmp)
        self.assertEqual(len(problems), 3, problems)
        self.assertTrue(all("SKILL.md differs" in p for p in problems), problems)

    def test_unbuilt_new_skill_is_caught(self) -> None:
        src = self.tmp / "skills-src" / "gamma"
        src.mkdir()
        (src / "SKILL.md").write_text("# gamma\n", encoding="utf-8")
        problems = MODULE.stale_built_skills(self.tmp)
        self.assertEqual(len(problems), 3, problems)
        self.assertTrue(all("gamma was never built" in p for p in problems), problems)

    def test_leftover_built_skill_is_caught(self) -> None:
        """build-skills.sh rm -rf's the trees, so a leftover means a stale build."""
        (self.tmp / ".codex/skills/ghost").mkdir(parents=True)
        problems = MODULE.stale_built_skills(self.tmp)
        self.assertEqual(problems, [".codex/skills/ghost is not in skills-src (renamed or removed)"])

    def test_missing_resource_file_is_caught(self) -> None:
        """A skill is its whole directory, not just SKILL.md."""
        (self.tmp / ".agents/skills/beta/reference.md").unlink()
        problems = MODULE.stale_built_skills(self.tmp)
        self.assertEqual(problems, [".agents/skills/beta: missing reference.md"])

    def test_finder_metadata_in_a_built_copy_is_not_drift(self) -> None:
        """Opening a built skill in Finder writes .DS_Store; no skill content changed."""
        (self.tmp / ".claude/skills/alpha/.DS_Store").write_bytes(b"\0\0\0\1Bud1")
        self.assertEqual(MODULE.stale_built_skills(self.tmp), [])

    def test_finder_metadata_in_a_source_skill_is_not_drift(self) -> None:
        """The same file created after the build must not read as 'missing'."""
        (self.tmp / "skills-src/beta/.DS_Store").write_bytes(b"\0\0\0\1Bud1")
        self.assertEqual(MODULE.stale_built_skills(self.tmp), [])

    def test_a_directory_without_skill_md_is_not_a_source_skill(self) -> None:
        (self.tmp / "skills-src" / "notes").mkdir()
        self.assertEqual(MODULE.source_skills(self.tmp), ["alpha", "beta"])
        self.assertEqual(MODULE.stale_built_skills(self.tmp), [])

    def test_fresh_checkout_with_no_built_trees_is_not_drift(self) -> None:
        """The CI condition, which turned main red before this distinction existed.

        skills-src/ exists there because two source skills are force-added, while
        all three built trees are gitignored and absent. Nothing built means
        nothing to be inconsistent with.
        """
        for built in BUILT_DIRS:
            shutil.rmtree(self.tmp / built.split("/")[0])
        self.assertEqual(MODULE.stale_built_skills(self.tmp), [])

    def test_partially_built_trees_are_drift(self) -> None:
        """Some built and some missing is a real half-finished build."""
        shutil.rmtree(self.tmp / ".codex")
        problems = MODULE.stale_built_skills(self.tmp)
        self.assertEqual(len(problems), 1, problems)
        self.assertIn(".codex/skills is missing while other built trees exist", problems[0])

    def test_absent_source_is_not_a_failure(self) -> None:
        """skills-src/ is gitignored, so CI has almost nothing to compare."""
        empty = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, empty)
        self.assertEqual(MODULE.stale_built_skills(empty), [])

    def test_real_repo_is_in_sync(self) -> None:
        self.assertEqual(MODULE.stale_built_skills(ROOT), [])


if __name__ == "__main__":
    unittest.main()
