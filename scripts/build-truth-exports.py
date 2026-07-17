#!/usr/bin/env python3
"""Materialize the canonical export bundle from mqobsidian-owned state.

Builds the five surfaces consumers read — the index plus inbox, score,
evidence, and policy manifests — into a temporary directory, validates every
document, and only then replaces `exports/` atomically. A failed validation
leaves the previous bundle untouched.

`exports/truth-export-index.json` is the single well-known entrypoint; every
other surface is discovered from it and stays vault-relative.

Sources (mqobsidian-owned):
  memory/local/observation-scoring/scores/*.json -> memory-score.v1 records
  memory/observations/*.jsonl       -> memory-observation.v1 records (evidence)
  memory/promotion-policy.json      -> promotion-policy.v1 weights/thresholds

Evidence is sanitized: only producer, kind, candidate, timestamp, and a summary
are published. Raw excerpts and source references are dropped because they carry
file paths and private context.
"""

from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
# The live scoring engine writes here (emit_generic_score.OUT / "scores"). A
# parallel `memory/scores` directory holds a dead snapshot from an older scoring
# scale; reading it publishes stale truth that still validates.
SCORES_DIR = ROOT / "memory" / "local" / "observation-scoring" / "scores"
OBSERVATIONS_DIR = ROOT / "memory" / "observations"
POLICY_SOURCE = ROOT / "memory" / "promotion-policy.json"
EXPORTS = ROOT / "exports"

SOURCE_ID = "mqobsidian-export"

# Only pre-promotion states belong in the inbox; anything past `candidate` has
# left it (see inbox-manifest.v1).
INBOX_STATES = {"observed", "candidate"}


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _as_datetime(value: str) -> str:
    """Widen a date (memory-score.v1) to a date-time (inbox-manifest.v1)."""
    if not value:
        return ""
    return f"{value}T00:00:00Z" if len(value) == 10 else value


def _declared_score_fields() -> set[str]:
    """The fields memory-score.v1 actually declares.

    Read from the schema rather than restated here, so a field mqobsidian adds
    to the contract is published without anyone remembering to edit this list.
    """
    schema = json.loads((ROOT / "schemas" / "memory-score.v1.json").read_text(encoding="utf-8"))
    return set(schema["properties"])


def load_scores() -> dict[str, dict[str, Any]]:
    """Load score records, projected onto the published contract.

    memory-score.v1 is `additionalProperties: false`, so an undeclared field
    makes the record invalid. The engine keeps internal state on these records
    (`ebms_state`, tied to the deferred DD-001 design), which is not ours to
    publish: exporting it would both violate the schema and freeze an undecided
    concept into a consumer contract. `validate-export.py` is stdlib-only and
    shallow, so it cannot catch this — the projection has to happen here.
    """
    declared = _declared_score_fields()
    scores: dict[str, dict[str, Any]] = {}
    for path in sorted(SCORES_DIR.glob("*.json")):
        record = json.loads(path.read_text(encoding="utf-8"))
        memory_id = record.get("memory_id")
        if not memory_id:
            raise ValueError(f"{path.name}: score record has no memory_id")
        if record.get("schema") != "memory-score.v1":
            raise ValueError(f"{path.name}: expected memory-score.v1")
        scores[memory_id] = {k: v for k, v in record.items() if k in declared}
    return scores


def load_observations() -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for path in sorted(OBSERVATIONS_DIR.glob("*.jsonl")):
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                records.append(json.loads(line))
    return records


