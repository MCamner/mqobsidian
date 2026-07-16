"""Tests for the canonical export bundle builder (v1.22 Task 3)."""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _builder_module():
    spec = importlib.util.spec_from_file_location(
        "build_truth_exports", ROOT / "scripts" / "build-truth-exports.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _seed(module, root: Path) -> None:
    """Point the builder at fixture sources.

    memory/ is private vault data and gitignored, so it does not exist in CI.
    Tests must never read it: they seed their own sources instead.
    """
    scores = root / "scores"
    observations = root / "observations"
    scores.mkdir(parents=True, exist_ok=True)
    observations.mkdir(parents=True, exist_ok=True)

    (scores / "cand-1.json").write_text(json.dumps({
        "schema": "memory-score.v1", "memory_id": "cand-1",
        "timestamp": "2026-07-16T00:00:00Z", "status": "candidate", "score": 0.72,
        "factors": {"frequency": 1.0, "source_count": 2.0, "confidence": 0.5,
                    "recency": 1.0, "usage_score": 0.0, "manual_boost": 0.0},
        "observed_by": ["repo-signal"], "feedback": {"positive": 1, "negative": 0},
        "first_seen": "2026-07-01", "last_seen": "2026-07-15",
    }), encoding="utf-8")
    (scores / "promoted-1.json").write_text(json.dumps({
        "schema": "memory-score.v1", "memory_id": "promoted-1",
        "timestamp": "2026-07-16T00:00:00Z", "status": "promoted", "score": 0.9,
        "first_seen": "2026-06-01", "last_seen": "2026-07-01",
    }), encoding="utf-8")
    (observations / "seed.observations.jsonl").write_text(json.dumps({
        "schema": "memory-observation.v1", "id": "obs-1", "producer": "claude",
        "proposed_memory_key": "cand-1", "timestamp": "2026-07-15T12:00:00Z",
        "title": "A reusable pattern", "repository": "mq-agent",
        "evidence": [{"excerpt": "x", "reference": "docs/a.md line 1", "source": "claude"}],
    }) + "\n", encoding="utf-8")

    policy = root / "promotion-policy.json"
    policy.write_text(json.dumps({
        "schema": "promotion-policy.v1", "source": "mqobsidian",
        "generated_at": "2026-07-16T00:00:00Z",
        "weights": {"frequency": 0.15, "source_count": 0.2, "confidence": 0.25,
                    "recency": 0.15, "usage_score": 0.2, "manual_boost": 0.05},
        "review_threshold": 0.55, "auto_threshold": 0.8,
        "min_supporting_factors": 2, "block_negative_feedback": True,
        "max_manifest_age_seconds": 86400,
    }), encoding="utf-8")

    module.SCORES_DIR = scores
    module.OBSERVATIONS_DIR = observations
    module.POLICY_SOURCE = policy


class BuildTruthExportsTests(unittest.TestCase):
    def test_builds_five_surfaces_that_validate(self) -> None:
        module = _builder_module()
        with tempfile.TemporaryDirectory() as directory:
            staging = Path(directory) / "staging"
            staging.mkdir()
            _seed(module, Path(directory) / "src")
            module.build_bundle(staging, generated_at="2026-07-16T00:00:00Z")
            built = sorted(p.name for p in staging.glob("*.json"))
            self.assertEqual(
                built,
                [
                    "inbox-manifest.json",
                    "memory-evidence-manifest.json",
                    "memory-score-manifest.json",
                    "promotion-policy.json",
                    "truth-export-index.json",
                ],
            )
            self.assertEqual(module.validate_bundle(staging), [])

    def test_output_is_byte_valid_json_with_trailing_newline(self) -> None:
        module = _builder_module()
        with tempfile.TemporaryDirectory() as directory:
            staging = Path(directory) / "staging"
            staging.mkdir()
            _seed(module, Path(directory) / "src")
            module.build_bundle(staging, generated_at="2026-07-16T00:00:00Z")
            for path in staging.glob("*.json"):
                raw = path.read_text(encoding="utf-8")
                self.assertTrue(raw.endswith("\n"), f"{path.name} has no trailing newline")
                json.loads(raw)

    def test_index_lists_every_built_surface_with_counts(self) -> None:
        module = _builder_module()
        with tempfile.TemporaryDirectory() as directory:
            staging = Path(directory) / "staging"
            staging.mkdir()
            _seed(module, Path(directory) / "src")
            index = module.build_bundle(staging, generated_at="2026-07-16T00:00:00Z")
            keys = {s["key"] for s in index["surfaces"]}
            self.assertEqual(keys, {"inbox", "scores", "evidence", "promotion-policy"})
            for surface in index["surfaces"]:
                self.assertTrue((staging / Path(surface["path"]).name).exists())
                self.assertIsInstance(surface["record_count"], int)
                self.assertIn("generated_at", surface)
                self.assertIn("drift", surface)

    def test_evidence_is_sanitized_and_carries_no_paths(self) -> None:
        module = _builder_module()
        observations = [
            {
                "id": "obs-1",
                "producer": "claude",
                "proposed_memory_key": "cand-1",
                "timestamp": "2026-07-15T12:00:00Z",
                "title": "A reusable pattern",
                "evidence": [
                    {
                        "excerpt": "secret excerpt",
                        "reference": "/Users/someone/private/notes.md line 4",
                        "source": "claude",
                    }
                ],
            }
        ]
        evidence = module.build_evidence(observations)
        record = evidence["observation:obs-1"]
        self.assertEqual(record["candidate_id"], "cand-1")
        self.assertEqual(record["producer"], "claude")
        blob = json.dumps(evidence)
        self.assertNotIn("/Users/", blob)
        self.assertNotIn("secret excerpt", blob)
        self.assertNotIn("reference", blob)

    def test_unresolvable_evidence_is_omitted(self) -> None:
        module = _builder_module()
        observations = [
            {"id": "obs-1", "producer": "claude", "timestamp": "t", "title": "no candidate"},
            {"producer": "claude", "proposed_memory_key": "cand-1", "title": "no id"},
        ]
        self.assertEqual(module.build_evidence(observations), {})

    def test_inbox_only_holds_pre_promotion_states(self) -> None:
        module = _builder_module()
        scores = {
            "a": {"schema": "memory-score.v1", "memory_id": "a", "status": "observed",
                  "score": 1, "first_seen": "2026-07-01", "last_seen": "2026-07-02"},
            "b": {"schema": "memory-score.v1", "memory_id": "b", "status": "candidate",
                  "score": 2, "first_seen": "2026-07-01", "last_seen": "2026-07-02"},
            "c": {"schema": "memory-score.v1", "memory_id": "c", "status": "promoted",
                  "score": 3, "first_seen": "2026-07-01", "last_seen": "2026-07-02"},
            "d": {"schema": "memory-score.v1", "memory_id": "d", "status": "archived",
                  "score": 4, "first_seen": "2026-07-01", "last_seen": "2026-07-02"},
        }
        inbox = module.build_inbox(scores, {}, "2026-07-16T00:00:00Z")
        self.assertEqual([item["id"] for item in inbox["items"]], ["a", "b"])

    def test_dates_are_widened_to_date_times(self) -> None:
        module = _builder_module()
        scores = {
            "a": {"schema": "memory-score.v1", "memory_id": "a", "status": "observed",
                  "score": 1, "first_seen": "2026-07-01", "last_seen": "2026-07-02"},
        }
        item = module.build_inbox(scores, {}, "2026-07-16T00:00:00Z")["items"][0]
        self.assertEqual(item["first_seen"], "2026-07-01T00:00:00Z")
        self.assertEqual(item["last_seen"], "2026-07-02T00:00:00Z")

    def test_occurrences_counts_supporting_evidence(self) -> None:
        module = _builder_module()
        scores = {
            "a": {"schema": "memory-score.v1", "memory_id": "a", "status": "candidate",
                  "score": 1, "first_seen": "2026-07-01", "last_seen": "2026-07-02"},
        }
        evidence = {
            "observation:o1": {"ref": "observation:o1", "candidate_id": "a"},
            "observation:o2": {"ref": "observation:o2", "candidate_id": "a"},
            "observation:o3": {"ref": "observation:o3", "candidate_id": "other"},
        }
        item = module.build_inbox(scores, evidence, "2026-07-16T00:00:00Z")["items"][0]
        self.assertEqual(item["occurrences"], 2)
        self.assertEqual(
            [e["ref"] for e in item["evidence"]], ["observation:o1", "observation:o2"]
        )

    def test_inbox_evidence_refs_resolve_in_the_evidence_manifest(self) -> None:
        """The join mq-agent ranking depends on must hold in real built output."""
        module = _builder_module()
        with tempfile.TemporaryDirectory() as directory:
            staging = Path(directory) / "staging"
            staging.mkdir()
            _seed(module, Path(directory) / "src")
            module.build_bundle(staging, generated_at="2026-07-16T00:00:00Z")
            inbox = json.loads((staging / "inbox-manifest.json").read_text())
            evidence = json.loads((staging / "memory-evidence-manifest.json").read_text())
            published = set(evidence["evidence"])
            for item in inbox["items"]:
                for ref in (e["ref"] for e in item.get("evidence", [])):
                    self.assertIn(ref, published, f"{item['id']} points at unpublished {ref}")

    def test_missing_policy_source_fails_loudly(self) -> None:
        module = _builder_module()
        module.POLICY_SOURCE = Path("/nonexistent/promotion-policy.json")
        with self.assertRaises(ValueError) as ctx:
            module.build_policy("2026-07-16T00:00:00Z")
        self.assertIn("never defaulted in code", str(ctx.exception))

    def test_reads_the_scores_dir_the_scorer_actually_writes(self) -> None:
        """The exporter must read live scoring output, not a parallel directory.

        `memory/scores` is a dead 2026-06-29 snapshot from an older scoring
        scale; the engine writes `memory/local/observation-scoring/scores`.
        Reading the wrong one publishes stale truth that still validates, so
        no schema check can catch it — only this assertion can.
        """
        module = _builder_module()
        self.assertEqual(
            module.SCORES_DIR,
            ROOT / "memory" / "local" / "observation-scoring" / "scores",
        )

    def test_score_source_matches_the_scoring_engine(self) -> None:
        """Cross-check the constant against the engine itself, when present.

        The engine is gitignored vault code, so this cannot run in CI — but
        locally it is the real invariant, not a restatement of the path.
        """
        commands = ROOT / "memory" / "commands"
        if not (commands / "emit_generic_score.py").exists():
            self.skipTest("scoring engine is local-only vault code; not present")
        import sys

        sys.path.insert(0, str(commands))
        try:
            import emit_generic_score as egs
        finally:
            sys.path.remove(str(commands))
        module = _builder_module()
        self.assertEqual(module.SCORES_DIR, egs._scores_dir(egs.OUT))

    def test_published_scores_carry_only_schema_declared_fields(self) -> None:
        """memory-score.v1 is `additionalProperties: false`, so publishing an
        undeclared field emits a record that violates the contract we publish.

        The live engine writes `ebms_state` (internal EBMS state, undeclared in
        every schema, example and doc). `validate-export.py` is deliberately
        shallow — stdlib-only, no jsonschema — so it enforces the top-level
        const and keys but never `additionalProperties` on nested records. It
        cannot catch this; only the producer can.
        """
        module = _builder_module()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            scores = root / "scores"
            scores.mkdir()
            (scores / "m-1.json").write_text(json.dumps({
                "schema": "memory-score.v1", "memory_id": "m-1",
                "timestamp": "2026-07-16T00:00:00Z", "status": "observed", "score": 0.9,
                "first_seen": "2026-07-01", "last_seen": "2026-07-02",
                "ebms_state": "scratch", "some_future_internal": {"x": 1},
            }), encoding="utf-8")
            module.SCORES_DIR = scores

            declared = set(json.loads(
                (ROOT / "schemas" / "memory-score.v1.json").read_text(encoding="utf-8")
            )["properties"])
            record = module.load_scores()["m-1"]
            self.assertEqual(record["memory_id"], "m-1")
            self.assertTrue(set(record) <= declared,
                            f"published undeclared fields: {sorted(set(record) - declared)}")

    def test_publishing_projection_is_driven_by_the_schema_not_a_hardcoded_list(self) -> None:
        """A field the schema declares must survive; only undeclared ones drop."""
        module = _builder_module()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            scores = root / "scores"
            scores.mkdir()
            (scores / "m-1.json").write_text(json.dumps({
                "schema": "memory-score.v1", "memory_id": "m-1",
                "timestamp": "2026-07-16T00:00:00Z", "status": "promoted", "score": 0.9,
                "factors": {"frequency": 1.0}, "observed_by": ["repo-signal"],
                "feedback": {"positive": 1, "negative": 0},
                "first_seen": "2026-07-01", "last_seen": "2026-07-02",
                "promoted_at": "2026-07-16", "ebms_state": "scratch",
            }), encoding="utf-8")
            module.SCORES_DIR = scores
            record = module.load_scores()["m-1"]
            self.assertNotIn("ebms_state", record)
            for field in ("factors", "observed_by", "feedback", "promoted_at", "first_seen"):
                self.assertIn(field, record, f"{field} is declared and must be published")

    def test_failed_validation_leaves_previous_exports_untouched(self) -> None:
        module = _builder_module()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            exports = root / "exports"
            exports.mkdir()
            sentinel = exports / "truth-export-index.json"
            sentinel.write_text('{"previous": true}', encoding="utf-8")
            module.EXPORTS = exports
            # A score record with no memory_id makes the build fail before replace.
            bad = root / "scores"
            bad.mkdir()
            (bad / "broken.json").write_text('{"schema": "memory-score.v1"}', encoding="utf-8")
            module.SCORES_DIR = bad

            with self.assertRaises(ValueError):
                module.load_scores()
            self.assertEqual(json.loads(sentinel.read_text()), {"previous": True})


if __name__ == "__main__":
    unittest.main()
