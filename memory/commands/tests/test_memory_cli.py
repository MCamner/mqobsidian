"""`mqobsidian memory` CLI — operator control-plane tests (tracked; tmp paths only).

The scoring POLICY is covered by test_generic_score; here we test the CONTROL PLANE:
  - `score --dry-run` writes nothing; `score --apply` persists
  - `status` reports the tier tally
  - `explain` gives a per-memory rationale (and fails cleanly on unknown ids)
  - `quarantine` lists the review queues
  - everything is read-only except `score --apply`
"""

from __future__ import annotations

import json
from pathlib import Path

import memory_cli as cli


def _obs(**over) -> dict:
    rec = {
        "schema": "memory-observation.v1",
        "id": "obs_1",
        "timestamp": "2026-06-28T12:00:00Z",
        "producer": "mq-agent",
        "repository": "mq-mcp",
        "category": "pattern",
        "title": "Co-change cluster detected",
        "observation": "When touching bridge.py, also check codegraph_cochange.py.",
        "confidence": 0.6,
        # Non-co-change source so the control-plane tests exercise the frequency policy
        # (single obs → observed); co-change's single-shot policy is tested in test_generic_score.
        "evidence": [{"source": "repo-signal", "reference": "run-x"}],
        "proposed_memory_key": "cochange-bridge-py",
    }
    rec.update(over)
    return rec


def _inbox(tmp: Path, records: list[dict]) -> Path:
    d = tmp / "observations"
    d.mkdir(parents=True, exist_ok=True)
    with (d / "mq-agent.observations.jsonl").open("w", encoding="utf-8") as fh:
        for r in records:
            fh.write(json.dumps(r) + "\n")
    return d


def _args(inbox: Path, out: Path, tmp: Path, *extra: str) -> list[str]:
    return [*extra, "--inbox", str(inbox), "--out", str(out), "--feedback", str(tmp / "none.jsonl")]


def test_score_dry_run_writes_nothing(tmp_path, capsys):
    inbox = _inbox(tmp_path, [_obs()])
    out = tmp_path / "out"
    rc = cli.main(["score", "--dry-run", *_args(inbox, out, tmp_path)])
    assert rc == 0
    assert not (out / "scores").exists()
    text = capsys.readouterr().out
    assert "dry-run" in text and "observed:     1" in text


def test_score_apply_writes_scores(tmp_path, capsys):
    inbox = _inbox(tmp_path, [_obs()])
    out = tmp_path / "out"
    rc = cli.main(["score", "--apply", *_args(inbox, out, tmp_path)])
    assert rc == 0
    assert list((out / "scores").glob("*.json"))
    assert "scores written: 1" in capsys.readouterr().out


def test_status_shows_counts(tmp_path, capsys):
    inbox = _inbox(tmp_path, [_obs()])
    out = tmp_path / "out"
    rc = cli.main(["status", *_args(inbox, out, tmp_path)])
    assert rc == 0
    text = capsys.readouterr().out
    assert "memories:     1" in text and "observed:     1" in text


def test_status_json_is_machine_readable(tmp_path, capsys):
    """mq-agent review-status --json forwards this; the shape is the contract."""
    inbox = _inbox(tmp_path, [_obs()])
    out = tmp_path / "out"
    rc = cli.main(["status", "--json", *_args(inbox, out, tmp_path)])
    assert rc == 0
    doc = json.loads(capsys.readouterr().out)
    assert doc["schema"] == "mqobsidian.memory-status.v1"
    assert doc["observations"] == {"total": 1, "valid": 1, "invalid": 0}
    assert doc["memories"] == 1
    assert doc["tiers"] == {"observed": 1, "candidate": 0, "promoted": 0, "deprecated": 0}
    assert doc["held"] == {"total": 0, "conflicting": 0, "risky": 0,
                           "superseding": 0, "promotion-review": 0}
    assert doc["quarantined"] == 0 and doc["tier_changes"] == 0


def test_status_json_counts_held_review_queue(tmp_path, capsys):
    inbox = _inbox(tmp_path, [_obs(id="cc1", workflow="co-change", confidence=0.7,
                                   evidence=[{"source": "bridget/cg-2", "reference": "r"}],
                                   proposed_memory_key="cochange-x")])
    out = tmp_path / "out"
    cli.main(["status", "--json", *_args(inbox, out, tmp_path)])
    held = json.loads(capsys.readouterr().out)["held"]
    assert held["promotion-review"] == 1 and held["total"] == 1


