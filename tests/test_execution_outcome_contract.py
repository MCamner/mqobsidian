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

    def test_repo_review_is_a_task_class(self) -> None:
        """mq-agent `review repo` produces outcomes under its own class. It is
        not mapped onto `audit`: correlation to feedback evidence goes through
        the exact run id, never through a borrowed vocabulary."""
        record = {**self.example, "task_class": "repo-review"}
        self.assertEqual(list(self.validator.iter_errors(record)), [])

    def test_every_historical_task_class_stays_valid(self) -> None:
        for task_class in (
            "audit", "ci", "docs", "release", "release-check", "signal",
            "task", "unclassified",
        ):
            record = {**self.example, "task_class": task_class}
            self.assertEqual(list(self.validator.iter_errors(record)), [], task_class)

    def test_an_undeclared_task_class_is_rejected(self) -> None:
        record = {**self.example, "task_class": "review"}
        self.assertNotEqual(list(self.validator.iter_errors(record)), [])

    def test_the_fingerprint_is_not_required(self) -> None:
        """Optional in the contract. Whether a given producer must write it is
        that producer's decision, not this schema's."""
        self.assertNotIn("runtime_fingerprint", self.schema["required"])

    def test_measured_fallback_is_optional_and_structured(self) -> None:
        record = {
            **self.example,
            "fallbacks": 1,
            "fallback": {
                "from": "mq-mcp-tool-policy",
                "to": "static-read-only-allowlist",
                "reason": "policy-unavailable-or-invalid",
                "stage": "workflow-policy",
                "source": "measured",
            },
        }

        self.assertEqual(list(self.validator.iter_errors(record)), [])

        without = {key: value for key, value in record.items() if key != "fallback"}
        self.assertEqual(list(self.validator.iter_errors(without)), [])

    def test_fallback_cannot_claim_unmeasured_or_smuggle_detail(self) -> None:
        base = {
            "from": "mq-mcp-tool-policy",
            "to": "static-read-only-allowlist",
            "reason": "policy-unavailable-or-invalid",
            "stage": "workflow-policy",
            "source": "measured",
        }
        for mutation in (
            {**base, "source": "inferred"},
            {**base, "prompt": "raw prompt"},
            {key: value for key, value in base.items() if key != "reason"},
        ):
            with self.subTest(mutation=mutation):
                record = {**self.example, "fallbacks": 1, "fallback": mutation}
                self.assertTrue(list(self.validator.iter_errors(record)))

    def test_unknown_fields_are_rejected(self) -> None:
        mutated = dict(self.example, routing_score=0.91)
        self.assertTrue(list(self.validator.iter_errors(mutated)))

    def _complete(self) -> dict:
        return {
            "status": "complete",
            "steps": [{"step": 1, "status": "complete"}],
        }

    def _partial(self) -> dict:
        return {
            "status": "partial",
            "steps": [{
                "step": 1, "status": "partial",
                "source_item_count": 91, "executed_call_count": 25,
            }],
        }

    def test_complete_execution_and_partial_failure_are_valid(self) -> None:
        records = (
            {**self.example, "completeness": self._complete()},
            {**self.example, "result": "FAIL", "exit_status": "error",
             "completeness": self._partial()},
        )
        for record in records:
            with self.subTest(record=record):
                self.assertEqual(list(self.validator.iter_errors(record)), [])

    def test_partial_execution_cannot_be_pass_or_ok(self) -> None:
        for result, exit_status in (("PASS", "ok"), ("PASS", "error"),
                                    ("FAIL", "ok"), ("SKIPPED", "skipped")):
            record = {**self.example, "result": result, "exit_status": exit_status,
                      "completeness": self._partial()}
            with self.subTest(result=result, exit_status=exit_status):
                self.assertTrue(list(self.validator.iter_errors(record)))

    def test_completeness_status_matches_its_step_states(self) -> None:
        for completeness in (
            {"status": "complete", "steps": self._partial()["steps"]},
            {"status": "partial", "steps": self._complete()["steps"]},
            {"status": "complete", "steps": []},
        ):
            record = {**self.example, "result": "FAIL", "exit_status": "error",
                      "completeness": completeness}
            self.assertTrue(list(self.validator.iter_errors(record)))

    def test_empty_plan_is_explicitly_partial(self) -> None:
        record = {**self.example, "result": "FAIL", "exit_status": "error",
                  "completeness": {"status": "partial", "steps": []}}
        self.assertEqual(list(self.validator.iter_errors(record)), [])

    def test_incomplete_step_states_are_explicit(self) -> None:
        for status in ("partial", "failed", "skipped", "not-executed", "unmeasured"):
            record = {**self.example, "result": "FAIL", "exit_status": "error",
                      "completeness": {"status": "partial", "steps": [
                          {"step": 1, "status": status},
                      ]}}
            self.assertEqual(list(self.validator.iter_errors(record)), [], status)

    def test_completeness_rejects_missing_or_invalid_measurements(self) -> None:
        for step in (
            {"step": 1},
            {"status": "partial"},
            {"step": 0, "status": "partial"},
            {"step": 1, "status": "guessed"},
            {"step": 1, "status": "partial", "source_item_count": 91},
            {"step": 1, "status": "partial", "executed_call_count": 25},
            {"step": 1, "status": "partial", "source_item_count": -1,
             "executed_call_count": 25},
            {"step": 1, "status": "partial", "source_item_count": 91,
             "executed_call_count": -1},
            {"step": 1, "status": "partial", "path": "private-path"},
        ):
            record = {**self.example, "result": "FAIL", "exit_status": "error",
                      "completeness": {"status": "partial", "steps": [step]}}
            with self.subTest(step=step):
                self.assertTrue(list(self.validator.iter_errors(record)))

    def test_old_closed_reader_rejects_new_field_but_accepts_history(self) -> None:
        import copy

        old = copy.deepcopy(self.schema)
        old["properties"].pop("completeness", None)
        old.pop("allOf", None)
        validator = Draft202012Validator(old)
        self.assertEqual(list(validator.iter_errors(self.example)), [])
        self.assertTrue(list(validator.iter_errors(
            {**self.example, "completeness": self._complete()}
        )))


if __name__ == "__main__":
    unittest.main()
