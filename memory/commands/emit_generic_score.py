#!/usr/bin/env python3
"""Phase 12E — the GENERIC cross-producer scoring engine (tracked; output local-only).

This is the real engine that Slice 1.5's compatibility adapter
(`emit_observation_score.py`) only *probed*. The adapter proved — against a
synthetic fixture — that a `memory-observation.v1` producer can reuse the
command-pattern record shapes. This engine does the real thing: it reads the
REAL, local-only observation inbox (`memory/observations/*.observations.jsonl`,
written only by real MQ runs: repo-signal, and now mq-agent's co-change emitter),
scores it, and AUTONOMOUSLY moves observations between promotion tiers — routing
only the exceptions (risky / conflicting) to a human review queue.

Design owner is the policy owner, not a daily inbox moderator: the default path is
automatic. Human review is required ONLY for high-risk, conflicting, public-facing,
or global-behaviour-changing memories (see `assess_risk` + the review buckets).

REUSED verbatim from `emit_memory_score.py` (Slice 1) — record SHAPES only, so the
two contracts stay one definition (ADR-008):

    build_score_record     memory-score.v1 shape
    build_promotion_event  promotion-event.v1 shape  (reason overridden per-track)
    _now / FEEDBACK        shared clock + shared (memory-scoped) feedback store

NEW here (the genuinely generic-engine logic):

  1. Inbox glob + per-producer ingest. Observations carry confidence+evidence, not
     worked/failed/reuse, so we map: worked<-frequency, failed<-0, reuse<-distinct
     session_id, confidence<-mean, source_count<-distinct producer, helped/not_helped
     <-shared feedback by memory_id.
  2. Structural validation + a three-bucket review queue (invalid / conflicting /
     risky). Stdlib-only, matching build_views.py house style.
  3. A measured `recency` factor (Slice 1 left it 0). One factor among several;
     never promotes alone (ADR-008).
  4. `derive_observation_tier` — an OBSERVATION-SPECIFIC auto-promotion policy that
     DELIBERATELY diverges from the command-pattern `emit_memory_score.derive_tier`:
     co-change-aware confidence floor (0.05, not 0.70), frequency/breadth-based
     promotion, "positive usage OR confirmed benefit" instead of strictly a feedback
     record — but still: FREQUENCY ALONE NEVER PROMOTES, and every high-risk /
     global / conflicting memory is held for human review instead of auto-promoting.
  5. `assess_risk` — keyword/category heuristic that flags safety- or
     architecture/decision-level memories so they never auto-promote silently.

Output is a SEPARATE real namespace so it never clobbers Slice 1's command-pattern
scores. Cross-producer score MERGE (one memory, many producers) is DD-003, deferred:

    memory/local/observations/scores/<memory_id>.json     (memory-score.v1)
    memory/local/observations/promotions/events.jsonl     (promotion-event.v1, append-only)
    memory/local/observations/review/invalid.jsonl        (failed validation)
    memory/local/observations/review/conflicting.jsonl    (negative feedback / contradiction)
    memory/local/observations/review/risky.jsonl          (safety / global — would promote, held)
    memory/local/observations/review/supersede-proposals.jsonl  (deep conflict; see below)
    memory/local/observations/promoted-content/<id>.json  (directive snapshot at promotion)
    memory/local/observations/report.md                   (human summary)

DEEP CONFLICT DETECTION (detect-and-hold; locked policy 2026-06-30). A PROMOTED
memory is AUTHORITATIVE until a human resolves a conflict — new evidence may NOT
silently downgrade or rewrite it (ADR-008 corollary: as frequency never auto-PROMOTES,
new evidence never auto-SUPERSEDES). When a memory is already promoted and its directive
drifts from the snapshot captured at promotion, OR new signals would deprecate it, the
engine KEEPS it promoted and appends a `propose-supersede` proposal for human review — it
NEVER auto-downgrades or rewrites promoted state. Snapshots are immutable here; resolution
is a manual/operator step (edit or remove the snapshot under promoted-content/).

All output is local-only/gitignored — never committed, never published. Promotion
is NOT publication: public export stays a separate, gated step (memory/observations
README + ADR-008).
"""

from __future__ import annotations

import hashlib
import json
from datetime import date, datetime, timezone
from pathlib import Path

import emit_memory_score as ems  # reuse memory-score.v1 / promotion-event.v1 SHAPES (ADR-008)

HERE = Path(__file__).resolve().parent
MEMORY = HERE.parent

# REAL inbox — local-only/gitignored, written only by real runs (memory/observations/README.md).
INBOX_DIR = MEMORY / "observations"
INBOX_GLOB = "*.observations.jsonl"

# REAL output — separate namespace from Slice 1's memory/local/scores (no clobber; DD-003 deferred).
# NB: deliberately NOT memory/local/observations — that name is reserved by the two-track
# guard (no synthetic FEED may masquerade as real evidence there); this is scoring OUTPUT.
OUT = MEMORY / "local" / "observation-scoring"