def test_explain_known_memory(tmp_path, capsys):
    inbox = _inbox(tmp_path, [_obs()])
    out = tmp_path / "out"
    rc = cli.main(["explain", "cochange-bridge-py", *_args(inbox, out, tmp_path)])
    assert rc == 0
    text = capsys.readouterr().out
    assert "status: observed" in text
    assert "ebms_state: scratch" in text
    assert "frequency: 1" in text
    assert "below the candidate bar" in text  # rationale explains why it's only observed


def test_explain_unknown_memory_returns_1(tmp_path, capsys):
    inbox = _inbox(tmp_path, [_obs()])
    out = tmp_path / "out"
    rc = cli.main(["explain", "does-not-exist", *_args(inbox, out, tmp_path)])
    assert rc == 1
    assert "unknown memory_id" in capsys.readouterr().err


def test_quarantine_lists_invalid(tmp_path, capsys):
    inbox = _inbox(tmp_path, [{"schema": "memory-observation.v1", "id": "bad", "confidence": 9}])
    out = tmp_path / "out"
    rc = cli.main(["quarantine", *_args(inbox, out, tmp_path)])
    assert rc == 0
    text = capsys.readouterr().out
    assert "invalid (1)" in text and "conflicting (0)" in text and "risky (0)" in text


# --- learn-writeback command ----------------------------------------------

def _score_record(memory_id: str, status: str) -> dict:
    return {
        "schema": "memory-score.v1", "memory_id": memory_id, "timestamp": "2026-06-28T12:00:00Z",
        "status": status, "score": 1.2,
        "factors": {"frequency": 10, "source_count": 2, "confidence": 0.6, "recency": 0.9,
                    "usage_score": 0, "manual_boost": 0},
        "observed_by": ["mq-agent"], "promoted_at": "2026-06-28",
    }


def _lw_env(tmp_path, status: str):
    """Set up out/scores + inbox so the CLI's learn-writeback has a memory of `status`."""
    inbox = _inbox(tmp_path, [_obs()])
    out = tmp_path / "out"
    scores = out / "scores"
    scores.mkdir(parents=True, exist_ok=True)
    (scores / "cochange-bridge-py.json").write_text(json.dumps(_score_record("cochange-bridge-py", status)))
    learn = tmp_path / "learn"
    args = [*_args(inbox, out, tmp_path), "--learn-dir", str(learn)]
    return out, learn, args


def test_learn_writeback_dry_run_shows_promoted_writes_nothing(tmp_path, capsys):
    out, learn, args = _lw_env(tmp_path, "promoted")
    rc = cli.main(["learn-writeback", "--dry-run", *args])
    assert rc == 0
    assert not learn.exists()
    text = capsys.readouterr().out
    assert "dry-run" in text and "promoted memories: 1" in text
    assert "[patterns] learn/patterns/cochange-bridge-py.md" in text and "would-write" in text


def test_learn_writeback_apply_writes_promoted(tmp_path, capsys):
    out, learn, args = _lw_env(tmp_path, "promoted")
    rc = cli.main(["learn-writeback", "--apply", *args])
    assert rc == 0
    f = learn / "patterns" / "cochange-bridge-py.md"
    assert f.exists() and "source_score_id: cochange-bridge-py" in f.read_text()
    assert "wrote: 1" in capsys.readouterr().out


def test_learn_writeback_skips_candidate(tmp_path, capsys):
    out, learn, args = _lw_env(tmp_path, "candidate")
    rc = cli.main(["learn-writeback", "--apply", *args])
    assert rc == 0
    assert not learn.exists()
    assert "promoted memories: 0" in capsys.readouterr().out


def test_learn_writeback_apply_is_idempotent(tmp_path, capsys):
    out, learn, args = _lw_env(tmp_path, "promoted")
    cli.main(["learn-writeback", "--apply", *args])
    capsys.readouterr()
    cli.main(["learn-writeback", "--apply", *args])
    assert "unchanged: 1" in capsys.readouterr().out
    assert len(list((learn / "patterns").glob("*.md"))) == 1


# --- score --writeback-promoted (chain scoring + learn-writeback in one run) ---
# (_gp — generic promotable observation under key gen-x — is defined below,
# shared with the resolve-supersede tests.)

