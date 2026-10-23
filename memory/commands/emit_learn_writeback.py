#!/usr/bin/env python3
"""Phase 12E §9 — learn-writeback: promote durable, agent-readable memory.

The LAST stage of the autonomous loop. When (and ONLY when) scoring has moved a
memory to `promoted`, this writer materialises one agent-readable learning file
under `memory/learn/<category>/`. Observed and candidate memories write NOTHING —
promotion is the gate, exactly as the scoring engine + ADR-008 decided.

Pipeline boundary (deliberate): scoring DECIDES, writeback CONSUMES. The promotion
decision is read from the persisted `memory-score.v1` records (status == "promoted"),
never re-derived here. Human-readable lesson text is pulled from the matching
observations and SANITISED before it lands in durable memory.

Provenance is preserved both ways: each learning file records its `source_score_id`
(memory-score.v1) and the `promotion_event` (promotion-event.v1) that promoted it, so
the durable memory is always explainable and reversible back to the evidence.

Safety (checklist §9 acceptance): no secrets, no raw stdout, no prompts, and no
absolute private paths ever reach a learning file — `_sanitize` redacts known token
shapes and rewrites absolute paths to their basename. Output is local-only/gitignored;
promotion is NOT publication (public export stays a separate, gated step).

Idempotent: filenames are deterministic (`<memory_key>.md`) and content is stable
(timestamps come from the stable `promoted_at`, never `now()`), so re-running rewrites
nothing that has not actually changed.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import emit_generic_score as egs

HERE = Path(__file__).resolve().parent
MEMORY = HERE.parent

SCORES_DIR = egs.OUT / "scores"
PROMOTIONS = egs.OUT / "promotions" / "events.jsonl"
INBOX_DIR = egs.INBOX_DIR
LEARN_DIR = MEMORY / "learn"

# memory-observation.v1 category -> learn subdir (checklist §9 target dirs).
CATEGORY_TO_DIR = {
    "pattern": "patterns",
    "workflow": "patterns",
    "bug": "fixes",
    "architecture": "architecture",
    "decision": "architecture",
    "review": "agent",
    "prompt": "agent",
    "preference": "agent",
    "learning": "agent",
}
DEFAULT_DIR = "agent"

# Defensive secret shapes (producers already sanitise; this is belt-and-braces).
_SECRET_RE = re.compile(
    r"\b(gh[pousr]_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9]{16,}|AKIA[0-9A-Z]{16}|xox[baprs]-[A-Za-z0-9-]{8,})\b"
)
# Absolute private paths -> keep only the basename (no leaking /Users/<name>/... layouts).
_ABS_PATH_RE = re.compile(r"(/(?:Users|home|private|var|tmp|opt|etc)/[^\s\"'`)]+)")


def _sanitize(text: str) -> str:
    """Scrub secrets and absolute private paths from text bound for durable memory."""
    if not text:
        return ""
    text = _SECRET_RE.sub("[redacted-secret]", text)
    text = _ABS_PATH_RE.sub(lambda m: Path(m.group(1)).name or "[path]", text)
    return text


def _safe(memory_id: str) -> str:
    return "".join(c if (c.isalnum() or c in "-_.") else "-" for c in memory_id) or "_"


def load_promoted_scores(scores_dir: Path) -> list[dict]:
    """The promotion decision is taken from the score records, not re-derived."""
    out: list[dict] = []
    if not scores_dir.exists():
        return out
    for path in sorted(scores_dir.glob("*.json")):
        rec = json.loads(path.read_text(encoding="utf-8"))
        if rec.get("schema") == "memory-score.v1" and rec.get("status") == "promoted":
            rec["_path"] = path.name
            out.append(rec)
    return out


def observations_by_key(inbox_dir: Path) -> dict[str, list[dict]]:
    by_key: dict[str, list[dict]] = {}
    for o in egs.load_inbox(inbox_dir):
        if "_raw" in o:
            continue
        key = o.get("proposed_memory_key") or o.get("id")
        if key:
            by_key.setdefault(key, []).append(o)
    return by_key


def promotion_event_id(promotions_path: Path, memory_id: str) -> str:
    """Latest promotion-event.v1 id whose `to == promoted` for this memory (audit link)."""
    found = ""
    if promotions_path.exists():
        for line in promotions_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            ev = json.loads(line)
            if ev.get("memory_id") == memory_id and ev.get("to") == "promoted":
                found = ev.get("id", "")
    return found


def build_learning(score: dict, observations: list[dict], promo_event_id: str) -> tuple[str, str, str]:
    """Pure: (subdir, filename, markdown). Lesson text is sanitised; provenance is
    linked back to memory-score.v1 + promotion-event.v1."""
    key = score["memory_id"]
    category = next((c for o in observations if (c := o.get("category"))), "learning")
    subdir = CATEGORY_TO_DIR.get(category, DEFAULT_DIR)
    title = _sanitize(next((t for o in observations if (t := o.get("title"))), key))

    lessons, sources = [], []
    for o in observations:
        obs_text = _sanitize(o.get("observation", ""))
        if obs_text and obs_text not in lessons:
            lessons.append(obs_text)
        for ev in o.get("evidence", []):
            src = ev.get("source", "")
            ref = _sanitize(ev.get("reference", ""))
            tag = f"{src}" + (f" ({ref})" if ref else "")
            if tag and tag not in sources:
                sources.append(tag)

    tags = sorted({t for o in observations for t in o.get("tags", []) if isinstance(t, str)})
    factors = score.get("factors", {})
    promoted_at = score.get("promoted_at", score.get("last_seen", ""))
    observed_by = score.get("observed_by", [])

    fm = [
        "---",
        "schema_version: learn.v1",
        "written_by: mqobsidian/emit_learn_writeback (§9 learn-writeback)",
        "status: promoted",
        f"memory_key: {key}",
        f"source_score_id: {key}",
        f"source_score: memory/local/observation-scoring/scores/{score['_path']}",
        f"promotion_event: {promo_event_id}",
        f"score: {score.get('score')}",
        f"category: {category}",
        f"promoted_at: {promoted_at}",
        f"observed_by: {observed_by}",
        f"tags: {tags}",
        "---",
    ]
    body = [
        "",
        f"# Promoted memory: {title}",
        "",
        "> Auto-written by mqobsidian §9 learn-writeback when scoring promoted this memory.",
        "> Local-only. Source of truth: memory-score.v1 + promotion-event.v1 (do not edit by hand).",
        "",
        "## Lesson",
        "",
    ]
    body += [f"- {line}" for line in lessons] or ["- (no observation text recorded)"]
    body += [
        "",
        "## Provenance",
        "",
        f"- memory_key: `{key}`",
        f"- score: `{score.get('score')}` · status: `promoted` · promoted_at: `{promoted_at}`",
        f"- factors: frequency={factors.get('frequency')}, source_count={factors.get('source_count')}, "
        f"confidence={factors.get('confidence')}, recency={factors.get('recency')}",
        f"- observed_by: {', '.join(observed_by) or '—'}",
        f"- source score record: `memory/local/observation-scoring/scores/{score['_path']}`",
        f"- promotion event: `{promo_event_id or '—'}`",
        f"- evidence sources: {', '.join(sources) or '—'}",
        "",
    ]
    return subdir, f"{_safe(key)}.md", "\n".join(fm + body)


def writeback(
    *, scores_dir: Path = SCORES_DIR, inbox_dir: Path = INBOX_DIR,
    promotions_path: Path = PROMOTIONS, learn_dir: Path = LEARN_DIR, dry_run: bool = False,
) -> dict:
    """Materialise one learning file per PROMOTED memory. Idempotent: unchanged files
    are left untouched. Returns a summary. Writes only under ``learn_dir``."""
    promoted = load_promoted_scores(scores_dir)
    obs_by_key = observations_by_key(inbox_dir)

    written, unchanged, files, details = 0, 0, [], []
    for score in promoted:
        key = score["memory_id"]
        subdir, fname, content = build_learning(
            score, obs_by_key.get(key, []), promotion_event_id(promotions_path, key)
        )
        rel = f"{subdir}/{fname}"
        files.append(rel)
        target = learn_dir / subdir / fname
        if target.exists() and target.read_text(encoding="utf-8") == content:
            status = "unchanged"
            unchanged += 1
        else:
            if not dry_run:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(content, encoding="utf-8")
            status = "would-write" if dry_run else "written"
            written += 1
        details.append({"memory_key": key, "category": subdir, "rel": rel, "status": status})

    return {"promoted": len(promoted), "written": written, "unchanged": unchanged,
            "files": files, "details": details}


def main() -> int:
    s = writeback()
    print(
        f"learn-writeback: {s['promoted']} promoted memories -> "
        f"{s['written']} written, {s['unchanged']} unchanged"
    )
    for d in s["details"]:
        print(f"  [{d['category']}] learn/{d['rel']}  ({d['status']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