CATEGORIES = {
    "pattern", "workflow", "architecture", "bug",
    "review", "decision", "prompt", "preference", "learning",
}

# Transparent linear recency decay. One factor among several; never promotes alone.
RECENCY_WINDOW_DAYS = 90

# --- observation-specific auto-promotion policy (checklist §5; ADR-008 invariant) ---
# observed -> candidate
CANDIDATE_FREQ_MIN = 3
CANDIDATE_CONFIDENCE_MIN = 0.05      # co-change is a weak signal; intake floor, not promotion
# candidate -> promoted
PROMOTE_FREQ_MIN = 8
PROMOTE_SOURCES_MIN = 2
STRONG_SOURCE_FREQ = 12              # "recurring strong source" alternative to >=2 producers

# Source-aware policy for CO-CHANGE (locked 2026-06-30). The frequency model above fits
# high-volume telemetry (repo-signal): repetition is real corroboration there. Co-change
# is OPERATOR-TRIGGERED — it grows in frequency only if the operator re-runs the same
# file, so a frequency-based promote bar is structurally unreachable. Co-change's signal
# is high SINGLE-SHOT confidence (real top-row confidence ~0.3–0.87), not repetition.
# So: a strong single-shot co-change reaches `candidate` WITHOUT a frequency requirement,
# and it NEVER auto-promotes — a strong cluster is HELD for human promotion review
# (`promotion-review`), never advanced to `promoted` by the machine. (Mirror invariant:
# as frequency never auto-promotes, co-change strength never auto-promotes either.)
COCHANGE_CANDIDATE_CONF = 0.30       # single-shot strength to reach candidate (a real cluster)
COCHANGE_PROMOTE_REVIEW_CONF = 0.60  # strong enough to PROPOSE for human promotion (held, not auto)

# Risk heuristic: memories that must never auto-promote silently (checklist §6).
SAFETY_KEYWORDS = (
    "credential", "secret", "token", "password", "api key", "api-key",
    "rm -rf", "drop table", "delete from", "chmod", "sudo", "private key",
)
GLOBAL_CATEGORIES = {"architecture", "decision"}


def _scores_dir(out: Path) -> Path:
    return out / "scores"


def _promotions_path(out: Path) -> Path:
    return out / "promotions" / "events.jsonl"


def _review_path(out: Path, bucket: str) -> Path:
    return out / "review" / f"{bucket}.jsonl"


def _report_path(out: Path) -> Path:
    return out / "report.md"


def _snapshot_dir(out: Path) -> Path:
    """Per-memory directive snapshot captured at promotion (immutable until human review)."""
    return out / "promoted-content"


def _supersede_path(out: Path) -> Path:
    return out / "review" / "supersede-proposals.jsonl"


def _resolved_supersede_path(out: Path) -> Path:
    """Append-only audit of human supersede resolutions (accept/reject)."""
    return out / "review" / "supersede-resolved.jsonl"


def _safe(memory_id: str) -> str:
    """Filesystem-safe score filename stem (memory ids are author-supplied keys)."""
    return "".join(c if (c.isalnum() or c in "-_.") else "-" for c in memory_id) or "_"


def _directive(observations: list[dict]) -> str:
    """The memory's representative claim: the freshest observation text, normalized.
    For co-change this embeds the cluster ("also check: A, B"), so a changed cluster
    changes the directive — that is what drift detection compares."""
    latest = max(observations, key=lambda o: (o.get("timestamp", ""), o.get("id", "")))
    return " ".join(str(latest.get("observation", "")).lower().split())


def _dhash(directive: str) -> str:
    return hashlib.sha1(directive.encode("utf-8")).hexdigest()[:16]


def _load_snapshots(out: Path) -> dict[str, dict]:
    """Directive snapshots captured when each memory first promoted (memory_id -> snapshot)."""
    snaps: dict[str, dict] = {}
    d = _snapshot_dir(out)
    if d.exists():
        for path in sorted(d.glob("*.json")):
            try:
                snap = json.loads(path.read_text(encoding="utf-8"))
            except (ValueError, OSError):
                continue
            mid = snap.get("memory_id")
            if mid:
                snaps[mid] = snap
    return snaps


def _write_snapshot_file(out: Path, mid: str, directive: str, directive_hash: str, promoted_at: str | None) -> None:
    """Write/overwrite one directive snapshot. Capture-at-promotion is immutable, but a human
    resolution (resolve-supersede --accept) deliberately overwrites it with the adopted directive."""
    d = _snapshot_dir(out)
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{_safe(mid)}.json").write_text(
        json.dumps({
            "memory_id": mid, "directive": directive, "directive_hash": directive_hash,
            "promoted_at": promoted_at, "captured_at": ems._now(),
        }, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _load_resolved_supersedes(out: Path) -> set[tuple[str, str]]:
    """(memory_id, current_hash) pairs a human has REJECTED — suppressed from re-proposal.
    Accepted resolutions stop drift by updating the snapshot, so only rejects need tracking."""
    out_set: set[tuple[str, str]] = set()
    path = _resolved_supersede_path(out)
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except ValueError:
                continue
            if r.get("resolution") == "rejected" and r.get("memory_id") and r.get("current_hash"):
                out_set.add((r["memory_id"], r["current_hash"]))
    return out_set


def append_resolved_supersede(out: Path, mid: str, current_hash: str, resolution: str, *, note: str = "") -> None:
    """Append-only audit record of a human supersede resolution (accept/reject)."""
    path = _resolved_supersede_path(out)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps({
            "memory_id": mid, "current_hash": current_hash, "resolution": resolution,
            "note": note, "resolved_at": ems._now(),
        }, ensure_ascii=False) + "\n")


