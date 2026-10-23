"""build_views CLI — asking for help must not render views (tracked; tmp paths only)."""

from __future__ import annotations

import json

import build_views as bv
import pytest


@pytest.fixture
def isolated(tmp_path, monkeypatch):
    patterns = tmp_path / "patterns.jsonl"
    patterns.write_text(json.dumps({"id": "p1", "repo_scope": "generic", "risk_class": "read-only"}) + "\n",
                        encoding="utf-8")
    monkeypatch.setattr(bv, "PATTERNS", patterns)
    monkeypatch.setattr(bv, "OBSERVATIONS", tmp_path / "observations.jsonl")
    monkeypatch.setattr(bv, "VIEWS", tmp_path / "views")
    monkeypatch.setattr(bv, "MQLAUNCH", tmp_path / "mqlaunch")
    return tmp_path


@pytest.mark.parametrize("argv, code", [(["--help"], 0), (["--bogus"], 2)])
def test_flags_do_not_render(isolated, argv, code):
    with pytest.raises(SystemExit) as exit_info:
        bv.main(argv)
    assert exit_info.value.code == code
    assert not (isolated / "views").exists()
    assert not (isolated / "mqlaunch").exists()


def test_no_arguments_still_renders(isolated):
    assert bv.main([]) == 0
    assert (isolated / "views" / "top-reusable.md").exists()
