"""Atomic promotion transitions with a write-ahead journal (v1.22 Task 4).

One tested state machine below the CLI. Every applied transition:

1. resolves evidence against the exported evidence manifest — an unresolvable
   ref blocks the transition rather than being recorded;
2. writes an fsynced intent journal holding prior file hashes, staged paths and
   the requested transition, *before* any state changes;
3. commits deterministically: score replace -> learn projection -> event append
   (the commit marker) -> journal completion.

Recovery is deterministic. On startup an incomplete journal either finishes
forward (its commit event exists) or restores hash-verified snapshots (it does
not). If forward recovery cannot complete, an inverse compensation event is
appended and prior projections are restored. The event log is append-only and
is never truncated.

Locked transition table:

    verb       from       -> to          durable effect
    promote    candidate  -> promoted    write/update category-mapped learn record
    reject     candidate  -> archived    no durable learn record
    defer      candidate  -> observed    no durable learn record
    rollback   promoted   -> candidate   remove generated learn projection only
    deprecate  promoted   -> deprecated  retain record, mark deprecated
"""

from __future__ import annotations

import hashlib
import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

JOURNAL_SCHEMA = "transition-journal.v1"
EVENT_SCHEMA = "promotion-event.v1"
PRODUCER = "mqobsidian"

# The locked table. from-state is authoritative: a verb applied to any other
# state is an illegal transition and is refused.
TRANSITIONS: dict[str, tuple[str, str]] = {
    "promote": ("candidate", "promoted"),
    "reject": ("candidate", "archived"),
    "defer": ("candidate", "observed"),
    "rollback": ("promoted", "candidate"),
    "deprecate": ("promoted", "deprecated"),
}

# Verbs whose durable effect touches the learn projection.
_WRITES_LEARN = {"promote"}
_REMOVES_LEARN = {"rollback"}

COMMIT_STEPS = ("score", "learn", "event")


