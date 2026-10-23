"""Phase 12E §9 learn-writeback tests (tracked; tmp paths only).

Acceptance: a promoted memory writes ONE agent-readable file; candidate/observed
write nothing; repeated runs are idempotent; provenance links back to the score id
and promotion event; and no secrets / absolute private paths leak into durable memory.
"""

from __future__ import annotations

import json
from pathlib import Path

import emit_learn_writeback as lw


def _score(memory_id: str, status: str, **over) -> dict:
    rec = {
        "schema": "memory-score.v1",
        "memory_id": memory_id,
        "timestamp": "2026-06-28T12:00:00Z",
        "status": status,
        "score": 1.234,
        "factors": {"frequency": 10, "source_count": 2, "confidence": 0.6, "recency": 0.9,
                    "usage_score": 0, "manual_boost": 0},
        "observed_by": ["mq-agent", "repo-signal"],
        "promoted_at": "2026-06-28",
    }
    rec.update(over)
    return rec


def _obs(key: str, **over) -> dict:
    rec = {
        "schema": "memory-observation.v1",
        "id": f"obs_{key}",
        "timestamp": "2026-06-28T12:00:00Z",
        "producer": "mq-agent",
        "repository": "mq-mcp",
        "category": "pattern",
        "title": "Co-change cluster detected",
        "observation": "When touching bridge.py, also check codegraph_cochange.py.",
        "confidence": 0.6,
        "evidence": [{"source": "bridget/cg-2", "reference": "cochange-run-x"}],
        "tags": ["co-change", "codegraph"],
        "proposed_memory_key": key,
    }
    rec.update(over)
    return rec


def _env(tmp: Path, scores: list[dict], observations: list[dict], events: list[dict] | None = None):
    scores_dir = tmp / "scores"
    scores_dir.mkdir(parents=True, exist_ok=True)
    for s in scores:
        (scores_dir / f"{lw._safe(s['memory_id'])}.json").write_text(json.dumps(s), encoding="utf-8")
    inbox = tmp / "observations"
    inbox.mkdir(parents=True, exist_ok=True)
    with (inbox / "mq-agent.observations.jsonl").open("w", encoding="utf-8") as fh:
        for o in observations:
            fh.write(json.dumps(o) + "\n")
    promotions = tmp / "promotions" / "events.jsonl"
    promotions.parent.mkdir(parents=True, exist_ok=True)
    if events:
        with promotions.open("w", encoding="utf-8") as fh:
            for e in events:
                fh.write(json.dumps(e) + "\n")
    learn = tmp / "learn"
    return dict(scores_dir=scores_dir, inbox_dir=inbox, promotions_path=promotions, learn_dir=learn)


# --- promoted-only ---------------------------------------------------------

def test_promoted_writes_one_file(tmp_path):
    env = _env(tmp_path, [_score("cochange-bridge-py", "promoted")], [_obs("cochange-bridge-py")])
    s = lw.writeback(**env)
    assert s["promoted"] == 1 and s["written"] == 1
    f = env["learn_dir"] / "patterns" / "cochange-bridge-py.md"
    assert f.exists()
    assert "status: promoted" in f.read_text()


def test_candidate_and_observed_write_nothing(tmp_path):
    env = _env(
        tmp_path,
        [_score("k-cand", "candidate"), _score("k-obs", "observed")],
        [_obs("k-cand"), _obs("k-obs")],
    )
    s = lw.writeback(**env)
    assert s["promoted"] == 0 and s["written"] == 0
    assert not (env["learn_dir"]).exists()


def test_category_maps_to_dir(tmp_path):
    env = _env(
        tmp_path,
        [_score("bugfix", "promoted"), _score("archx", "promoted")],
        [_obs("bugfix", category="bug"), _obs("archx", category="architecture")],
    )
    lw.writeback(**env)
    assert (env["learn_dir"] / "fixes" / "bugfix.md").exists()
    assert (env["learn_dir"] / "architecture" / "archx.md").exists()


# --- idempotency -----------------------------------------------------------

def test_repeated_run_is_idempotent(tmp_path):
    env = _env(tmp_path, [_score("cochange-bridge-py", "promoted")], [_obs("cochange-bridge-py")])
    first = lw.writeback(**env)
    f = env["learn_dir"] / "patterns" / "cochange-bridge-py.md"
    content_after_first = f.read_text()
    second = lw.writeback(**env)
    assert first["written"] == 1 and second["written"] == 0 and second["unchanged"] == 1
    assert f.read_text() == content_after_first  # byte-stable, no churn
    assert len(list((env["learn_dir"] / "patterns").glob("*.md"))) == 1  # no duplicate


# --- provenance ------------------------------------------------------------

def test_provenance_records_score_and_event(tmp_path):
    event = {"schema": "promotion-event.v1", "id": "promo_cochange-bridge-py_X",
             "memory_id": "cochange-bridge-py", "from": "candidate", "to": "promoted"}
    env = _env(tmp_path, [_score("cochange-bridge-py", "promoted")], [_obs("cochange-bridge-py")], [event])
    lw.writeback(**env)
    text = (env["learn_dir"] / "patterns" / "cochange-bridge-py.md").read_text()
    assert "source_score_id: cochange-bridge-py" in text
    assert "memory_key: cochange-bridge-py" in text
    assert "promo_cochange-bridge-py_X" in text
    assert "scores/cochange-bridge-py.json" in text


# --- sanitisation ----------------------------------------------------------

def test_secrets_and_abs_paths_are_scrubbed(tmp_path):
    # Built at runtime so no credential-shaped literal sits in the repo.
    fake_token = "gh" + "p_" + "ABCDEFGHIJKLMNOPQRSTUVWXYZ012345"
    dirty = _obs(
        "cochange-bridge-py",
        observation=f"see /Users/example/secret-repo/config and token {fake_token}",
        evidence=[{"source": "repo-signal", "reference": "/Users/example/macos-scripts"}],
    )
    env = _env(tmp_path, [_score("cochange-bridge-py", "promoted")], [dirty])
    lw.writeback(**env)
    text = (env["learn_dir"] / "patterns" / "cochange-bridge-py.md").read_text()
    assert "/Users/example" not in text
    assert fake_token not in text
    assert "[redacted-secret]" in text
    assert "config" in text and "macos-scripts" in text  # basename survives


def test_dry_run_writes_nothing(tmp_path):
    env = _env(tmp_path, [_score("cochange-bridge-py", "promoted")], [_obs("cochange-bridge-py")])
    s = lw.writeback(dry_run=True, **env)
    assert s["written"] == 1 and not env["learn_dir"].exists()
