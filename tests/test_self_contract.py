"""Contract tests for mqobsidian consuming its own agent contract."""
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


def _load(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / filename)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


AE = _load("agent_entrypoints_mod", "agent_entrypoints.py")
GATE = _load("check_agent_entrypoints", "check-agent-entrypoints.py")
CLEAN = _load("check_clean_checkout", "check-clean-checkout.py")

EXTENSION = "## Local Extension\n\nlocal governance\n"


def _canonical_agents() -> str:
    template = (ROOT / "templates" / "AGENTS.md").read_text(encoding="utf-8")
    return AE.render_agents(template, "mqobsidian")


class AppendExtensionTests(unittest.TestCase):
    def test_extension_cannot_weaken_the_contract(self) -> None:
        """An extension adds; the canonical checks still see the contract."""
        merged = AE.append_extension(_canonical_agents(), EXTENSION)
        self.assertEqual(AE.check_rendered(merged, kind="agents"), [])
        self.assertIn("## Local Extension", merged)

    def test_dropping_a_canonical_section_still_fails(self) -> None:
        stripped = _canonical_agents().replace("## Fallback Rule", "## Fallback")
        merged = AE.append_extension(stripped, EXTENSION)
        self.assertIn(
            "missing canonical section '## Fallback Rule'",
            AE.check_rendered(merged, kind="agents"),
        )

    def test_extension_needs_its_heading(self) -> None:
        with self.assertRaises(ValueError):
            AE.append_extension(_canonical_agents(), "just some prose\n")


class LiveEntrypointTests(unittest.TestCase):
    """The gap: the gate checked renderings and never the live root files."""

    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)

    def test_absent_root_files_are_not_a_failure(self) -> None:
        """AGENTS.md and CLAUDE.md are gitignored, so CI has neither."""
        findings, checked = GATE.check_live_entrypoints(self.tmp)
        self.assertEqual((findings, checked), ([], 0))

    def test_a_non_canonical_root_agents_is_caught(self) -> None:
        (self.tmp / "AGENTS.md").write_text("# hand-written\n", encoding="utf-8")
        findings, checked = GATE.check_live_entrypoints(self.tmp)
        self.assertEqual(checked, 1)
        self.assertTrue(any("missing canonical section" in f for f in findings), findings)
        self.assertTrue(all(f.startswith("AGENTS.md: ") for f in findings), findings)

    def test_a_root_claude_without_the_include_is_caught(self) -> None:
        (self.tmp / "CLAUDE.md").write_text(
            f"<!-- {AE.LINEAGE_MARKER} -->\n\n# CLAUDE.md\n", encoding="utf-8"
        )
        findings, _ = GATE.check_live_entrypoints(self.tmp)
        self.assertEqual(findings, ["CLAUDE.md: CLAUDE.md must include '@AGENTS.md' to inherit canonical sections"])

    def test_this_repo_passes_its_own_contract(self) -> None:
        """No repo-name exemption: mqobsidian is the first consumer."""
        findings, checked = GATE.check_live_entrypoints(ROOT)
        self.assertEqual(findings, [])
        if checked:
            agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
            for section in AE.CANONICAL_SECTIONS:
                self.assertIn(section, agents)
            for canary in AE.CANONICAL_CANARIES:
                self.assertIn(canary, agents)
            self.assertIn(AE.LINEAGE_MARKER, agents)
            self.assertIn(AE.EXTENSION_HEADING, agents)


class CleanCheckoutTests(unittest.TestCase):
    def test_a_non_repo_is_skipped(self) -> None:
        empty = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, empty)
        code, output = CLEAN.run_suite_on_clean_checkout(empty)
        self.assertNotEqual(code, 0)
        self.assertIn("git archive failed", output)


if __name__ == "__main__":
    unittest.main()