def load_inbox(inbox_dir: Path) -> list[dict]:
    """Every JSON line from every producer inbox file. Unparseable lines are returned
    as ``{"_raw": <text>}`` so validation can quarantine them rather than crash."""
    out: list[dict] = []
    if not inbox_dir.exists():
        return out
    for path in sorted(inbox_dir.glob(INBOX_GLOB)):
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                out.append({"_raw": line})
    return out


def validate(record: dict) -> str | None:
    """Structural check against memory-observation.v1. Returns a reason string when
    the record must be QUARANTINED, or None when it is well-formed. Stdlib-only."""
    if "_raw" in record:
        return "unparseable JSON line"
    if record.get("schema") != "memory-observation.v1":
        return f"schema is not memory-observation.v1 (got {record.get('schema')!r})"
    for key in ("id", "producer", "repository", "title", "observation"):
        val = record.get(key)
        if not isinstance(val, str) or not val.strip():
            return f"missing or empty required field: {key}"
    if record.get("category") not in CATEGORIES:
        return f"category not in enum: {record.get('category')!r}"
    conf = record.get("confidence")
    if not isinstance(conf, (int, float)) or isinstance(conf, bool) or not (0.0 <= conf <= 1.0):
        return f"confidence not a number in [0,1]: {conf!r}"
    evidence = record.get("evidence")
    if not isinstance(evidence, list) or not evidence:
        return "evidence must be a non-empty array"
    for item in evidence:
        if not isinstance(item, dict) or not isinstance(item.get("source"), str) or not item["source"].strip():
            return "every evidence item requires a non-empty source"
    return None


def assess_risk(records: list[dict]) -> tuple[str, str]:
    """Classify a memory's review risk from its observations (checklist §6).

    Returns one of ("safety", "global", "low") plus a human reason. A memory flagged
    `safety` or `global` is never auto-promoted silently — it is held for human review.
    """
    cats = {c for r in records if (c := r.get("category"))}
    blob = " ".join(
        f"{r.get('title', '')} {r.get('observation', '')} {' '.join(r.get('tags', []))}"
        for r in records
    ).lower()
    hit = next((k for k in SAFETY_KEYWORDS if k in blob), None)
    if hit:
        return "safety", f"safety-sensitive keyword: {hit!r}"
    risky_cats = cats & GLOBAL_CATEGORIES
    if risky_cats:
        return "global", f"global/architecture category: {sorted(risky_cats)}"
    return "low", ""


def _recency(last_seen: str | None, *, today: date | None = None) -> float:
    """Linear decay in [0,1]: 1.0 today, 0.0 once older than RECENCY_WINDOW_DAYS."""
    if not last_seen:
        return 0.0
    today = today or datetime.now(timezone.utc).date()
    try:
        seen = date.fromisoformat(last_seen[:10])
    except ValueError:
        return 0.0
    age = (today - seen).days
    if age <= 0:
        return 1.0
    return round(max(0.0, 1.0 - age / RECENCY_WINDOW_DAYS), 3)


def _score(
    confidence: float, frequency: int, reuse: int, source_count: int,
    recency: float, helped: int, not_helped: int,
) -> float:
    """Transparent additive ranking score. Monotone up in good signals, DOWN in
    negative feedback. Secondary to the promotion TIER, which `derive_observation_tier`
    decides; never lets frequency alone carry a memory."""
    return round(
        confidence
        + 0.15 * frequency
        + 0.10 * reuse
        + 0.05 * source_count
        + 0.10 * recency
        + 0.10 * helped
        - 0.20 * not_helped,
        3,
    )


def ebms_state(tier: str, review_bucket: str | None = None) -> str:
    """Map mqobsidian's operational tier to the EBMS lifecycle vocabulary.

    `pattern` is a review-held, promotion-ready state; `permanent` is reached
    only after promotion, which is the gate consumed by learn-writeback.
    """
    if tier == "promoted":
        return "permanent"
    if tier == "candidate" and review_bucket == "promotion-review":
        return "pattern"
    if tier == "candidate":
        return "candidate"
    return "scratch"