def _promote_env(tmp_path):
    """An inbox that promotes gen-x; returns (out, learn, args) with a --learn-dir."""
    out = tmp_path / "out"
    (tmp_path / "none.jsonl").write_text(json.dumps({"pattern_id": "gen-x", "outcome": "helped"}) + "\n")
    orig = [_gp("repo-signal", i) for i in range(5)] + [_gp("command-bus", i) for i in range(5)]
    inbox = _inbox(tmp_path, orig)
    learn = tmp_path / "learn"
    args = [*_args(inbox, out, tmp_path), "--learn-dir", str(learn)]
    return out, learn, args


def test_score_writeback_promoted_writes_scores_and_learn(tmp_path, capsys):
    out, learn, args = _promote_env(tmp_path)
    rc = cli.main(["score", "--apply", "--writeback-promoted", *args])
    assert rc == 0
    assert list((out / "scores").glob("*.json"))          # scoring persisted
    assert (learn / "patterns" / "gen-x.md").exists()      # promoted → learn file written
    text = capsys.readouterr().out
    assert "scores written: " in text and "Learn-writeback" in text and "wrote: 1" in text


def test_score_writeback_promoted_dry_run_writes_nothing(tmp_path, capsys):
    out, learn, args = _promote_env(tmp_path)
    rc = cli.main(["score", "--dry-run", "--writeback-promoted", *args])
    assert rc == 0
    assert not (out / "scores").exists()
    assert not learn.exists()
    text = capsys.readouterr().out
    assert "dry-run" in text and "Learn-writeback" in text


def test_score_without_flag_does_not_writeback(tmp_path, capsys):
    out, learn, args = _promote_env(tmp_path)
    rc = cli.main(["score", "--apply", *args])
    assert rc == 0
    assert not learn.exists()                              # no writeback unless flag set
    assert "Learn-writeback" not in capsys.readouterr().out


# --- promote-from-review (action the co-change promotion-review queue) ------

def _cc(**over) -> dict:
    """A strong single-shot co-change observation → lands in the promotion-review queue."""
    rec = _obs(id="cc1", workflow="co-change", confidence=0.7,
               evidence=[{"source": "bridget/cg-2", "reference": "r"}],
               proposed_memory_key="cochange-x")
    rec.update(over)
    return rec


def test_promote_from_review_apply_promotes_and_holds(tmp_path, capsys):
    inbox = _inbox(tmp_path, [_cc()])
    out = tmp_path / "out"
    args = _args(inbox, out, tmp_path)
    rc = cli.main(["promote-from-review", "cochange-x", "--apply", *args])
    assert rc == 0
    ev = json.loads((out / "promotions" / "events.jsonl").read_text().strip().splitlines()[-1])
    assert ev["to"] == "promoted" and ev["memory_id"] == "cochange-x"
    assert (out / "promoted-content" / "cochange-x.json").exists()
    # follow-up: promoted and NOT bogusly superseded (authority-block fix)
    capsys.readouterr()
    cli.main(["status", *args])
    text = capsys.readouterr().out
    assert "promoted:     1" in text and "superseding: 0" in text


def test_promote_from_review_dry_run_writes_nothing(tmp_path, capsys):
    inbox = _inbox(tmp_path, [_cc()])
    out = tmp_path / "out"
    rc = cli.main(["promote-from-review", "cochange-x", *_args(inbox, out, tmp_path)])
    assert rc == 0
    assert not (out / "promotions").exists()
    assert "dry-run" in capsys.readouterr().out


def test_promote_from_review_not_in_queue_returns_1(tmp_path, capsys):
    inbox = _inbox(tmp_path, [_cc(confidence=0.1)])  # weak → observed, not queued
    out = tmp_path / "out"
    rc = cli.main(["promote-from-review", "cochange-x", "--apply", *_args(inbox, out, tmp_path)])
    assert rc == 1
    assert "not in the promotion-review queue" in capsys.readouterr().err


# --- resolve-supersede (action the deep-conflict queue) ---------------------

def _gp(producer: str, i: int, *, text: str | None = None, ts: str = "2026-06-28T12:00:00Z") -> dict:
    """A generic (non-co-change) promotable observation under key gen-x."""
    over = {"id": f"{producer}{i}", "producer": producer, "proposed_memory_key": "gen-x", "timestamp": ts}
    if text is not None:
        over["observation"] = text
    return _obs(**over)  # _obs default evidence source is repo-signal → generic policy


