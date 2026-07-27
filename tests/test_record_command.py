from __future__ import annotations

import importlib.util
import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "record_command.py"
SPEC = importlib.util.spec_from_file_location("record_command", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
rc = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(rc)


def _patterns(tmp_path: Path) -> Path:
    path = tmp_path / "patterns.jsonl"
    path.write_text(
        json.dumps(
            {
                "id": "repo-quick-state",
                "name": "Repo quick state",
                "status": "active",
                "risk_class": "read-only",
                "task_tags": ["repo-inspect"],
            }
        )
        + "\n",
        encoding="utf-8",
    )
    return path


def _argv(tmp_path: Path, *extra: str) -> list[str]:
    return [
        "repo-quick-state",
        "--command",
        "git status --short",
        "--sanitized-command",
        "git status --short",
        "--agent",
        "codex",
        "--repo",
        "mqobsidian",
        "--task-type",
        "repo-inspect",
        "--outcome",
        "worked",
        "--risk-class",
        "read-only",
        "--session-ref",
        "session-123",
        "--patterns",
        str(_patterns(tmp_path)),
        "--inbox",
        str(tmp_path / "observations.jsonl"),
        *extra,
    ]


class RecordCommandTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self.temporary_directory.name)

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def test_dry_run_validates_without_writing(self) -> None:
        output = io.StringIO()
        with redirect_stdout(output):
            result = rc.main([*_argv(self.tmp_path), "--dry-run"])

        self.assertEqual(result, 0)
        self.assertFalse((self.tmp_path / "observations.jsonl").exists())
        record = json.loads(output.getvalue())
        self.assertEqual(record["pattern_id"], "repo-quick-state")
        self.assertFalse(record["promote_candidate"])

    def test_append_writes_one_compact_jsonl_record(self) -> None:
        result = rc.main(_argv(self.tmp_path, "--note", "Useful preflight."))

        self.assertEqual(result, 0)
        rows = [
            json.loads(line)
            for line in (self.tmp_path / "observations.jsonl")
            .read_text(encoding="utf-8")
            .splitlines()
        ]
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["note"], "Useful preflight.")

    def test_unknown_pattern_is_rejected(self) -> None:
        argv = _argv(self.tmp_path)
        argv[0] = "made-up"
        errors = io.StringIO()

        with redirect_stderr(errors):
            result = rc.main(argv)

        self.assertEqual(result, 2)
        self.assertFalse((self.tmp_path / "observations.jsonl").exists())
        self.assertIn("unknown pattern_id", errors.getvalue())

    def test_pattern_contract_mismatch_is_rejected(self) -> None:
        argv = _argv(self.tmp_path)
        argv[argv.index("repo-inspect")] = "validate"
        errors = io.StringIO()

        with redirect_stderr(errors):
            result = rc.main(argv)

        self.assertEqual(result, 2)
        self.assertIn("task_type", errors.getvalue())

    def test_raw_command_requires_explicit_sanitized_form(self) -> None:
        argv = _argv(self.tmp_path)
        index = argv.index("--sanitized-command")
        del argv[index : index + 2]
        errors = io.StringIO()

        with redirect_stderr(errors), self.assertRaises(SystemExit) as raised:
            rc.main(argv)

        self.assertEqual(raised.exception.code, 2)
        self.assertIn("sanitized-command", errors.getvalue())


if __name__ == "__main__":
    unittest.main()
