import importlib.util
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check-context-links.py"
SPEC = importlib.util.spec_from_file_location("check_context_links", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ContextLinksTest(unittest.TestCase):
    def test_reports_missing_front_door(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            for rel_path in MODULE.REQUIRED_FRONT_DOORS[1:]:
                path = root / rel_path
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("ok\n", encoding="utf-8")

            self.assertEqual(
                MODULE.missing_front_doors(root),
                ["memory/learn/agent/mqobsidian.md"],
            )

    def test_accepts_complete_front_door_chain(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            for rel_path in MODULE.REQUIRED_FRONT_DOORS:
                path = root / rel_path
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("ok\n", encoding="utf-8")

            self.assertEqual(MODULE.missing_front_doors(root), [])


if __name__ == "__main__":
    unittest.main()