def _promoted_then_drifted(tmp_path):
    """Promote gen-x, then introduce drifting evidence; returns (out, args)."""
    out = tmp_path / "out"
    (tmp_path / "none.jsonl").write_text(json.dumps({"pattern_id": "gen-x", "outcome": "helped"}) + "\n")
    orig = [_gp("repo-signal", i) for i in range(5)] + [_gp("command-bus", i) for i in range(5)]
    inbox = _inbox(tmp_path, orig)
    args = _args(inbox, out, tmp_path)
    cli.main(["score", "--apply", *args])  # promote gen-x + snapshot
    _inbox(tmp_path, orig + [_gp("repo-signal", 99, text="Do the opposite now.", ts="2026-06-29T12:00:00Z")])
    return out, args


def test_resolve_supersede_accept_adopts_new_directive(tmp_path, capsys):
    out, args = _promoted_then_drifted(tmp_path)
    rc = cli.main(["resolve-supersede", "gen-x", "--accept", "--apply", *args])
    assert rc == 0
    capsys.readouterr()
    cli.main(["status", *args])
    assert "superseding: 0" in capsys.readouterr().out  # snapshot updated → conflict cleared


def test_resolve_supersede_reject_suppresses(tmp_path, capsys):
    out, args = _promoted_then_drifted(tmp_path)
    rc = cli.main(["resolve-supersede", "gen-x", "--reject", "--apply", *args])
    assert rc == 0
    assert (out / "review" / "supersede-resolved.jsonl").exists()
    capsys.readouterr()
    cli.main(["status", *args])
    assert "superseding: 0" in capsys.readouterr().out  # suppressed; memory stays promoted


def test_resolve_supersede_unknown_returns_1(tmp_path, capsys):
    inbox = _inbox(tmp_path, [_obs()])
    out = tmp_path / "out"
    rc = cli.main(["resolve-supersede", "nope", "--reject", "--apply", *_args(inbox, out, tmp_path)])
    assert rc == 1
    assert "no open supersede proposal" in capsys.readouterr().err


# --- the five locked transition verbs (v1.22 Task 5) ------------------------
#
# The state machine itself is covered by test_transition_journal; here we test
# the CONTROL PLANE: preview vs apply, refusal, and what happens to published
# truth when the rebuild that must follow an applied transition fails.

MEM_ID = "cochange-bridge-py"


def _seed_transition(tmp_path, state: str = "candidate") -> tuple[Path, list[str]]:
    """A scored memory in `state`, published evidence, and a built export bundle."""
    inbox = _inbox(tmp_path, [_obs()])
    out = tmp_path / "out"
    scores = out / "scores"
    scores.mkdir(parents=True)
    (scores / f"{MEM_ID}.json").write_text(json.dumps({
        "schema": "memory-score.v1", "memory_id": MEM_ID,
        "timestamp": "2026-07-16T00:00:00Z", "status": state, "score": 0.81,
        "factors": {"frequency": 1.0, "source_count": 2.0, "confidence": 0.6,
                    "recency": 1.0, "usage_score": 0.0, "manual_boost": 0.0},
        "observed_by": ["repo-signal"], "feedback": {"positive": 1, "negative": 0},
        "first_seen": "2026-07-01", "last_seen": "2026-07-15",
    }, indent=2), encoding="utf-8")

    policy = tmp_path / "promotion-policy.json"
    policy.write_text(json.dumps({
        "schema": "promotion-policy.v1", "source": "mqobsidian",
        "generated_at": "2026-07-16T00:00:00Z",
        "weights": {"frequency": 0.15, "source_count": 0.2, "confidence": 0.25,
                    "recency": 0.15, "usage_score": 0.2, "manual_boost": 0.05},
        "review_threshold": 0.55, "auto_threshold": 0.8,
        "min_supporting_factors": 2, "block_negative_feedback": True,
        "max_manifest_age_seconds": 86400,
    }), encoding="utf-8")

    exports = tmp_path / "exports"
    exports.mkdir()
    builder = cli._builder()
    builder.SCORES_DIR, builder.OBSERVATIONS_DIR = scores, inbox
    builder.POLICY_SOURCE, builder.EXPORTS = policy, exports
    assert builder.rebuild() == []

    args = [
        "--inbox", str(inbox), "--out", str(out), "--feedback", str(tmp_path / "none.jsonl"),
        "--learn-dir", str(tmp_path / "learn"), "--exports", str(exports),
        "--policy", str(policy),
    ]
    return out, args


