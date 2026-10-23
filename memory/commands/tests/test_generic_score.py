"""Phase 12E generic engine — real-inbox scoring + autonomous promotion tests.

Tracked; runs on tmp paths only. Covers the acceptance bar for the autonomous learning loop
(checklist §5/§6/§11): observations are scored and auto-moved between tiers, with
ONLY the exceptions (risky / conflicting / invalid) routed to a human review queue.

Invariants asserted here:
  - a valid mq-agent co-change observation is scored
  - factors derive correctly: frequency, source_count, confidence, recency
  - negative feedback lowers the score
  - frequency alone never promotes (ADR-008)
  - safety/global-risk memories are HELD for review, never auto-promoted
  - the promotion-event trail is append-only and grows only on a real tier change
  - invalid records are quarantined, not scored
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import emit_generic_score as egs

# --- helpers ---------------------------------------------------------------

def _obs(**over) -> dict:
    """A valid memory-observation.v1 record (mq-agent co-change shape by default)."""
    rec = {
        "schema": "memory-observation.v1",
        "id": "obs_mq-agent_cochange_1",
        "timestamp": "2026-06-28T12:00:00Z",
        "producer": "mq-agent",
        "repository": "mq-mcp",
        "workflow": "co-change",
        "title": "Co-change cluster detected",
        "observation": "When touching bridge.py, also check codegraph_cochange.py.",
        "category": "pattern",
        "confidence": 0.6,
        "evidence": [{"source": "bridget/cg-2", "reference": "cochange-run-x", "excerpt": "co-changed 4/10"}],
        "tags": ["co-change", "codegraph", "bridget"],
        "proposed_memory_key": "cochange-bridge-py",
    }
    rec.update(over)
    return rec


def _metrics(records, feedback=None, **kw):
    return egs.collect_metrics(records, feedback or [], **kw)["cochange-bridge-py"]


def _gen(**over) -> dict:
    """A valid NON-co-change observation (repo-signal command-pattern), so it exercises
    the frequency-based generic policy rather than the co-change single-shot policy."""
    rec = {
        "schema": "memory-observation.v1",
        "id": "gen_1",
        "timestamp": "2026-06-28T12:00:00Z",
        "producer": "repo-signal",
        "repository": "mq-mcp",
        "workflow": "command-pattern",
        "title": "Command pattern detected",
        "observation": "Run codegraph_cochange.py checks before merging.",
        "category": "pattern",
        "confidence": 0.6,
        "evidence": [{"source": "repo-signal", "reference": "rs-run-1", "excerpt": "seen"}],
        "tags": ["command"],
        "proposed_memory_key": "cmd-pattern-x",
    }
    rec.update(over)
    return rec


def _gmetrics(records, feedback=None, **kw):
    return egs.collect_metrics(records, feedback or [], **kw)["cmd-pattern-x"]


def _write_inbox(inbox_dir: Path, records: list[dict], *, producer: str = "mq-agent") -> None:
    inbox_dir.mkdir(parents=True, exist_ok=True)
    path = inbox_dir / f"{producer}.observations.jsonl"
    with path.open("a", encoding="utf-8") as fh:
        for r in records:
            fh.write(json.dumps(r) + "\n")


def _fb(memory_id: str, outcome: str) -> dict:
    return {"pattern_id": memory_id, "outcome": outcome}


# --- validation / quarantine ----------------------------------------------

def test_valid_cochange_record_passes_validation():
    assert egs.validate(_obs()) is None


def test_wrong_schema_is_quarantined():
    assert egs.validate(_obs(schema="something-else")) is not None


def test_missing_required_field_is_quarantined():
    bad = _obs()
    del bad["producer"]
    assert egs.validate(bad) is not None


def test_confidence_out_of_range_is_quarantined():
    assert egs.validate(_obs(confidence=1.5)) is not None


def test_bad_category_is_quarantined():
    assert egs.validate(_obs(category="nonsense")) is not None


def test_evidence_without_source_is_quarantined():
    assert egs.validate(_obs(evidence=[{"reference": "x"}])) is not None


def test_unparseable_line_is_quarantined():
    assert egs.validate({"_raw": "not json"}) is not None


# --- factor derivation -----------------------------------------------------

def test_frequency_counts_repeats():
    m = _metrics([_obs(id=f"o{i}") for i in range(3)])
    assert m["frequency"] == 3 and m["worked"] == 3


def test_source_count_is_distinct_producers():
    m = _metrics([_obs(id="a", producer="mq-agent"), _obs(id="b", producer="repo-signal")])
    assert m["source_count"] == 2 and m["observed_by"] == ["mq-agent", "repo-signal"]


def test_confidence_is_mean():
    m = _metrics([_obs(id="a", confidence=0.8), _obs(id="b", confidence=0.4)])
    assert abs(m["confidence"] - 0.6) < 1e-9


def test_reuse_is_distinct_sessions():
    m = _metrics([_obs(id="a", session_id="s1"), _obs(id="b", session_id="s1"), _obs(id="c", session_id="s2")])
    assert m["reuse"] == 2


def test_recency_recent_higher_than_old():
    today = date(2026, 6, 28)
    recent = _metrics([_obs(timestamp="2026-06-28T00:00:00Z")], today=today)
    old = _metrics([_obs(timestamp="2026-01-01T00:00:00Z")], today=today)
    assert recent["recency"] == 1.0 and old["recency"] == 0.0
    assert recent["recency"] > old["recency"]


def test_negative_feedback_lowers_score():
    base = _metrics([_obs(id=f"o{i}") for i in range(3)])
    neg = _metrics([_obs(id=f"o{i}") for i in range(3)], feedback=[_fb("cochange-bridge-py", "not_helped")])
    assert neg["score"] < base["score"]


# --- generic frequency policy (§5) — frequency alone never promotes ---------
# (non-co-change producers, e.g. repo-signal telemetry, where repetition is corroboration)

def test_single_observation_stays_observed():
    tier, _, bucket = egs.derive_observation_tier(_gmetrics([_gen()]))
    assert tier == "observed" and bucket is None


def test_high_frequency_no_breadth_no_benefit_stays_candidate():
    """Many observations from ONE source, no feedback → candidate, never promoted.
    Frequency + repetition cannot promote without breadth AND confirmed benefit."""
    m = _gmetrics([_gen(id=f"o{i}", confidence=0.95) for i in range(50)])
    tier, awaiting, bucket = egs.derive_observation_tier(m)
    assert m["frequency"] == 50 and tier == "candidate" and awaiting is True and bucket is None


def test_breadth_and_benefit_promotes():
    """freq>=8 + >=2 sources + confirming feedback + low risk → auto-promoted."""
    obs = ([_gen(id=f"a{i}", producer="repo-signal") for i in range(5)]
           + [_gen(id=f"b{i}", producer="command-bus") for i in range(5)])
    m = _gmetrics(obs, feedback=[_fb("cmd-pattern-x", "helped")])
    tier, _, bucket = egs.derive_observation_tier(m)
    assert m["frequency"] == 10 and m["source_count"] == 2 and tier == "promoted" and bucket is None


def test_promotion_ready_but_no_benefit_stays_candidate():
    obs = ([_gen(id=f"a{i}", producer="repo-signal") for i in range(5)]
           + [_gen(id=f"b{i}", producer="command-bus") for i in range(5)])
    tier, awaiting, bucket = egs.derive_observation_tier(_gmetrics(obs))  # no feedback
    assert tier == "candidate" and awaiting is True and bucket is None


# --- co-change policy (§ source-aware) — single-shot strength, review-required promotion ---

def test_cochange_single_strong_observation_reaches_candidate():
    """A single STRONG co-change observation reaches candidate — no frequency needed."""
    tier, awaiting, bucket = egs.derive_observation_tier(_metrics([_obs(confidence=0.45)]))
    assert tier == "candidate" and awaiting is True and bucket is None


def test_cochange_weak_single_observation_stays_observed():
    tier, _, bucket = egs.derive_observation_tier(_metrics([_obs(confidence=0.2)]))
    assert tier == "observed" and bucket is None


def test_cochange_strong_cluster_is_held_for_promotion_review_never_promoted():
    """Even with high frequency, breadth and benefit, co-change NEVER auto-promotes —
    a strong single-shot cluster is HELD for human promotion review."""
    obs = ([_obs(id=f"a{i}", producer="mq-agent", confidence=0.7) for i in range(5)]
           + [_obs(id=f"b{i}", producer="repo-signal", confidence=0.7) for i in range(5)])
    m = _metrics(obs, feedback=[_fb("cochange-bridge-py", "helped")])
    tier, awaiting, bucket = egs.derive_observation_tier(m)
    assert m["frequency"] == 10 and tier == "candidate" and awaiting is True
    assert bucket == "promotion-review"  # proposed for human promotion, not auto-promoted


def test_ebms_state_maps_promotion_review_to_pattern():
    assert egs.ebms_state("observed") == "scratch"
    assert egs.ebms_state("candidate") == "candidate"
    assert egs.ebms_state("candidate", "promotion-review") == "pattern"
    assert egs.ebms_state("promoted") == "permanent"


def test_cochange_never_returns_promoted_tier():
    """No combination of co-change signals yields the 'promoted' tier from the machine."""
    for conf in (0.3, 0.6, 0.95):
        for freq in (1, 10, 50):
            obs = [_obs(id=f"o{i}", confidence=conf) for i in range(freq)]
            tier, _, _ = egs.derive_observation_tier(_metrics(obs))
            assert tier != "promoted"


# --- risk routing (§6) — exceptions held for human review ------------------

def test_safety_risk_held_for_review_never_promotes():
    obs = ([_obs(id=f"a{i}", producer="mq-agent", observation="rotate the api key and secret token") for i in range(6)]
           + [_obs(id=f"b{i}", producer="repo-signal") for i in range(6)])
    m = _metrics(obs, feedback=[_fb("cochange-bridge-py", "helped")])
    assert m["risk_level"] == "safety"
    tier, _, bucket = egs.derive_observation_tier(m)
    assert tier == "observed" and bucket == "risky"  # held, not auto-promoted


def test_global_category_held_for_review():
    obs = ([_obs(id=f"a{i}", producer="mq-agent", category="architecture") for i in range(5)]
           + [_obs(id=f"b{i}", producer="repo-signal", category="architecture") for i in range(5)])
    m = _metrics(obs, feedback=[_fb("cochange-bridge-py", "helped")])
    assert m["risk_level"] == "global"
    tier, _, bucket = egs.derive_observation_tier(m)
    assert tier == "candidate" and bucket == "risky"  # would promote, but held


def test_negative_feedback_deprecates_and_routes_conflicting():
    m = _metrics([_obs(id=f"o{i}") for i in range(5)], feedback=[_fb("cochange-bridge-py", "not_helped")])
    tier, _, bucket = egs.derive_observation_tier(m)
    assert tier == "deprecated" and bucket == "conflicting"


# --- end-to-end run --------------------------------------------------------

def test_run_scores_valid_and_quarantines_invalid(tmp_path):
    inbox = tmp_path / "observations"
    out = tmp_path / "out"
    _write_inbox(inbox, [_gen()])  # single non-co-change obs → observed
    _write_inbox(inbox, [{"schema": "memory-observation.v1", "id": "bad", "confidence": 9}], producer="broken")

    summary = egs.run(inbox, out, feedback_path=tmp_path / "none.jsonl")

    assert summary["valid"] == 1 and summary["invalid"] == 1 and summary["memories"] == 1
    score_files = list((out / "scores").glob("*.json"))
    assert len(score_files) == 1
    rec = json.loads(score_files[0].read_text())
    assert rec["schema"] == "memory-score.v1" and rec["status"] == "observed"
    assert rec["ebms_state"] == "scratch"
    assert {"frequency", "source_count", "confidence", "recency"} <= set(rec["factors"])
    assert (out / "review" / "invalid.jsonl").exists()


def test_run_routes_risky_to_review(tmp_path):
    inbox = tmp_path / "observations"
    out = tmp_path / "out"
    obs = ([_obs(id=f"a{i}", producer="mq-agent", observation="store the secret token") for i in range(6)]
           + [_obs(id=f"b{i}", producer="repo-signal") for i in range(6)])
    _write_inbox(inbox, obs)
    fb = tmp_path / "fb.jsonl"
    fb.write_text(json.dumps(_fb("cochange-bridge-py", "helped")) + "\n")

    summary = egs.run(inbox, out, feedback_path=fb)
    assert summary["review"]["risky"] == 1 and summary["tally"]["promoted"] == 0
    risky = (out / "review" / "risky.jsonl").read_text().strip().splitlines()
    assert len(risky) == 1 and json.loads(risky[0])["risk_level"] == "safety"


def test_run_promotion_event_only_on_change(tmp_path):
    inbox = tmp_path / "observations"
    out = tmp_path / "out"
    obs = ([_gen(id=f"a{i}", producer="repo-signal") for i in range(5)]
           + [_gen(id=f"b{i}", producer="command-bus") for i in range(5)])
    _write_inbox(inbox, obs)
    fb = tmp_path / "fb.jsonl"
    fb.write_text(json.dumps(_fb("cmd-pattern-x", "helped")) + "\n")

    first = egs.run(inbox, out, feedback_path=fb)
    second = egs.run(inbox, out, feedback_path=fb)

    assert first["new_events"] >= 1 and first["tally"]["promoted"] == 1
    assert second["new_events"] == 0
    trail = (out / "promotions" / "events.jsonl").read_text().strip().splitlines()
    assert len(trail) == first["new_events"]
    ev = json.loads(trail[-1])
    assert ev["schema"] == "promotion-event.v1" and ev["to"] == "promoted"


def test_run_isolated_namespace(tmp_path):
    inbox = tmp_path / "observations"
    out = tmp_path / "out"
    _write_inbox(inbox, [_obs()])
    egs.run(inbox, out, feedback_path=tmp_path / "none.jsonl")
    assert (out / "scores").exists()
    # real namespace is memory/local/observation-scoring (NOT the reserved .../observations)
    assert egs.OUT.name == "observation-scoring"
    assert egs.OUT.parent.name == "local"


# --- deep conflict detection (§ detect-and-hold; promoted is authoritative) -------

def _promote(inbox: Path, *, text: str | None = None, ts: str = "2026-06-28T12:00:00Z") -> list[dict]:
    """A batch that auto-promotes cmd-pattern-x: freq=10, 2 sources, low risk. Uses the
    generic (non-co-change) fixture because co-change never auto-promotes; the authority/
    supersede layer being tested here is source-agnostic."""
    over = {"timestamp": ts}
    if text is not None:
        over["observation"] = text
    obs = ([_gen(id=f"a{i}", producer="repo-signal", **over) for i in range(5)]
           + [_gen(id=f"b{i}", producer="command-bus", **over) for i in range(5)])
    _write_inbox(inbox, obs)
    return obs


def test_promotion_captures_directive_snapshot(tmp_path):
    inbox, out = tmp_path / "observations", tmp_path / "out"
    _promote(inbox)
    fb = tmp_path / "fb.jsonl"
    fb.write_text(json.dumps(_fb("cmd-pattern-x", "helped")) + "\n")

    summary = egs.run(inbox, out, feedback_path=fb)
    assert summary["tally"]["promoted"] == 1
    snap = out / "promoted-content" / "cmd-pattern-x.json"
    assert snap.exists()
    s = json.loads(snap.read_text())
    assert s["memory_id"] == "cmd-pattern-x" and s["directive_hash"] and s["directive"]


def test_directive_drift_holds_promoted_and_proposes_supersede(tmp_path):
    """A promoted memory whose evidence drifts STAYS promoted (authoritative) and a
    supersede is proposed for human review — never auto-downgraded or rewritten."""
    inbox, out = tmp_path / "observations", tmp_path / "out"
    fb = tmp_path / "fb.jsonl"
    fb.write_text(json.dumps(_fb("cmd-pattern-x", "helped")) + "\n")

    _promote(inbox)
    first = egs.run(inbox, out, feedback_path=fb)
    assert first["tally"]["promoted"] == 1 and first["review"]["superseding"] == 0

    # New, contradicting evidence arrives later (different claim, fresher timestamp).
    _promote(inbox, text="Skip the ask.py checks instead.", ts="2026-06-29T12:00:00Z")
    second = egs.run(inbox, out, feedback_path=fb)

    assert second["tally"]["promoted"] == 1          # still authoritative
    assert second["tally"]["deprecated"] == 0        # never auto-downgraded
    assert second["review"]["superseding"] == 1
    assert second["new_events"] == 0                 # promoted state unchanged → no event

    proposals = (out / "review" / "supersede-proposals.jsonl").read_text().strip().splitlines()
    assert len(proposals) == 1
    p = json.loads(proposals[0])
    assert p["memory_id"] == "cmd-pattern-x" and p["trigger"] == "directive-drift"
    assert "ask.py" in p["current_directive"] and "codegraph_cochange.py" in p["promoted_directive"]


def test_negative_feedback_on_promoted_holds_not_deprecates(tmp_path):
    """Negative feedback deprecates an UNpromoted memory, but a PROMOTED one is held
    (supersede proposed) — it is authoritative until a human resolves the conflict."""
    inbox, out = tmp_path / "observations", tmp_path / "out"
    _promote(inbox)
    fb = tmp_path / "fb.jsonl"
    fb.write_text(json.dumps(_fb("cmd-pattern-x", "helped")) + "\n")
    egs.run(inbox, out, feedback_path=fb)  # promote + snapshot

    # Contradiction now arrives as negative feedback.
    with fb.open("a") as fh:
        fh.write(json.dumps(_fb("cmd-pattern-x", "not_helped")) + "\n")
    summary = egs.run(inbox, out, feedback_path=fb)

    assert summary["tally"]["promoted"] == 1 and summary["tally"]["deprecated"] == 0
    assert summary["review"]["superseding"] == 1 and summary["review"]["conflicting"] == 0
    p = json.loads((out / "review" / "supersede-proposals.jsonl").read_text().strip().splitlines()[0])
    assert p["trigger"] == "negative-feedback"


def test_supersede_proposal_is_deduped_across_runs(tmp_path):
    inbox, out = tmp_path / "observations", tmp_path / "out"
    _promote(inbox)
    fb = tmp_path / "fb.jsonl"
    fb.write_text(json.dumps(_fb("cmd-pattern-x", "helped")) + "\n")
    egs.run(inbox, out, feedback_path=fb)
    _promote(inbox, text="Skip the ask.py checks instead.", ts="2026-06-29T12:00:00Z")
    egs.run(inbox, out, feedback_path=fb)
    egs.run(inbox, out, feedback_path=fb)  # same conflict again → must NOT re-log
    proposals = (out / "review" / "supersede-proposals.jsonl").read_text().strip().splitlines()
    assert len(proposals) == 1


def test_drift_on_unpromoted_memory_is_not_a_supersede(tmp_path):
    """No promoted authority to protect → normal flow, no supersede proposal."""
    inbox, out = tmp_path / "observations", tmp_path / "out"
    _write_inbox(inbox, [_obs(id="a0"), _obs(id="a1", observation="totally different claim",
                                             timestamp="2026-06-29T12:00:00Z")])
    summary = egs.run(inbox, out, feedback_path=tmp_path / "none.jsonl")
    assert summary["review"]["superseding"] == 0
    assert not (out / "review" / "supersede-proposals.jsonl").exists()


# --- human resolution: promote-from-review / resolve-supersede --------------

def test_human_promoted_cochange_stays_promoted_not_bogusly_superseded(tmp_path):
    """A co-change memory's base tier is only 'candidate' (it never auto-promotes). After a
    HUMAN promotion, it must stay promoted and NOT be flagged as a (bogus) supersede when
    nothing actually changed — this guards the authority-block fix."""
    inbox, out = tmp_path / "observations", tmp_path / "out"
    none = tmp_path / "none.jsonl"
    _write_inbox(inbox, [_obs(confidence=0.7)])  # strong single-shot co-change
    res = egs.evaluate(inbox, feedback_path=none)
    d = res["decisions"]["cochange-bridge-py"]
    assert d["bucket"] == "promotion-review"  # held for human promotion, not auto-promoted

    egs.record_promotion(out, "cochange-bridge-py", res["metrics"]["cochange-bridge-py"],
                         d["tier"], d["directive"], d["directive_hash"], reason="human review")

    res2 = egs.evaluate(inbox, feedback_path=none,
                        prior=egs._last_known_tiers(egs._promotions_path(out)),
                        snapshots=egs._load_snapshots(out))
    assert res2["decisions"]["cochange-bridge-py"]["tier"] == "promoted"
    assert res2["summary"]["review"]["superseding"] == 0  # no bogus downgrade-as-supersede


def test_rejected_supersede_is_suppressed_from_re_proposal(tmp_path):
    inbox, out = tmp_path / "observations", tmp_path / "out"
    fb = tmp_path / "fb.jsonl"
    fb.write_text(json.dumps(_fb("cmd-pattern-x", "helped")) + "\n")
    _promote(inbox)
    egs.run(inbox, out, feedback_path=fb)
    _promote(inbox, text="Skip the ask.py checks instead.", ts="2026-06-29T12:00:00Z")
    first = egs.run(inbox, out, feedback_path=fb)
    assert first["review"]["superseding"] == 1
    # human rejects THIS conflict
    cur_hash = json.loads((out / "review" / "supersede-proposals.jsonl")
                          .read_text().strip().splitlines()[-1])["current_hash"]
    egs.append_resolved_supersede(out, "cmd-pattern-x", cur_hash, "rejected")
    second = egs.run(inbox, out, feedback_path=fb)
    assert second["review"]["superseding"] == 0  # suppressed; memory stays promoted
    assert second["tally"]["promoted"] == 1


def test_accepted_supersede_updates_snapshot_and_clears_conflict(tmp_path):
    inbox, out = tmp_path / "observations", tmp_path / "out"
    fb = tmp_path / "fb.jsonl"
    fb.write_text(json.dumps(_fb("cmd-pattern-x", "helped")) + "\n")
    _promote(inbox)
    egs.run(inbox, out, feedback_path=fb)
    _promote(inbox, text="Skip the ask.py checks instead.", ts="2026-06-29T12:00:00Z")
    first = egs.run(inbox, out, feedback_path=fb)
    it = first["review"]  # has 1 superseding
    assert it["superseding"] == 1
    # human accepts: adopt the current directive as authoritative
    res = egs.evaluate(inbox, feedback_path=fb,
                       prior=egs._last_known_tiers(egs._promotions_path(out)),
                       snapshots=egs._load_snapshots(out),
                       resolved=egs._load_resolved_supersedes(out))
    p = res["review"]["superseding"][0]
    egs._write_snapshot_file(out, "cmd-pattern-x", p["current_directive"], p["current_hash"], p["promoted_at"])
    second = egs.run(inbox, out, feedback_path=fb)
    assert second["review"]["superseding"] == 0  # snapshot now matches current → no drift
    assert second["tally"]["promoted"] == 1