def derive_observation_tier(m: dict) -> tuple[str, bool, str | None]:
    """Observation-track promotion policy (checklist §5). Returns
    (tier, awaiting_promotion, review_bucket). SOURCE-AWARE: co-change uses a
    single-shot, review-required policy; everything else uses the frequency model.

    `review_bucket` is None on the automatic happy path, or "conflicting"/"risky"/
    "promotion-review" when the memory must be routed to a human (the only exceptions).
    FREQUENCY ALONE NEVER PROMOTES; every high-risk/global/conflicting memory is held.
    """
    if m.get("is_cochange"):
        return _derive_cochange_tier(m)

    freq = m["frequency"]
    sources = m["source_count"]
    conf = m["confidence"]
    helped = m["helped"]
    not_helped = m["not_helped"]
    risk = m.get("risk_level", "low")
    benefit = helped >= 1 or m.get("usage_score", 0) > 0

    # Recurring negative feedback contradicts the memory -> deprecate + route for review.
    if not_helped > 0:
        return "deprecated", False, "conflicting"

    meets_candidate = freq >= CANDIDATE_FREQ_MIN and conf >= CANDIDATE_CONFIDENCE_MIN
    if not meets_candidate:
        return "observed", False, None

    # Safety risk blocks even candidate auto-advance — hold at observed for review.
    if risk == "safety":
        return "observed", False, "risky"

    strong_source = sources >= PROMOTE_SOURCES_MIN or freq >= STRONG_SOURCE_FREQ
    meets_promote = freq >= PROMOTE_FREQ_MIN and strong_source and benefit
    if not meets_promote:
        return "candidate", True, None

    # Promotion-ready, but a global/architecture change must not promote without review.
    if risk == "global":
        return "candidate", True, "risky"
    return "promoted", False, None


def _derive_cochange_tier(m: dict) -> tuple[str, bool, str | None]:
    """Co-change promotion policy: review-promotable from single-shot strength, NEVER
    auto-promotable by repetition (locked 2026-06-30). Co-change never returns "promoted"
    — a strong cluster is held for human promotion review instead."""
    conf = m["confidence"]
    not_helped = m["not_helped"]
    risk = m.get("risk_level", "low")

    # Negative feedback still contradicts an UNpromoted co-change memory (the authority
    # layer in evaluate separately protects an already-promoted one).
    if not_helped > 0:
        return "deprecated", False, "conflicting"

    # Below single-shot strength → stays observed (no frequency can rescue it).
    if conf < COCHANGE_CANDIDATE_CONF:
        return "observed", False, None

    # Safety-sensitive content is held even at candidate.
    if risk == "safety":
        return "observed", False, "risky"

    # Global/architecture co-change is held for review (never auto-advanced).
    if risk == "global":
        return "candidate", True, "risky"

    # Strong single-shot cluster → propose for HUMAN promotion (held; co-change never auto-promotes).
    if conf >= COCHANGE_PROMOTE_REVIEW_CONF:
        return "candidate", True, "promotion-review"

    # A real-but-not-strong cluster sits at candidate, awaiting stronger evidence.
    return "candidate", True, None


def collect_metrics(observations: list[dict], feedback: list[dict], *, today: date | None = None) -> dict[str, dict]:
    """Aggregate valid observations by memory key into the metrics dict shape that the
    reused ems.build_score_record / build_promotion_event understand, plus the
    engine-internal `risk_level` used for review routing (not a persisted factor)."""
    by_key: dict[str, list[dict]] = {}
    for o in observations:
        key = o.get("proposed_memory_key") or o["id"]
        by_key.setdefault(key, []).append(o)

    fb_by: dict[str, list[dict]] = {}
    for f in feedback:
        mid = f.get("pattern_id")  # feedback is memory-scoped; field name is historical
        if mid:
            fb_by.setdefault(mid, []).append(f)

    metrics: dict[str, dict] = {}
    for key, obs in by_key.items():
        fb = fb_by.get(key, [])
        confs = [float(o["confidence"]) for o in obs if "confidence" in o]
        confidence = sum(confs) / len(confs) if confs else 0.0
        sessions = {o.get("session_id") for o in obs if o.get("session_id")}
        producers = sorted({p for o in obs if (p := o.get("producer"))})
        stamps = sorted(o["timestamp"] for o in obs if o.get("timestamp"))
        frequency = len(obs)
        reuse = len(sessions)
        source_count = len(producers)
        helped = sum(1 for f in fb if f.get("outcome") == "helped")
        not_helped = sum(1 for f in fb if f.get("outcome") == "not_helped")
        last_seen = stamps[-1][:10] if stamps else None
        recency = _recency(last_seen, today=today)
        risk_level, risk_reason = assess_risk(obs)
        directive = _directive(obs)
        # Source-aware: co-change uses a single-shot, review-required promotion policy.
        is_cochange = any(
            o.get("workflow") == "co-change"
            or any(e.get("source") == "bridget/cg-2" for e in o.get("evidence", []) if isinstance(e, dict))
            for o in obs
        )
        metrics[key] = {
            # --- ingest mapping (kept for the reused build_promotion_event reason text) ---
            "worked": frequency, "failed": 0, "reuse": reuse,
            # --- promotion-policy + score inputs ---
            "frequency": frequency,
            "source_count": source_count,
            "confidence": confidence,
            "helped": helped,
            "not_helped": not_helped,
            "usage_score": 0,           # no usage telemetry yet; benefit comes from feedback
            "observed_by": producers,
            "operator_preference": 0.0,
            "first_seen": stamps[0][:10] if stamps else None,
            "last_seen": last_seen,
            "recency": recency,
            "risk_level": risk_level,   # engine-internal: drives review routing, not a factor
            "risk_reason": risk_reason,
            "directive": directive,         # engine-internal: representative claim for drift detection
            "directive_hash": _dhash(directive),
            "is_cochange": is_cochange,     # engine-internal: selects the co-change tier policy
            "score": _score(confidence, frequency, reuse, source_count, recency, helped, not_helped),
        }
    return metrics