def _run(capsys, argv: list[str]) -> tuple[int, dict]:
    rc = cli.main(argv)
    return rc, json.loads(capsys.readouterr().out)


def test_transition_previews_by_default_and_writes_nothing(tmp_path, capsys):
    out, args = _seed_transition(tmp_path)
    before = (out / "scores" / f"{MEM_ID}.json").read_text()
    rc, doc = _run(capsys, ["promote", MEM_ID, "--reason", "strong cluster",
                            "--evidence", "observation:obs_1", *args])
    assert rc == 0
    assert doc["mode"] == "preview" and doc["event"] is None
    assert doc["transition"] == {"verb": "promote", "memory_id": MEM_ID, "from": "candidate",
                                 "to": "promoted", "reason": "strong cluster"}
    assert doc["evidence"]["source_evidence_refs"] == ["observation:obs_1"]
    assert doc["durable_effect"]["learn"] == "write"
    assert (out / "scores" / f"{MEM_ID}.json").read_text() == before
    assert not (out / "promotions" / "events.jsonl").exists()
    assert not (tmp_path / "learn").exists()


def test_promote_apply_writes_state_event_projection_and_rebuilds(tmp_path, capsys):
    out, args = _seed_transition(tmp_path)
    rc, doc = _run(capsys, ["promote", MEM_ID, "--apply", "--reason", "strong cluster",
                            "--evidence", "observation:obs_1", *args])
    assert rc == 0, doc
    assert doc["mode"] == "applied" and doc["ok"] is True
    assert doc["event"]["to"] == "promoted" and doc["event"]["verb"] == "promote"

    score = json.loads((out / "scores" / f"{MEM_ID}.json").read_text())
    assert score["status"] == "promoted"

    learn = Path(doc["durable_effect"]["path"])
    assert learn.exists()
    # The projection must cite the event that authorised it, not an empty link.
    assert f"promotion_event: {doc['event']['id']}" in learn.read_text()

    # Published truth reflects the transition: promoted memories leave the inbox.
    exports = tmp_path / "exports"
    inbox_doc = json.loads((exports / "inbox-manifest.json").read_text())
    assert MEM_ID not in [i["id"] for i in inbox_doc["items"]]
    scores_doc = json.loads((exports / "memory-score-manifest.json").read_text())
    assert scores_doc["scores"][MEM_ID]["status"] == "promoted"

    # The journal is gone: the transition is durably complete.
    assert not list((out / "journal").glob("*.json"))


def test_illegal_transition_is_refused_before_anything_changes(tmp_path, capsys):
    out, args = _seed_transition(tmp_path, state="promoted")
    before = (out / "scores" / f"{MEM_ID}.json").read_text()
    rc, doc = _run(capsys, ["promote", MEM_ID, "--apply", "--reason", "no",
                            "--evidence", "observation:obs_1", *args])
    assert rc == 1
    assert "illegal transition" in doc["error"] and "requires 'candidate'" in doc["error"]
    assert (out / "scores" / f"{MEM_ID}.json").read_text() == before


def test_promote_without_evidence_is_refused(tmp_path, capsys):
    out, args = _seed_transition(tmp_path)
    rc, doc = _run(capsys, ["promote", MEM_ID, "--apply", "--reason", "trust me", *args])
    assert rc == 1
    assert "traceable source evidence" in doc["error"]
    assert not (out / "promotions" / "events.jsonl").exists()


def test_unpublished_evidence_ref_is_refused(tmp_path, capsys):
    out, args = _seed_transition(tmp_path)
    rc, doc = _run(capsys, ["promote", MEM_ID, "--apply", "--reason", "strong",
                            "--evidence", "observation:made-up", *args])
    assert rc == 1
    assert "unresolved evidence refs: observation:made-up" in doc["error"]


def test_reject_and_defer_leave_no_learn_record(tmp_path, capsys):
    for verb, expected in (("reject", "archived"), ("defer", "observed")):
        tmp = tmp_path / verb
        tmp.mkdir()
        out, args = _seed_transition(tmp)
        rc, doc = _run(capsys, [verb, MEM_ID, "--apply", "--reason", "not durable", *args])
        assert rc == 0, doc
        assert doc["event"]["to"] == expected
        assert doc["durable_effect"]["learn"] == "none"
        assert not (tmp / "learn").exists()
        assert json.loads((out / "scores" / f"{MEM_ID}.json").read_text())["status"] == expected


