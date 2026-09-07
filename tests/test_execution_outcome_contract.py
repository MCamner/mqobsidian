from __future__ import annotations

import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schemas" / "mq.execution-outcome.v1.json"
EXAMPLE = ROOT / "examples" / "execution-outcome.example.json"


class ExecutionOutcomeContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        self.example = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        self.validator = Draft202012Validator(self.schema)

    def test_example_conforms_to_contract(self) -> None:
        self.assertEqual(list(self.validator.iter_errors(self.example)), [])

    def test_runtime_provenance_fields_are_required(self) -> None:
        for field in (
            "run_id",
            "runtime",
            "task_class",
            "result",
            "exit_status",
            "latency_ms",
            "recorded_at",
        ):
            with self.subTest(field=field):
                mutated = dict(self.example)
                mutated.pop(field)
                self.assertTrue(list(self.validator.iter_errors(mutated)))

    # --- runtime fingerprint (DEC-006) ------------------------------------
    #
    # Which code produced the observation. A projection of the producing
    # runtime's own identity, deliberately smaller than mq.runtime-identity.v1:
    # install type, process metadata and local paths answer a different
    # question, and comparison and policy answer a third.

    def _with_fingerprint(self, fingerprint: object) -> dict:
        return {**self.example, "runtime_fingerprint": fingerprint}

    def test_a_record_without_a_fingerprint_still_conforms(self) -> None:
        """Every record written before the field existed stays valid. Absence
        means provenance was not observed, and nothing is backfilled."""
        without = {k: v for k, v in self.example.items() if k != "runtime_fingerprint"}

        self.assertEqual(list(self.validator.iter_errors(without)), [])

    def test_each_quality_level_conforms_to_what_it_carries(self) -> None:
        for quality, version, commit in (
            ("verified", "1.28.0", "a" * 40),
            ("partial", "1.28.0", None),
            ("unknown", None, None),
        ):
            with self.subTest(quality):
                record = self._with_fingerprint(
                    {
                        "component": "mq-agent",
                        "version": version,
                        "commit": commit,
                        "identity_quality": quality,
                    }
                )
                self.assertEqual(list(self.validator.iter_errors(record)), [])

    def test_a_fingerprint_cannot_claim_more_than_it_carries(self) -> None:
        for quality, version, commit in (
            ("verified", "1.28.0", None),
            ("verified", None, "a" * 40),
            ("partial", "1.28.0", "a" * 40),
            ("unknown", "1.28.0", None),
            ("unknown", None, "a" * 40),
        ):
            with self.subTest(f"{quality} {version} {commit}"):
                record = self._with_fingerprint(
                    {
                        "component": "mq-agent",
                        "version": version,
                        "commit": commit,
                        "identity_quality": quality,
                    }
                )
                self.assertNotEqual(list(self.validator.iter_errors(record)), [])

    def test_a_commit_is_a_lowercase_git_object_name(self) -> None:
        """A trailing newline is deliberately absent from this list.

        `$` matches before a final newline in Python's `re` and not in
        ECMA-262, so what the pattern rejects there depends on the validator.
        The producers reject it outright — `usable_commit()` uses `fullmatch`
        in both mq-agent and mq-mcp, each with its own test — and stating a
        guarantee here that a JavaScript validator would keep and a Python one
        would not is worse than leaving it to the side that can hold it.
        """
        for commit in ("ABCDEF1", "not-a-sha", "abcdef", "1234567890" * 5, "a b c d e"):
            with self.subTest(commit):
                record = self._with_fingerprint(
                    {
                        "component": "mq-agent",
                        "version": "1.28.0",
                        "commit": commit,
                        "identity_quality": "verified",
                    }
                )
                self.assertNotEqual(list(self.validator.iter_errors(record)), [])

    def test_a_fingerprint_needs_a_subject(self) -> None:
        """A commit without a component names nothing."""
        record = self._with_fingerprint(
            {"version": "1.28.0", "commit": "a" * 40, "identity_quality": "verified"}
        )

        self.assertNotEqual(list(self.validator.iter_errors(record)), [])

    def test_the_fingerprint_carries_no_comparison_or_policy(self) -> None:
        """It says what the code was, never whether that was acceptable.

        Checked as rejected properties rather than as a word list: the field is
        closed, so anything not declared is already an error, and this states
        which additions were specifically meant to stay out.
        """
        for smuggled in (
            "matches_checkout",
            "current",
            "healthy",
            "reason_codes",
            "install_type",
            "module_path",
            "source_path",
            "started_at",
        ):
            with self.subTest(smuggled):
                record = self._with_fingerprint(
                    {
                        "component": "mq-agent",
                        "version": "1.28.0",
                        "commit": "a" * 40,
                        "identity_quality": "verified",
                        smuggled: True,
                    }
                )
                self.assertNotEqual(list(self.validator.iter_errors(record)), [])

    def test_the_fingerprint_is_not_required(self) -> None:
        """Optional in the contract. Whether a given producer must write it is
        that producer's decision, not this schema's."""
        self.assertNotIn("runtime_fingerprint", self.schema["required"])

    def test_unknown_fields_are_rejected(self) -> None:
        mutated = dict(self.example, routing_score=0.91)
        self.assertTrue(list(self.validator.iter_errors(mutated)))


if __name__ == "__main__":
    unittest.main()