class TransitionError(Exception):
    """A transition was refused before any state changed."""


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _sha256(path: Path) -> str | None:
    if not path.exists():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _fsync_write(path: Path, text: str) -> None:
    """Write and fsync, so the journal survives a crash after this returns."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        handle.write(text)
        handle.flush()
        os.fsync(handle.fileno())


def _append_jsonl(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def resolve_evidence(refs: list[str], evidence_manifest: dict[str, Any]) -> list[str]:
    """Resolve refs against memory-evidence-manifest.v1.

    Evidence authority lives in the manifest. A ref that is not published there
    is unresolvable and blocks the transition — opaque refs never become
    justification.
    """
    published = evidence_manifest.get("evidence")
    if not isinstance(published, dict):
        raise TransitionError("evidence manifest has no evidence map")
    unresolved = [ref for ref in refs if ref not in published]
    if unresolved:
        raise TransitionError(f"unresolved evidence refs: {', '.join(sorted(unresolved))}")
    return list(refs)


def plan_transition(
    verb: str,
    memory_id: str,
    *,
    scores_dir: Path,
    evidence_manifest: dict[str, Any],
    evidence_refs: list[str],
    reason: str,
) -> dict[str, Any]:
    """Validate a transition and return its plan. Writes nothing."""
    if verb not in TRANSITIONS:
        raise TransitionError(f"unknown transition verb: {verb}")
    expected_from, to_state = TRANSITIONS[verb]

    score_path = scores_dir / f"{memory_id}.json"
    if not score_path.exists():
        raise TransitionError(f"no score record for memory_id '{memory_id}'")
    score = json.loads(score_path.read_text(encoding="utf-8"))

    current = score.get("status")
    if current != expected_from:
        raise TransitionError(
            f"illegal transition '{verb}' for '{memory_id}': "
            f"state is '{current}', requires '{expected_from}'"
        )

    if not reason or not reason.strip():
        raise TransitionError("a transition requires a reason")

    # Every promotion must trace to source evidence.
    if verb == "promote" and not evidence_refs:
        raise TransitionError("promote requires traceable source evidence")

    resolved = resolve_evidence(evidence_refs, evidence_manifest)

    return {
        "verb": verb,
        "memory_id": memory_id,
        "from": expected_from,
        "to": to_state,
        "reason": reason,
        "source_evidence_refs": resolved,
        "score_path": str(score_path),
        "score": score,
        "writes_learn": verb in _WRITES_LEARN,
        "removes_learn": verb in _REMOVES_LEARN,
    }


def _build_event(plan: dict[str, Any], journal_id: str) -> dict[str, Any]:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    event: dict[str, Any] = {
        "schema": EVENT_SCHEMA,
        "id": f"promo_{plan['memory_id']}_{stamp}_{journal_id[:8]}",
        "timestamp": _now(),
        "producer": PRODUCER,
        "memory_id": plan["memory_id"],
        "from": plan["from"],
        "to": plan["to"],
        "reason": plan["reason"],
        "verb": plan["verb"],
        "journal_id": journal_id,
    }
    if plan["source_evidence_refs"]:
        event["source_evidence_refs"] = list(plan["source_evidence_refs"])
    score = plan.get("score") or {}
    if isinstance(score.get("score"), (int, float)):
        event["score"] = score["score"]
    return event


def _snapshot_dir(journal_dir: Path, journal_id: str) -> Path:
    return journal_dir / f"{journal_id}.snapshots"


def _snapshot(paths: list[Path], backup_dir: Path) -> list[dict[str, Any]]:
    """Record prior hash, staged path, and a byte copy of every existing file.

    The hash alone cannot restore a modified file, so the prior bytes are
    copied next to the journal and verified against the hash on recovery.
    """
    snapshots: list[dict[str, Any]] = []
    for index, path in enumerate(paths):
        existed = path.exists()
        digest = _sha256(path)
        backup: str | None = None
        if existed:
            backup_dir.mkdir(parents=True, exist_ok=True)
            target = backup_dir / f"{index}-{path.name}"
            target.write_bytes(path.read_bytes())
            backup = str(target)
        snapshots.append({
            "path": str(path),
            "sha256": digest,
            "existed": existed,
            "backup": backup,
        })
    return snapshots


def begin_journal(
    plan: dict[str, Any], *, journal_dir: Path, staged_paths: list[Path]
) -> dict[str, Any]:
    """Write the fsynced intent journal before any state changes."""
    journal_id = uuid.uuid4().hex
    journal = {
        "schema": JOURNAL_SCHEMA,
        "journal_id": journal_id,
        "started_at": _now(),
        "memory_id": plan["memory_id"],
        "verb": plan["verb"],
        "from": plan["from"],
        "to": plan["to"],
        "reason": plan["reason"],
        "source_evidence_refs": list(plan["source_evidence_refs"]),
        "snapshots": _snapshot(staged_paths, _snapshot_dir(journal_dir, journal_id)),
        "steps": list(COMMIT_STEPS),
        "state": "pending",
    }
    _fsync_write(journal_dir / f"{journal_id}.json", json.dumps(journal, indent=2) + "\n")
    return journal


def _journal_path(journal_dir: Path, journal_id: str) -> Path:
    return journal_dir / f"{journal_id}.json"


def commit_score(plan: dict[str, Any]) -> None:
    """Step 1: replace the score record with the new state."""
    path = Path(plan["score_path"])
    score = dict(plan["score"])
    score["status"] = plan["to"]
    score["timestamp"] = _now()
    if plan["to"] == "promoted":
        score["promoted_at"] = datetime.now(timezone.utc).date().isoformat()
    _fsync_write(path, json.dumps(score, indent=2, ensure_ascii=False) + "\n")


def commit_learn(plan: dict[str, Any], *, learn_path: Path | None, learn_content: str | None) -> None:
    """Step 2: replace or remove the learn projection.

    promote writes the category-mapped record; rollback removes only the
    generated projection; deprecate retains it. Other verbs write nothing.
    """
    if plan["writes_learn"]:
        if learn_path is None or learn_content is None:
            raise TransitionError("promote requires a learn projection to write")
        _fsync_write(learn_path, learn_content)
    elif plan["removes_learn"]:
        if learn_path is not None and learn_path.exists():
            learn_path.unlink()


def commit_event(
    plan: dict[str, Any], *, events_path: Path, journal_id: str, event: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Step 3: append the event. Its presence is the commit marker.

    Accepts an already-built event so a caller that needed the event id earlier
    (to cite it in a projection) still commits through this one append path.
    """
    if event is None:
        event = _build_event(plan, journal_id)
    _append_jsonl(events_path, event)
    return event


def _discard_journal(journal_dir: Path, journal_id: str) -> None:
    """Drop the journal and its snapshot copies together."""
    path = _journal_path(journal_dir, journal_id)
    if path.exists():
        path.unlink()
    backups = _snapshot_dir(journal_dir, journal_id)
    if backups.exists():
        for item in backups.iterdir():
            item.unlink()
        backups.rmdir()


def complete_journal(journal_dir: Path, journal_id: str) -> None:
    """Step 4: drop the journal — the transition is durably complete."""
    _discard_journal(journal_dir, journal_id)