def test_rollback_removes_the_generated_projection(tmp_path, capsys):
    out, args = _seed_transition(tmp_path)
    rc, _ = _run(capsys, ["promote", MEM_ID, "--apply", "--reason", "strong",
                          "--evidence", "observation:obs_1", *args])
    assert rc == 0
    learn = next((tmp_path / "learn").rglob("*.md"))
    assert learn.exists()

    rc, doc = _run(capsys, ["rollback", MEM_ID, "--apply", "--reason", "premature", *args])
    assert rc == 0, doc
    assert doc["event"]["to"] == "candidate"
    assert not learn.exists(), "rollback must remove the projection it generated"


def test_deprecate_retains_the_record(tmp_path, capsys):
    out, args = _seed_transition(tmp_path)
    _run(capsys, ["promote", MEM_ID, "--apply", "--reason", "strong",
                  "--evidence", "observation:obs_1", *args])
    learn = next((tmp_path / "learn").rglob("*.md"))
    rc, doc = _run(capsys, ["deprecate", MEM_ID, "--apply", "--reason", "superseded", *args])
    assert rc == 0, doc
    assert doc["event"]["to"] == "deprecated"
    assert learn.exists(), "deprecate retains the record; it does not erase history"


def test_missing_export_bundle_blocks_transitions(tmp_path, capsys):
    out, args = _seed_transition(tmp_path)
    (tmp_path / "exports" / "memory-evidence-manifest.json").unlink()
    rc, doc = _run(capsys, ["promote", MEM_ID, "--apply", "--reason", "strong",
                            "--evidence", "observation:obs_1", *args])
    assert rc == 1
    assert "no evidence manifest" in doc["error"]


def test_rebuild_failure_compensates_and_restores_prior_truth(tmp_path, capsys, monkeypatch):
    out, args = _seed_transition(tmp_path)
    published_before = (tmp_path / "exports" / "memory-score-manifest.json").read_text()

    real_builder = cli._builder()
    calls = {"n": 0}

    def failing_rebuild() -> list[str]:
        calls["n"] += 1
        if calls["n"] == 1:
            return ["inbox-manifest.json: synthetic validation failure"]
        return real_rebuild()

    real_rebuild = real_builder.rebuild
    real_builder.rebuild = failing_rebuild
    monkeypatch.setattr(cli, "_builder", lambda: real_builder)

    rc, doc = _run(capsys, ["promote", MEM_ID, "--apply", "--reason", "strong",
                            "--evidence", "observation:obs_1", *args])
    assert rc == 1, doc
    assert doc["error"] == "export rebuild failed after the transition"
    assert doc["compensated"].startswith("compensate_")
    assert doc["recovery"] == "prior truth rebuilt"

    # Local state is back where it started.
    assert json.loads((out / "scores" / f"{MEM_ID}.json").read_text())["status"] == "candidate"
    assert not list((tmp_path / "learn").rglob("*.md"))
    assert (tmp_path / "exports" / "memory-score-manifest.json").read_text() == published_before

    # History is append-only: the event and its inverse both survive.
    events = [json.loads(x) for x in
              (out / "promotions" / "events.jsonl").read_text().splitlines() if x.strip()]
    assert [e["to"] for e in events] == ["promoted", "candidate"]
    assert events[1]["compensates"] == events[0]["id"]


def test_unrecoverable_rebuild_marks_drift_and_fails_closed(tmp_path, capsys, monkeypatch):
    out, args = _seed_transition(tmp_path)
    real_builder = cli._builder()
    real_builder.rebuild = lambda: ["inbox-manifest.json: synthetic validation failure"]
    monkeypatch.setattr(cli, "_builder", lambda: real_builder)

    rc, doc = _run(capsys, ["promote", MEM_ID, "--apply", "--reason", "strong",
                            "--evidence", "observation:obs_1", *args])
    assert rc == 1
    assert "rebuild of prior truth also failed" in doc["compensation_error"]
    assert doc["recovery"].startswith("index marked drift: true")

    # The index must now admit it is not current, on every surface.
    index = json.loads((tmp_path / "exports" / "truth-export-index.json").read_text())
    assert index["surfaces"] and all(s["drift"] is True for s in index["surfaces"])