def build_evidence(observations: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Publish sanitized evidence keyed by the ref the inbox points at."""
    evidence: dict[str, dict[str, Any]] = {}
    for record in observations:
        obs_id = record.get("id")
        candidate_id = record.get("proposed_memory_key")
        if not obs_id or not candidate_id:
            continue  # unresolvable: cannot be traced to a candidate
        ref = f"observation:{obs_id}"
        evidence[ref] = {
            "ref": ref,
            "producer": str(record.get("producer") or "unknown"),
            "schema_id": "memory-observation.v1",
            "candidate_id": candidate_id,
            "kind": "observation",
            "observed_at": str(record.get("timestamp") or ""),
            "summary": str(record.get("title") or record.get("summary") or ""),
        }
    return evidence


def build_inbox(scores: dict[str, dict[str, Any]],
                evidence: dict[str, dict[str, Any]], generated_at: str) -> dict[str, Any]:
    by_candidate: dict[str, list[str]] = {}
    for ref, record in evidence.items():
        by_candidate.setdefault(record["candidate_id"], []).append(ref)

    items: list[dict[str, Any]] = []
    for memory_id, score in sorted(scores.items()):
        if score.get("status") not in INBOX_STATES:
            continue
        refs = sorted(by_candidate.get(memory_id, []))
        observed_by = score.get("observed_by") or []
        item: dict[str, Any] = {
            "id": memory_id,
            "source": str(observed_by[0]) if observed_by else "mqobsidian",
            "state": score["status"],
            "first_seen": _as_datetime(str(score.get("first_seen") or "")),
            "last_seen": _as_datetime(str(score.get("last_seen") or "")),
        }
        # occurrences is how many times the candidate was observed — the count of
        # supporting evidence, not the frequency factor.
        if refs:
            item["occurrences"] = len(refs)
            item["evidence"] = [{"ref": ref, "kind": "observation"} for ref in refs]
        if isinstance(score.get("score"), (int, float)):
            item["score"] = score["score"]
        items.append(item)

    return {
        "schema": "inbox-manifest.v1",
        "source": SOURCE_ID,
        "generated_at": generated_at,
        "items": items,
    }


def build_score_manifest(scores: dict[str, dict[str, Any]], generated_at: str) -> dict[str, Any]:
    return {
        "schema": "memory-score-manifest.v1",
        "source": SOURCE_ID,
        "generated_at": generated_at,
        "scores": dict(sorted(scores.items())),
    }


def build_evidence_manifest(evidence: dict[str, dict[str, Any]], generated_at: str) -> dict[str, Any]:
    return {
        "schema": "memory-evidence-manifest.v1",
        "source": SOURCE_ID,
        "generated_at": generated_at,
        "evidence": dict(sorted(evidence.items())),
    }


def _display(path: Path) -> str:
    """Repo-relative when possible; never let path formatting mask a real error."""
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def build_policy(generated_at: str) -> dict[str, Any]:
    if not POLICY_SOURCE.exists():
        raise ValueError(
            f"missing policy source {_display(POLICY_SOURCE)}; "
            "weights and thresholds are vault data and are never defaulted in code"
        )
    policy = json.loads(POLICY_SOURCE.read_text(encoding="utf-8"))
    policy["source"] = SOURCE_ID
    policy["generated_at"] = generated_at
    return policy


def build_index(surfaces: list[dict[str, Any]], generated_at: str) -> dict[str, Any]:
    return {
        "schema": "truth-export-index.v1",
        "source": SOURCE_ID,
        "generated_at": generated_at,
        "surfaces": surfaces,
    }


def _write(directory: Path, name: str, payload: dict[str, Any]) -> None:
    path = directory / name
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def build_bundle(directory: Path, generated_at: str | None = None) -> dict[str, Any]:
    """Build all five documents into `directory`. Returns the index payload."""
    stamp = generated_at or _now()
    scores = load_scores()
    observations = load_observations()
    evidence = build_evidence(observations)

    inbox = build_inbox(scores, evidence, stamp)
    score_manifest = build_score_manifest(scores, stamp)
    evidence_manifest = build_evidence_manifest(evidence, stamp)
    policy = build_policy(stamp)

    _write(directory, "inbox-manifest.json", inbox)
    _write(directory, "memory-score-manifest.json", score_manifest)
    _write(directory, "memory-evidence-manifest.json", evidence_manifest)
    _write(directory, "promotion-policy.json", policy)

    surfaces = [
        {
            "key": "inbox",
            "schema": "inbox-manifest.v1",
            "path": "exports/inbox-manifest.json",
            "generated_at": stamp,
            "drift": False,
            "record_count": len(inbox["items"]),
            "description": "promotion inbox candidates",
        },
        {
            "key": "scores",
            "schema": "memory-score-manifest.v1",
            "path": "exports/memory-score-manifest.json",
            "generated_at": stamp,
            "drift": False,
            "record_count": len(score_manifest["scores"]),
            "description": "current promotion score records",
        },
        {
            "key": "evidence",
            "schema": "memory-evidence-manifest.v1",
            "path": "exports/memory-evidence-manifest.json",
            "generated_at": stamp,
            "drift": False,
            "record_count": len(evidence_manifest["evidence"]),
            "description": "sanitized promotion evidence",
        },
        {
            "key": "promotion-policy",
            "schema": "promotion-policy.v1",
            "path": "exports/promotion-policy.json",
            "generated_at": stamp,
            "drift": False,
            "record_count": 1,
            "description": "promotion ranking weights and review thresholds",
        },
    ]
    index = build_index(surfaces, stamp)
    _write(directory, "truth-export-index.json", index)
    return index


def validate_bundle(directory: Path) -> list[str]:
    """Validate every built document before it is allowed to replace exports/."""
    sys.path.insert(0, str(ROOT / "scripts"))
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "validate_export", ROOT / "scripts" / "validate-export.py"
    )
    if spec is None or spec.loader is None:
        return ["cannot load validate-export.py"]
    validator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(validator)
    # The validator reports paths relative to its ROOT; point it at the staging
    # directory so it can describe documents that do not live in the repo yet.
    validator.ROOT = directory  # type: ignore[attr-defined]

    schemas = {
        name: json.loads((ROOT / "schemas" / f"{name}.json").read_text(encoding="utf-8"))
        for name in (
            "inbox-manifest.v1",
            "memory-score-manifest.v1",
            "memory-evidence-manifest.v1",
            "promotion-policy.v1",
            "truth-export-index.v1",
        )
    }

    problems: list[str] = []
    checks = [
        ("inbox-manifest.json", "inbox-manifest.v1", None, None),
        ("memory-score-manifest.json", "memory-score-manifest.v1", "scores", "memory_id"),
        ("memory-evidence-manifest.json", "memory-evidence-manifest.v1", "evidence", "ref"),
        ("promotion-policy.json", "promotion-policy.v1", None, None),
        ("truth-export-index.json", "truth-export-index.v1", None, None),
    ]
    for filename, schema_id, map_key, identity_key in checks:
        path = directory / filename
        if not path.exists():
            problems.append(f"{filename}: not built")
            continue
        if map_key and identity_key:
            problems.extend(
                validator.validate_keyed_manifest(path, schemas[schema_id], map_key, identity_key)
            )
        else:
            problems.extend(validator.validate_manifest_example(path, schemas[schema_id]))

    index_path = directory / "truth-export-index.json"
    if index_path.exists():
        problems.extend(validator.validate_promotion_index_mapping(index_path))
    return problems


def rebuild() -> list[str]:
    """Build, validate, and atomically swap in the bundle.

    Returns the validation problems; an empty list means `exports/` now holds a
    validated bundle. On any problem the previous bundle is left untouched, so a
    caller can treat a non-empty result as "published truth did not change".
    """
    staging: Path | None = Path(tempfile.mkdtemp(prefix="mqobsidian-exports-"))
    try:
        assert staging is not None
        build_bundle(staging)
        problems = validate_bundle(staging)
        if problems:
            return problems

        # Atomic-enough replace: swap the validated bundle in, then drop the old one.
        previous = EXPORTS.with_name("exports.previous")
        if previous.exists():
            shutil.rmtree(previous)
        if EXPORTS.exists():
            os.replace(EXPORTS, previous)
        os.replace(staging, EXPORTS)
        staging = None  # consumed by the replace
        if previous.exists():
            shutil.rmtree(previous)
    finally:
        if staging is not None and staging.exists():
            shutil.rmtree(staging)
    return []


def mark_drift() -> None:
    """Set `drift: true` on every surface in the index, atomically.

    The last resort: published truth could not be rebuilt and could not be
    rolled back, so the index must say so rather than keep asserting freshness.
    Written via a temp file + replace, because a half-written index would be
    worse than a drifted one.
    """
    index_path = EXPORTS / "truth-export-index.json"
    if not index_path.exists():
        raise ValueError(f"cannot mark drift: {_display(index_path)} does not exist")
    index = json.loads(index_path.read_text(encoding="utf-8"))
    for surface in index.get("surfaces", []):
        surface["drift"] = True
    handle = tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=str(EXPORTS), prefix=".index-", suffix=".json", delete=False
    )
    try:
        with handle:
            handle.write(json.dumps(index, indent=2, ensure_ascii=False) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(handle.name, index_path)
    except BaseException:
        Path(handle.name).unlink(missing_ok=True)
        raise


def main() -> int:
    problems = rebuild()
    if problems:
        print("export build failed validation; exports/ left unchanged:")
        for problem in problems:
            print(f"  - {problem}")
        return 1

    built = sorted(p.name for p in EXPORTS.glob("*.json"))
    print(f"built {len(built)} canonical surfaces into exports/:")
    for name in built:
        print(f"  - {name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