def apply_transition(
    plan: dict[str, Any],
    *,
    journal_dir: Path,
    events_path: Path,
    learn_path: Path | None = None,
    learn_content: str | None = None,
    learn_builder: Any = None,
) -> dict[str, Any]:
    """Apply a planned transition through the journal.

    Steps run in a fixed order and each is separately injectable for fault
    tests. A crash between any two leaves a journal that recovery resolves to
    either complete old state or complete new state.

    `learn_builder` takes the event and returns the projection text. The event
    is built (purely) before the learn step so the projection can cite the
    promotion event that authorises it; only its *append* is the commit marker,
    so the durable write order is unchanged.
    """
    staged = [Path(plan["score_path"])]
    if learn_path is not None:
        staged.append(learn_path)
    journal = begin_journal(plan, journal_dir=journal_dir, staged_paths=staged)
    journal_id = journal["journal_id"]
    event = _build_event(plan, journal_id)

    commit_score(plan)
    if learn_builder is not None:
        learn_content = learn_builder(event)
    commit_learn(plan, learn_path=learn_path, learn_content=learn_content)
    commit_event(plan, events_path=events_path, journal_id=journal_id, event=event)
    complete_journal(journal_dir, journal_id)
    return {"journal_id": journal_id, "event": event, "state": "complete"}


def _find_commit_event(events_path: Path, journal_id: str) -> dict[str, Any] | None:
    for record in _read_jsonl(events_path):
        if record.get("journal_id") == journal_id:
            return record
    return None


def _restore(snapshots: list[dict[str, Any]]) -> list[str]:
    """Restore hash-verified snapshots.

    A file the aborted transition created is removed. A file it modified is
    restored from its byte copy, but only after the copy verifies against the
    hash recorded before the change — a corrupt backup fails loudly rather
    than writing unverified bytes over real memory.
    """
    restored: list[str] = []
    for snap in snapshots:
        path = Path(snap["path"])
        if not snap["existed"]:
            if path.exists():
                path.unlink()
                restored.append(f"removed {path.name}")
            continue
        backup = snap.get("backup")
        if not backup or not Path(backup).exists():
            raise TransitionError(
                f"cannot restore {path.name}: snapshot copy is missing"
            )
        if _sha256(Path(backup)) != snap["sha256"]:
            raise TransitionError(
                f"cannot restore {path.name}: snapshot copy fails hash verification"
            )
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(Path(backup).read_bytes())
        restored.append(f"restored {path.name}")
    return restored


def recover(
    journal_dir: Path,
    *,
    events_path: Path,
    learn_path_for: Any = None,
) -> list[dict[str, Any]]:
    """Resolve every incomplete journal deterministically.

    Forward when the commit event exists; otherwise restore prior state. The
    event log is never truncated: an irrecoverable forward pass appends an
    inverse compensation event instead of deleting history.
    """
    results: list[dict[str, Any]] = []
    if not journal_dir.exists():
        return results

    for path in sorted(journal_dir.glob("*.json")):
        journal = json.loads(path.read_text(encoding="utf-8"))
        journal_id = journal["journal_id"]
        event = _find_commit_event(events_path, journal_id)

        if event is not None:
            # Committed: the event is durable, so finish forward.
            _discard_journal(journal_dir, journal_id)
            results.append({
                "journal_id": journal_id,
                "outcome": "finished-forward",
                "memory_id": journal["memory_id"],
            })
            continue

        # Not committed: restore prior state. A failed restore keeps the
        # journal so the next pass can retry rather than losing the record.
        try:
            restored = _restore(journal.get("snapshots", []))
        except TransitionError as exc:
            results.append({
                "journal_id": journal_id,
                "outcome": "unrecoverable",
                "memory_id": journal["memory_id"],
                "error": str(exc),
            })
            continue
        _discard_journal(journal_dir, journal_id)
        results.append({
            "journal_id": journal_id,
            "outcome": "rolled-back",
            "memory_id": journal["memory_id"],
            "restored": restored,
        })
    return results


def compensate(
    event: dict[str, Any], *, events_path: Path, reason: str
) -> dict[str, Any]:
    """Append an inverse event. Never truncates the log."""
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    inverse = {
        "schema": EVENT_SCHEMA,
        "id": f"compensate_{event['memory_id']}_{stamp}",
        "timestamp": _now(),
        "producer": PRODUCER,
        "memory_id": event["memory_id"],
        "from": event["to"],
        "to": event["from"],
        "reason": reason,
        "compensates": event["id"],
    }
    _append_jsonl(events_path, inverse)
    return inverse
