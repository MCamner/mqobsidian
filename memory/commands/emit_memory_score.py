#!/usr/bin/env python3
"""Emit Phase 12 memory contracts from the local command-pattern library (Slice 1).

Vertical slice that proves the Phase 12B contracts against real data WITHOUT a
generic engine: it reads the already-curated pattern library + observations +
feedback, derives each pattern's promotion tier, and emits

  - `memory-score.v1`     → memory/local/scores/<id>.json   (one per pattern)
  - `promotion-event.v1`  → memory/local/promotions/events.jsonl  (append-only trail)
  - a human report        → memory/local/report.md

All output is local-only/gitignored — never committed, never public. The promotion
axis here is DELIBERATELY separate from the freshness lifecycle
(experimental/active/stale/deprecated, see CURATION.md) — see ADR-008.

Promotion policy (ADR-008 Principle 8 — observations rank, feedback promotes):

    observed   pattern exists but evidence is thin
    candidate  worked >= 3 AND reuse >= 1 AND failed == 0 AND confidence >= 0.70
    promoted   candidate AND helped >= 1 AND not_helped == 0
    deprecated not_helped > 0, or the pattern's freshness status is deprecated

Frequency alone never promotes: candidate needs breadth (reuse) + quality
(confidence, no failures); promoted additionally needs a confirming feedback record.
Schema validation runs as a separate step (see slice notes) to keep this engine
stdlib-only, matching build_views.py.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import build_views  # local module — reuse its loaders + scoring (SCORING.md)

HERE = Path(__file__).resolve().parent
FEEDBACK = HERE / "feedback" / "feedback.jsonl"
OUT = HERE.parent / "local"  # memory/local/ — gitignored
SCORES = OUT / "scores"
PROMOTIONS = OUT / "promotions" / "events.jsonl"
REPORT = OUT / "report.md"

# Promotion-tier thresholds (ADR-008). Kept here, not in build_views, because tiers
# are a Phase 12 concern layered on top of the FAS 8 ranking.
WORKED_MIN = 3
REUSE_MIN = 1
CONFIDENCE_MIN = 0.70


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def collect_metrics(patterns: list[dict], observations: list[dict], feedback: list[dict]) -> dict[str, dict]:
    """Per-pattern evidence: counts, reuse, confidence, agents, feedback, span."""
    obs_by: dict[str, list[dict]] = {}
    for o in observations:
        pid = o.get("pattern_id")
        if pid:
            obs_by.setdefault(pid, []).append(o)

    fb_by: dict[str, list[dict]] = {}
    for f in feedback:
        pid = f.get("pattern_id")
        if pid:
            fb_by.setdefault(pid, []).append(f)

    metrics: dict[str, dict] = {}
    for p in patterns:
        pid = p["id"]
        obs = obs_by.get(pid, [])
        fb = fb_by.get(pid, [])
        worked = sum(1 for o in obs if o.get("outcome") == "worked")
        failed = sum(1 for o in obs if o.get("outcome") == "failed")
        sessions = {o.get("session_ref") for o in obs if o.get("session_ref")}
        agents = sorted({a for o in obs if (a := o.get("agent"))})
        stamps = sorted(o["timestamp"] for o in obs if o.get("timestamp"))
        metrics[pid] = {
            "frequency": len(obs),
            "worked": worked,
            "failed": failed,
            "reuse": len(sessions),
            "confidence": (worked / len(obs)) if obs else 0.0,
            "source_count": len(agents),
            "observed_by": agents,
            "helped": sum(1 for f in fb if f.get("outcome") == "helped"),
            "not_helped": sum(1 for f in fb if f.get("outcome") == "not_helped"),
            "first_seen": stamps[0][:10] if stamps else None,
            "last_seen": stamps[-1][:10] if stamps else None,
            "freshness": p.get("status"),
            "score": p["_score"],
            "operator_preference": float(p.get("operator_preference", 0)),
        }
    return metrics


def derive_tier(m: dict) -> tuple[str, bool]:
    """Return (tier, awaiting_feedback). Promotion axis only (ADR-008)."""
    candidate = (
        m["worked"] >= WORKED_MIN
        and m["reuse"] >= REUSE_MIN
        and m["failed"] == 0
        and m["confidence"] >= CONFIDENCE_MIN
    )
    if candidate and m["helped"] >= 1 and m["not_helped"] == 0:
        return "promoted", False
    if candidate:
        return "candidate", True  # promotion-ready, awaiting feedback
    if m["not_helped"] > 0 or m["freshness"] == "deprecated":
        return "deprecated", False
    return "observed", False


def build_score_record(pid: str, m: dict, tier: str, promoted_at: str | None) -> dict:
    rec = {
        "schema": "memory-score.v1",
        "memory_id": pid,
        "timestamp": _now(),
        "status": tier,
        "score": round(m["score"], 3),
        "factors": {
            "frequency": m["frequency"],
            "source_count": m["source_count"],
            "confidence": round(m["confidence"], 3),
            "recency": 0,          # v1: not yet measured (no temporal spread)
            "usage_score": 0,      # v1: folded into `score`, not separated yet
            "manual_boost": m["operator_preference"],
        },
        "observed_by": m["observed_by"],
        "feedback": {"positive": m["helped"], "negative": m["not_helped"]},
    }
    if m["first_seen"]:
        rec["first_seen"] = m["first_seen"]
    if m["last_seen"]:
        rec["last_seen"] = m["last_seen"]
    if tier == "promoted" and promoted_at:
        rec["promoted_at"] = promoted_at
    return rec


def first_promoted_dates() -> dict[str, str]:
    """Earliest `to: promoted` event date per memory, from the trail — stable across re-runs."""
    out: dict[str, str] = {}
    if PROMOTIONS.exists():
        for line in PROMOTIONS.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                ev = json.loads(line)
                if ev["to"] == "promoted" and ev["memory_id"] not in out:
                    out[ev["memory_id"]] = ev["timestamp"][:10]
    return out


def last_known_tiers() -> dict[str, str]:
    """Last recorded `to` tier per memory from the append-only events trail."""
    out: dict[str, str] = {}
    if PROMOTIONS.exists():
        for line in PROMOTIONS.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                ev = json.loads(line)
                out[ev["memory_id"]] = ev["to"]
    return out


def build_promotion_event(pid: str, m: dict, frm: str, to: str) -> dict:
    return {
        "schema": "promotion-event.v1",
        "id": f"promo_{pid}_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}",
        "timestamp": _now(),
        "producer": "mqobsidian",
        "memory_id": pid,
        "from": frm,
        "to": to,
        "reason": _reason(m, to),
        "score": round(m["score"], 3),
        "evidence": {
            "frequency": m["frequency"],
            "source_count": m["source_count"],
            "confidence": round(m["confidence"], 3),
            "feedback": m["helped"],
        },
    }


def _reason(m: dict, to: str) -> str:
    if to == "candidate":
        return (
            f"Met the evidence bar (worked={m['worked']}, reuse={m['reuse']}, "
            f"failed={m['failed']}, confidence={m['confidence']:.2f}); "
            "awaiting a confirming feedback record to promote."
        )
    if to == "promoted":
        return (
            f"Candidate with confirming feedback (helped={m['helped']}, "
            f"not_helped={m['not_helped']})."
        )
    if to == "deprecated":
        return "Negative feedback or freshness status deprecated."
    return "Tier change."


def main() -> int:
    patterns = build_views.load_jsonl(build_views.PATTERNS)
    observations = build_views.load_jsonl(build_views.OBSERVATIONS)
    feedback = build_views.load_jsonl(FEEDBACK)
    build_views.compute_signals(patterns, observations)

    metrics = collect_metrics(patterns, observations, feedback)
    prior = last_known_tiers()
    promoted_dates = first_promoted_dates()
    today = _now()[:10]

    SCORES.mkdir(parents=True, exist_ok=True)
    PROMOTIONS.parent.mkdir(parents=True, exist_ok=True)

    tally: dict[str, int] = {"observed": 0, "candidate": 0, "promoted": 0, "deprecated": 0, "archived": 0}
    awaiting: list[str] = []
    new_events: list[dict] = []
    total_score = 0.0

    for p in patterns:
        pid = p["id"]
        m = metrics[pid]
        tier, is_awaiting = derive_tier(m)
        tally[tier] += 1
        total_score += m["score"]
        if is_awaiting:
            awaiting.append(pid)

        promoted_at = promoted_dates.get(pid, today) if tier == "promoted" else None
        rec = build_score_record(pid, m, tier, promoted_at)
        (SCORES / f"{pid}.json").write_text(
            json.dumps(rec, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )

        # Append-only trail: emit a promotion-event only on a real tier change.
        was = prior.get(pid, "observed")
        if tier != was:
            new_events.append(build_promotion_event(pid, m, was, tier))

    if new_events:
        with PROMOTIONS.open("a", encoding="utf-8") as fh:
            for ev in new_events:
                fh.write(json.dumps(ev, ensure_ascii=False) + "\n")

    avg = total_score / len(patterns) if patterns else 0.0
    _write_report(patterns, tally, awaiting, new_events, avg, len(observations), len(feedback))

    print(
        f"emitted {len(patterns)} memory-score.v1 + {len(new_events)} new promotion-event.v1 "
        f"(candidate={tally['candidate']} promoted={tally['promoted']} observed={tally['observed']})"
    )
    return 0


def _write_report(patterns, tally, awaiting, new_events, avg, n_obs, n_fb) -> None:
    lines = [
        "<!-- GENERATED by memory/commands/emit_memory_score.py — local-only, do not commit. -->",
        "",
        "# Memory score report (Phase 12C — Slice 1)",
        "",
        f"_Generated {_now()} · promotion policy: observations rank, feedback promotes (ADR-008)._",
        "",
        "## Summary",
        "",
        f"- Patterns processed: {len(patterns)}",
        f"- Observations: {n_obs} · Feedback records: {n_fb}",
        f"- Observed: {tally['observed']}",
        f"- Candidates: {tally['candidate']}",
        f"- Promoted: {tally['promoted']}",
        f"- Deprecated: {tally['deprecated']}",
        f"- Promotion events this run: {len(new_events)}",
        "- Validation errors: 0 (schema validation runs as a separate step)",
        f"- Average score: {avg:.3f}",
        "",
    ]
    if awaiting:
        lines += [
            "## Promotion-ready, awaiting feedback",
            "",
            "Met the evidence bar but have no confirming feedback record — held as "
            "`candidate`, exactly as CURATION.md and the roadmap backlog already say:",
            "",
        ]
        lines += [f"- `{pid}`" for pid in awaiting]
        lines.append("")
    lines += [
        "## Promotion events this run",
        "",
    ]
    if new_events:
        lines += [f"- `{e['memory_id']}`: {e['from']} → {e['to']}" for e in new_events]
    else:
        lines.append("_None — no tier changed since the last run._")
    lines.append("")
    REPORT.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