def _last_known_tiers(promotions: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    if promotions.exists():
        for line in promotions.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                ev = json.loads(line)
                out[ev["memory_id"]] = ev["to"]
    return out


def _first_promoted_dates(promotions: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    if promotions.exists():
        for line in promotions.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                ev = json.loads(line)
                if ev["to"] == "promoted" and ev["memory_id"] not in out:
                    out[ev["memory_id"]] = ev["timestamp"][:10]
    return out


def _reason(m: dict, to: str) -> str:
    """Observation-track, explainable promotion reason (audit + `explain`)."""
    base = (
        f"freq={m['frequency']}, sources={m['source_count']}, conf={m['confidence']:.2f}, "
        f"helped={m['helped']}, not_helped={m['not_helped']}, risk={m.get('risk_level', 'low')}"
    )
    if to == "candidate":
        return f"Met candidate bar ({base}); awaiting breadth/benefit to promote."
    if to == "promoted":
        return f"Met promotion bar with confirmed benefit ({base})."
    if to == "deprecated":
        return f"Negative feedback contradicts the memory ({base})."
    return f"Tier change ({base})."


def _cochange_rationale(m: dict) -> list[str]:
    """Co-change prose, mirroring _derive_cochange_tier (single-shot; review-required)."""
    conf, not_helped = m["confidence"], m["not_helped"]
    risk = m.get("risk_level", "low")
    if not_helped > 0:
        return [f"Deprecated: {not_helped} negative feedback record(s) contradict this co-change memory."]
    if conf < COCHANGE_CANDIDATE_CONF:
        return [f"Observed: co-change confidence {conf:.2f} < {COCHANGE_CANDIDATE_CONF} "
                "(single-shot strength; frequency cannot rescue it)."]
    lines = [f"Candidate: co-change confidence {conf:.2f} >= {COCHANGE_CANDIDATE_CONF} (single-shot strength)."]
    if risk == "safety":
        lines.append("Held (risky): safety-sensitive content — not auto-advanced; needs human review.")
    elif risk == "global":
        lines.append("Held (risky): architecture/decision-level change needs human review.")
    elif conf >= COCHANGE_PROMOTE_REVIEW_CONF:
        lines.append(f"Held (promotion-review): confidence {conf:.2f} >= {COCHANGE_PROMOTE_REVIEW_CONF} — "
                     "strong enough to PROPOSE for promotion; co-change never auto-promotes, a human decides.")
    else:
        lines.append(f"Candidate: confidence {conf:.2f} < {COCHANGE_PROMOTE_REVIEW_CONF} — "
                     "a real cluster, awaiting stronger evidence to propose promotion.")
    return lines


def tier_rationale(m: dict) -> list[str]:
    """Plain-language lines explaining why a memory got its tier AND why not higher.
    Mirrors derive_observation_tier exactly, in prose, for `explain` + audit."""
    if m.get("is_cochange"):
        return _cochange_rationale(m)

    freq, sources, conf = m["frequency"], m["source_count"], m["confidence"]
    helped, not_helped, risk = m["helped"], m["not_helped"], m.get("risk_level", "low")
    benefit = helped >= 1 or m.get("usage_score", 0) > 0
    lines: list[str] = []

    if not_helped > 0:
        lines.append(f"Deprecated: {not_helped} negative feedback record(s) contradict this memory.")
        return lines

    if not (freq >= CANDIDATE_FREQ_MIN and conf >= CANDIDATE_CONFIDENCE_MIN):
        unmet = []
        if freq < CANDIDATE_FREQ_MIN:
            unmet.append(f"frequency {freq} < {CANDIDATE_FREQ_MIN}")
        if conf < CANDIDATE_CONFIDENCE_MIN:
            unmet.append(f"confidence {conf:.2f} < {CANDIDATE_CONFIDENCE_MIN}")
        lines.append(f"Observed: below the candidate bar ({', '.join(unmet)}).")
        return lines

    lines.append(f"Candidate: frequency {freq} >= {CANDIDATE_FREQ_MIN} and confidence "
                 f"{conf:.2f} >= {CANDIDATE_CONFIDENCE_MIN}.")
    if risk == "safety":
        lines.append("Held (risky): safety-sensitive content — not auto-advanced; needs human review.")
        return lines

    strong_source = sources >= PROMOTE_SOURCES_MIN or freq >= STRONG_SOURCE_FREQ
    unmet = []
    if freq < PROMOTE_FREQ_MIN:
        unmet.append(f"frequency {freq} < {PROMOTE_FREQ_MIN}")
    if not strong_source:
        unmet.append(f"source_count {sources} < {PROMOTE_SOURCES_MIN} (and frequency < {STRONG_SOURCE_FREQ})")
    if not benefit:
        unmet.append("no usage/benefit signal yet")
    if unmet:
        lines.append(f"Not promoted: {'; '.join(unmet)}.")
    elif risk == "global":
        lines.append("Promotion-ready but held (risky): architecture/decision-level change needs review.")
    else:
        lines.append(f"Promoted: frequency {freq} >= {PROMOTE_FREQ_MIN}, breadth met, confirmed "
                     "benefit, and risk is low.")
    return lines


def _supersede_proposal(mid: str, m: dict, snap: dict | None, trigger: str) -> dict:
    """The reviewable underlay for a deep conflict: the promoted (authoritative) directive
    next to the diverging current one, so a human can decide whether to supersede."""
    return {
        "memory_id": mid,
        "trigger": trigger,                       # "directive-drift" | "negative-feedback"
        "promoted_directive": (snap or {}).get("directive", ""),
        "current_directive": m["directive"],
        "promoted_hash": (snap or {}).get("directive_hash", ""),
        "current_hash": m["directive_hash"],
        "promoted_at": (snap or {}).get("promoted_at"),
        "score": m["score"],
        "observed_by": m["observed_by"],
        "reason": (
            "new evidence diverges from the promoted memory — proposing supersede; "
            "the promoted memory stays authoritative until a human resolves the conflict"
        ),
    }


def evaluate(
    inbox_dir: Path, *, feedback_path: Path = ems.FEEDBACK,
    prior: dict[str, str] | None = None, promoted_dates: dict[str, str] | None = None,
    snapshots: dict[str, dict] | None = None, resolved: set[tuple[str, str]] | None = None,
    today: date | None = None,
) -> dict:
    """PURE computation: read + validate the inbox, derive tiers, and decide what WOULD
    be written — without touching disk. `run` wraps this and persists; the CLI uses it
    read-only for status / explain / quarantine / --dry-run."""
    raw = load_inbox(inbox_dir)
    feedback = ems.build_views.load_jsonl(feedback_path)

    valid: list[dict] = []
    invalid: list[dict] = []
    for rec in raw:
        reason = validate(rec)
        if reason:
            invalid.append({"reason": reason, "record": rec})
        else:
            valid.append(rec)

    metrics = collect_metrics(valid, feedback, today=today)
    prior = prior or {}
    promoted_dates = promoted_dates or {}
    snapshots = snapshots or {}
    resolved = resolved or set()
    today_str = (today or datetime.now(timezone.utc).date()).isoformat()

    tally = {"observed": 0, "candidate": 0, "promoted": 0, "deprecated": 0, "archived": 0}
    decisions: dict[str, dict] = {}
    new_events: list[dict] = []
    review: dict[str, list[dict]] = {
        "conflicting": [], "risky": [], "superseding": [], "promotion-review": [],
    }

    for mid in sorted(metrics):
        m = metrics[mid]
        tier, awaiting, bucket = derive_observation_tier(m)
        was = prior.get(mid, "observed")

        # Deep conflict / authority protection (detect-and-hold; locked policy). A memory
        # that is already PROMOTED is authoritative: new evidence may not silently
        # downgrade or rewrite it. If its directive drifted from the promotion snapshot,
        # or current signals would deprecate it, we KEEP it promoted and propose a
        # supersede for human review — never auto-downgrade. (frequency never auto-PROMOTES;
        # by the same invariant, new evidence never auto-SUPERSEDES.)
        supersede = None
        if was == "promoted":
            snap = snapshots.get(mid)
            drifted = snap is not None and m["directive_hash"] != snap.get("directive_hash")
            contradicted = m["not_helped"] > 0
            # A promoted memory STAYS promoted (authoritative) no matter what the base policy
            # recomputes — it is never auto-downgraded (so a human-promoted co-change memory,
            # whose base tier is only "candidate", is not bogusly demoted). Propose a supersede
            # only on a real conflict (directive drift or negative feedback), and only when a
            # human has not already resolved THIS exact conflict (same current directive hash).
            if (drifted or contradicted) and (mid, m["directive_hash"]) not in resolved:
                trigger = "directive-drift" if drifted else "negative-feedback"
                supersede = _supersede_proposal(mid, m, snap, trigger)
            tier, awaiting, bucket = "promoted", False, None  # hold authority; supersede handles routing

        tally[tier] += 1
        reason = _reason(m, tier)

        promoted_at = promoted_dates.get(mid, today_str) if tier == "promoted" else None
        rec = ems.build_score_record(mid, m, tier, promoted_at)   # REUSED shape
        rec["factors"]["recency"] = m["recency"]                  # Slice 1 left this 0; we measure it
        rec["ebms_state"] = ebms_state(tier, bucket)
        rationale = tier_rationale(m)
        if supersede:
            rationale = [
                "Held (supersede proposed): promoted memory is authoritative; new evidence "
                f"diverges ({supersede['trigger']}) and awaits human resolution.",
                *rationale,
            ]
        decisions[mid] = {
            "tier": tier, "ebms_state": rec["ebms_state"], "awaiting": awaiting, "bucket": bucket, "reason": reason,
            "rationale": rationale, "score_record": rec,
            "risk_level": m["risk_level"], "score": m["score"], "supersede": supersede,
            "directive": m["directive"], "directive_hash": m["directive_hash"],
        }

        if supersede:
            review["superseding"].append(supersede)
        elif bucket:
            review[bucket].append({
                "memory_id": mid, "tier": tier, "score": m["score"],
                "risk_level": m["risk_level"], "reason": m.get("risk_reason") or reason,
                "observed_by": m["observed_by"],
            })

        if tier != was:
            ev = ems.build_promotion_event(mid, m, was, tier)    # REUSED shape (sets from/to)
            ev["reason"] = reason                                 # observation-track reason
            new_events.append(ev)

    summary = {
        "observations": len(raw),
        "valid": len(valid),
        "invalid": len(invalid),
        "memories": len(metrics),
        "tally": tally,
        "new_events": len(new_events),
        "review": {b: len(items) for b, items in review.items()},
    }
    return {
        "summary": summary, "decisions": decisions, "metrics": metrics,
        "invalid": invalid, "review": review, "new_events": new_events,
    }


def run(
    inbox_dir: Path, out: Path, *, feedback_path: Path = ems.FEEDBACK,
    today: date | None = None, dry_run: bool = False,
) -> dict:
    """Score the real observation inbox, auto-move tiers, route exceptions to review,
    and (unless ``dry_run``) persist scores/promotions/review/report into ``out``.
    Returns the summary dict. Writes only into ``out`` (isolated, local-only namespace)."""
    promotions = _promotions_path(out)
    prior = _last_known_tiers(promotions)
    promoted_dates = _first_promoted_dates(promotions)
    snapshots = _load_snapshots(out)
    resolved = _load_resolved_supersedes(out)
    result = evaluate(
        inbox_dir, feedback_path=feedback_path, prior=prior,
        promoted_dates=promoted_dates, snapshots=snapshots, resolved=resolved, today=today,
    )
    if dry_run:
        return result["summary"]

    scores_dir = _scores_dir(out)
    scores_dir.mkdir(parents=True, exist_ok=True)
    promotions.parent.mkdir(parents=True, exist_ok=True)
    for mid, d in result["decisions"].items():
        (scores_dir / f"{_safe(mid)}.json").write_text(
            json.dumps(d["score_record"], indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
    if result["new_events"]:
        with promotions.open("a", encoding="utf-8") as fh:
            for ev in result["new_events"]:
                fh.write(json.dumps(ev, ensure_ascii=False) + "\n")
    _append_review(out, "invalid", [{**r, "queued_at": ems._now()} for r in result["invalid"]])
    for bucket in ("conflicting", "risky", "promotion-review"):  # superseding has its own log
        _append_review(out, bucket, [{**it, "queued_at": ems._now()} for it in result["review"][bucket]])
    _append_supersede_proposals(out, result["review"]["superseding"])
    _capture_snapshots(out, result["decisions"], snapshots, promoted_dates, today)
    _write_report(out, result["metrics"], result["summary"], result["invalid"],
                  result["new_events"], result["review"])
    return result["summary"]


def _append_supersede_proposals(out: Path, proposals: list[dict]) -> None:
    """Append-only audit of deep-conflict supersede proposals, deduped by
    (memory_id, current_hash) so an unresolved conflict is not re-logged every run."""
    if not proposals:
        return
    path = _supersede_path(out)
    seen: set[tuple[str, str]] = set()
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                try:
                    p = json.loads(line)
                except ValueError:
                    continue
                seen.add((p.get("memory_id", ""), p.get("current_hash", "")))
    fresh = [p for p in proposals if (p["memory_id"], p["current_hash"]) not in seen]
    if not fresh:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        for p in fresh:
            fh.write(json.dumps({**p, "queued_at": ems._now()}, ensure_ascii=False) + "\n")


def _capture_snapshots(
    out: Path, decisions: dict[str, dict], snapshots: dict[str, dict],
    promoted_dates: dict[str, str], today: date | None,
) -> None:
    """Snapshot the directive of each promoted memory that has no snapshot yet (capture at
    first promotion; backfills legacy promoted memories). Immutable until a human resolves
    a conflict — never overwritten here, so drift is always measured against the promotion."""
    today_str = (today or datetime.now(timezone.utc).date()).isoformat()
    for mid, dec in decisions.items():
        if dec["tier"] != "promoted" or mid in snapshots:
            continue
        _write_snapshot_file(out, mid, dec["directive"], dec["directive_hash"],
                             promoted_dates.get(mid, today_str))


def record_promotion(out: Path, mid: str, m: dict, from_tier: str, directive: str,
                     directive_hash: str, *, reason: str, today: date | None = None) -> dict:
    """Persist a HUMAN promotion decision: append a promotion-event.v1 (from_tier -> promoted)
    and capture the directive snapshot so future drift is measured against it. Used by the
    operator CLI to action the promotion-review queue — co-change never auto-promotes."""
    today_str = (today or datetime.now(timezone.utc).date()).isoformat()
    ev = ems.build_promotion_event(mid, m, from_tier, "promoted")
    ev["reason"] = reason
    promotions = _promotions_path(out)
    promotions.parent.mkdir(parents=True, exist_ok=True)
    with promotions.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(ev, ensure_ascii=False) + "\n")
    _write_snapshot_file(out, mid, directive, directive_hash, today_str)
    return ev


def _append_review(out: Path, bucket: str, items: list[dict]) -> None:
    if not items:
        return
    path = _review_path(out, bucket)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        for it in items:
            fh.write(json.dumps(it, ensure_ascii=False) + "\n")


def _write_report(out: Path, metrics, summary, invalid, new_events, review) -> None:
    lines = [
        "<!-- GENERATED by memory/commands/emit_generic_score.py — Phase 12E generic engine. -->",
        "<!-- Local-only/gitignored — never committed, never published. -->",
        "",
        "# Generic memory-score report (Phase 12E)",
        "",
        f"_Generated {ems._now()} · automatic by default; human review only for exceptions (ADR-008)._",
        "",
        "## Summary",
        "",
        f"- Observations read: {summary['observations']} "
        f"(valid: {summary['valid']}, invalid: {summary['invalid']})",
        f"- Distinct memories: {summary['memories']}",
        f"- Observed: {summary['tally']['observed']} · Candidate: {summary['tally']['candidate']} "
        f"· Promoted: {summary['tally']['promoted']} · Deprecated: {summary['tally']['deprecated']}",
        f"- Promotion events this run: {summary['new_events']}",
        f"- Held for human review — conflicting: {summary['review']['conflicting']}, "
        f"risky: {summary['review']['risky']}, superseding: {summary['review']['superseding']}, "
        f"promotion-review: {summary['review']['promotion-review']}, invalid: {summary['invalid']}",
        "",
        "## Per-memory",
        "",
        "| memory_id | tier | freq | reuse | conf | rec | sources | risk |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for mid in sorted(metrics):
        m = metrics[mid]
        tier, _, _ = derive_observation_tier(m)
        lines.append(
            f"| {mid} | {tier} | {m['frequency']} | {m['reuse']} | {m['confidence']:.2f} | "
            f"{m['recency']:.2f} | {m['source_count']} | {m['risk_level']} |"
        )
    lines += ["", "## Promotion events this run", ""]
    if new_events:
        lines += [f"- `{e['memory_id']}`: {e['from']} → {e['to']} — {e['reason']}" for e in new_events]
    else:
        lines.append("_None — no tier changed since the last run._")

    held = (review["conflicting"] + review["risky"]
            + review["superseding"] + review["promotion-review"])
    if held or invalid:
        lines += ["", "## Held for human review (the only exceptions)", ""]
        for it in review["risky"]:
            lines.append(f"- ⚠️ risky `{it['memory_id']}` ({it['risk_level']}): {it['reason']}")
        for it in review["promotion-review"]:
            lines.append(f"- ⬆️ promotion-review `{it['memory_id']}`: {it['reason']}")
        for it in review["conflicting"]:
            lines.append(f"- ⚔️ conflicting `{it['memory_id']}`: {it['reason']}")
        for it in review["superseding"]:
            lines.append(
                f"- 🔁 supersede proposed `{it['memory_id']}` ({it['trigger']}): "
                f"promoted=\"{it['promoted_directive']}\" → current=\"{it['current_directive']}\""
            )
        for it in invalid:
            lines.append(f"- 🚫 invalid: {it['reason']}")
    lines.append("")
    _report_path(out).write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    summary = run(INBOX_DIR, OUT)
    r = summary["review"]
    print(
        f"generic engine: {summary['observations']} observations "
        f"({summary['valid']} valid, {summary['invalid']} invalid) "
        f"-> {summary['memories']} memories "
        f"(observed={summary['tally']['observed']} candidate={summary['tally']['candidate']} "
        f"promoted={summary['tally']['promoted']} deprecated={summary['tally']['deprecated']}), "
        f"{summary['new_events']} promotion-event.v1, "
        f"review[conflicting={r['conflicting']} risky={r['risky']} "
        f"superseding={r['superseding']} promotion-review={r['promotion-review']}]"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
