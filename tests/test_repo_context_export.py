"""Contract tests for the reference repo-context exporter."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest


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
