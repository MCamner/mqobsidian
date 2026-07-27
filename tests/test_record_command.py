from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "record_command.py"
SPEC = importlib.util.spec_from_file_location("record_command", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
rc = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(rc)


def _patterns(tmp_path):
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


def _argv(tmp_path, *extra: str) -> list[str]:
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


def test_dry_run_validates_without_writing(tmp_path, capsys):
    assert rc.main([*_argv(tmp_path), "--dry-run"]) == 0
    assert not (tmp_path / "observations.jsonl").exists()
    record = json.loads(capsys.readouterr().out)
    assert record["pattern_id"] == "repo-quick-state"
    assert record["promote_candidate"] is False


def test_append_writes_one_compact_jsonl_record(tmp_path):
    assert rc.main(_argv(tmp_path, "--note", "Useful preflight.")) == 0
    rows = [
        json.loads(line)
        for line in (tmp_path / "observations.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    assert len(rows) == 1
    assert rows[0]["note"] == "Useful preflight."


def test_unknown_pattern_is_rejected(tmp_path, capsys):
    argv = _argv(tmp_path)
    argv[0] = "made-up"
    assert rc.main(argv) == 2
    assert not (tmp_path / "observations.jsonl").exists()
    assert "unknown pattern_id" in capsys.readouterr().err


def test_pattern_contract_mismatch_is_rejected(tmp_path, capsys):
    argv = _argv(tmp_path)
    argv[argv.index("repo-inspect")] = "validate"
    assert rc.main(argv) == 2
    assert "task_type" in capsys.readouterr().err


def test_raw_command_requires_explicit_sanitized_form(tmp_path, capsys):
    argv = _argv(tmp_path)
    index = argv.index("--sanitized-command")
    del argv[index : index + 2]
    with pytest.raises(SystemExit) as exc:
        rc.main(argv)
    assert exc.value.code == 2
    assert "sanitized-command" in capsys.readouterr().err
