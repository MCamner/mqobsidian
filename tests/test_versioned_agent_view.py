"""A committed agent view may only be built from committed sources (DEC-007).

`memory/learn/repos/` is gitignored, so a tracked view that cited it, or one
built for a system whose hot.md/index.md lacks `agent_view: versioned`, could
not be reproduced from a clean clone. Byte-for-byte reproduction needs the generator
(mq-agent) and runs as a CI step; this test is the local guard that needs
nothing but the repo.
"""

import re
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCES_RE = re.compile(r"^sources:\s*\[(.*)\]\s*$", re.MULTILINE)
VERSIONED_RE = re.compile(r"^agent_view:\s*versioned\s*$", re.MULTILINE)


def tracked_views(root: Path = ROOT) -> list[str]:
    if not (root / ".git").exists():
        # A `git archive` export (the clean-checkout gate) has no .git; every
        # file in it is tracked by construction.
        return sorted(
            p.relative_to(root).as_posix() for p in (root / "memory/learn/agent").glob("*.md")
        )
    out = subprocess.run(
        ["git", "ls-files", "memory/learn/agent/*.md"],
        cwd=root,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    return [line for line in out.splitlines() if line]


def _allowed_sources(system: str) -> tuple[str, str]:
    return (f"systems/{system}/hot.md", f"systems/{system}/index.md")


def problems(system: str, index_text: str, view_text: str, present: set[str]) -> list[str]:
    """`present` is the set of the system's hot.md/index.md paths that exist."""
    found: list[str] = []
    if not VERSIONED_RE.search(index_text):
        found.append(f"systems/{system}/index.md does not declare agent_view: versioned")
    match = SOURCES_RE.search(view_text)
    sources = [s.strip() for s in match.group(1).split(",")] if match else []
    if not sources:
        found.append(f"the {system} view lists no sources")
    for source in sources:
        if source not in _allowed_sources(system):
            found.append(f"the {system} view cites an uncommitted source: {source}")
        elif source not in present:
            found.append(f"the {system} view cites a missing source: {source}")
    return found


def _read(root: Path, rel: str) -> str:
    path = root / rel
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def root_problems(root: Path = ROOT) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    for rel in tracked_views(root):
        system = Path(rel).stem
        present = {s for s in _allowed_sources(system) if (root / s).is_file()}
        index = _read(root, f"systems/{system}/index.md")
        result[rel] = problems(system, index, _read(root, rel), present)
    return result


GOOD_VIEW = "sources: [systems/mqobsidian/hot.md, systems/mqobsidian/index.md]\n"


class VersionedAgentViewTest(unittest.TestCase):
    def test_the_front_door_view_is_tracked(self) -> None:
        self.assertIn("memory/learn/agent/mqobsidian.md", tracked_views())

    def test_every_tracked_view_is_built_from_committed_sources(self) -> None:
        for rel, found in root_problems().items():
            with self.subTest(view=rel):
                self.assertEqual(found, [])

    def test_tracked_views_without_git_lists_the_export(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "memory/learn/agent").mkdir(parents=True)
            (root / "memory/learn/agent/mqobsidian.md").write_text("x\n", encoding="utf-8")
            self.assertEqual(tracked_views(root), ["memory/learn/agent/mqobsidian.md"])

    def test_a_view_citing_local_lessons_is_rejected(self) -> None:
        view = "sources: [systems/mqobsidian/hot.md, memory/learn/repos/mqobsidian.md]\n"
        found = problems(
            "mqobsidian", "agent_view: versioned\n", view, {"systems/mqobsidian/hot.md"}
        )
        self.assertEqual(
            found,
            ["the mqobsidian view cites an uncommitted source: memory/learn/repos/mqobsidian.md"],
        )

    def _export(self, tmp: str, view: str, hot: str, index: str) -> Path:
        root = Path(tmp)
        (root / "memory/learn/agent").mkdir(parents=True)
        (root / "systems/mqobsidian").mkdir(parents=True)
        (root / "memory/learn/agent/mqobsidian.md").write_text(view, encoding="utf-8")
        if hot:
            (root / "systems/mqobsidian/hot.md").write_text(hot, encoding="utf-8")
        if index:
            (root / "systems/mqobsidian/index.md").write_text(index, encoding="utf-8")
        return root

    def test_a_valid_export_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = self._export(tmp, GOOD_VIEW, "type: hot-cache\n", "agent_view: versioned\n")
            self.assertEqual(root_problems(root), {"memory/learn/agent/mqobsidian.md": []})

    def test_an_invalid_exported_view_is_still_rejected(self) -> None:
        view = "sources: [systems/mqobsidian/hot.md, memory/learn/repos/mqobsidian.md]\n"
        with tempfile.TemporaryDirectory() as tmp:
            root = self._export(tmp, view, "type: hot-cache\n", "agent_view: versioned\n")
            self.assertEqual(
                root_problems(root)["memory/learn/agent/mqobsidian.md"],
                ["the mqobsidian view cites an uncommitted source: memory/learn/repos/mqobsidian.md"],
            )

    def test_the_marker_must_be_in_index_md(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = self._export(tmp, GOOD_VIEW, "agent_view: versioned\n", "type: index\n")
            self.assertEqual(
                root_problems(root)["memory/learn/agent/mqobsidian.md"],
                ["systems/mqobsidian/index.md does not declare agent_view: versioned"],
            )

    def test_a_source_other_than_hot_or_index_is_rejected(self) -> None:
        view = "sources: [systems/mqobsidian/notes.md]\n"
        found = problems("mqobsidian", "agent_view: versioned\n", view, set())
        self.assertEqual(
            found,
            ["the mqobsidian view cites an uncommitted source: systems/mqobsidian/notes.md"],
        )

    def test_a_missing_source_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = self._export(tmp, GOOD_VIEW, "", "agent_view: versioned\n")
            self.assertEqual(
                root_problems(root)["memory/learn/agent/mqobsidian.md"],
                ["the mqobsidian view cites a missing source: systems/mqobsidian/hot.md"],
            )

    def test_an_unmarked_system_is_rejected(self) -> None:
        view = "sources: [systems/mqobsidian/hot.md]\n"
        found = problems("mqobsidian", "type: index\n", view, {"systems/mqobsidian/hot.md"})
        self.assertEqual(
            found, ["systems/mqobsidian/index.md does not declare agent_view: versioned"]
        )


if __name__ == "__main__":
    unittest.main()
