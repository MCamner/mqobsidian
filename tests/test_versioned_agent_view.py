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


def problems(system: str, source_text: str, view_text: str) -> list[str]:
    """`source_text` is the system's hot.md and index.md, concatenated."""
    found: list[str] = []
    if not VERSIONED_RE.search(source_text):
        found.append(f"systems/{system}/ does not declare agent_view: versioned")
    match = SOURCES_RE.search(view_text)
    sources = [s.strip() for s in match.group(1).split(",")] if match else []
    if not sources:
        found.append(f"the {system} view lists no sources")
    for source in sources:
        if not source.startswith(f"systems/{system}/"):
            found.append(f"the {system} view cites an uncommitted source: {source}")
    return found


def _read(rel: str) -> str:
    path = ROOT / rel
    return path.read_text(encoding="utf-8") if path.is_file() else ""


class VersionedAgentViewTest(unittest.TestCase):
    def test_the_front_door_view_is_tracked(self) -> None:
        self.assertIn("memory/learn/agent/mqobsidian.md", tracked_views())

    def test_every_tracked_view_is_built_from_committed_sources(self) -> None:
        for rel in tracked_views():
            system = Path(rel).stem
            with self.subTest(view=rel):
                sources = _read(f"systems/{system}/hot.md") + _read(f"systems/{system}/index.md")
                self.assertEqual(problems(system, sources, _read(rel)), [])

    def test_tracked_views_without_git_lists_the_export(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "memory/learn/agent").mkdir(parents=True)
            (root / "memory/learn/agent/mqobsidian.md").write_text("x\n", encoding="utf-8")
            self.assertEqual(tracked_views(root), ["memory/learn/agent/mqobsidian.md"])

    def test_a_view_citing_local_lessons_is_rejected(self) -> None:
        view = "sources: [systems/mqobsidian/hot.md, memory/learn/repos/mqobsidian.md]\n"
        found = problems("mqobsidian", "agent_view: versioned\n", view)
        self.assertEqual(
            found,
            ["the mqobsidian view cites an uncommitted source: memory/learn/repos/mqobsidian.md"],
        )

    def test_an_unmarked_system_is_rejected(self) -> None:
        view = "sources: [systems/mqobsidian/hot.md]\n"
        found = problems("mqobsidian", "type: hot-cache\n", view)
        self.assertEqual(
            found, ["systems/mqobsidian/ does not declare agent_view: versioned"]
        )


if __name__ == "__main__":
    unittest.main()
