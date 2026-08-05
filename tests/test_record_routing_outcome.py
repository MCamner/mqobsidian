from __future__ import annotations

import importlib.util
import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "record-routing-outcome.py"
SPEC = importlib.util.spec_from_file_location("record_routing_outcome", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
writer = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(writer)


SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "additionalProperties": False,
    "required": [
        "schema",
        "decision_id",
        "task_class",
        "selected_route",
        "local_model",
        "authoritative_agent",
        "attempted",
        "model_output_received",
        "schema_valid",
        "verification",
        "accepted_by_agent",
        "accepted_by_operator",
        "escalated",
        "escalation_reason",
        "recorded_at",
    ],
    "properties": {
        "schema": {"const": "mq.model-route-outcome.v1"},
        "decision_id": {"type": "string", "minLength": 1},
        "task_class": {"enum": ["docs-review"]},
        "selected_route": {"enum": ["local-shadow"]},
        "local_model": {"type": ["string", "null"]},
        "authoritative_agent": {"enum": ["codex", "claude"]},
        "attempted": {"type": "boolean"},
        "model_output_received": {"type": "boolean"},
        "schema_valid": {"type": "boolean"},
        "verification": {
            "type": "object",
            "additionalProperties": False,
            "required": ["status", "checks"],
            "properties": {
                "status": {"enum": ["PASS", "FAIL", "SKIPPED", "UNAVAILABLE"]},
                "checks": {
                    "type": "array",
                    "items": {"type": "string", "minLength": 1},
                },
            },
        },
        "accepted_by_agent": {"type": "boolean"},
        "accepted_by_operator": {"type": "boolean"},
        "escalated": {"type": "boolean"},
        "escalation_reason": {"type": ["string", "null"]},
        "recorded_at": {"type": "string", "format": "date-time"},
    },
}


def _outcome(**changes: object) -> dict[str, object]:
    result: dict[str, object] = {
        "schema": "mq.model-route-outcome.v1",
        "decision_id": "route-example-1",
        "task_class": "docs-review",
        "selected_route": "local-shadow",
        "local_model": "local-model",
        "authoritative_agent": "codex",
        "attempted": True,
        "model_output_received": True,
        "schema_valid": True,
        "verification": {
            "status": "PASS",
            "checks": ["candidate-schema", "task-class-match"],
        },
        "accepted_by_agent": False,
        "accepted_by_operator": False,
        "escalated": False,
        "escalation_reason": None,
        "recorded_at": "2026-08-04T12:00:00Z",
    }
    result.update(changes)
    return result


class RecordRoutingOutcomeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        self.schema = self.root / "model_route_outcome.schema.json"
        self.input = self.root / "outcome.json"
        self.output = self.root / "routing" / "outcomes.jsonl"
        self.schema.write_text(json.dumps(SCHEMA), encoding="utf-8")

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def run_writer(self, outcome: dict[str, object], *extra: str) -> tuple[int, str, str]:
        self.input.write_text(json.dumps(outcome), encoding="utf-8")
        stdout = io.StringIO()
        stderr = io.StringIO()
        argv = [
            str(self.input),
            "--schema",
            str(self.schema),
            "--output",
            str(self.output),
            *extra,
        ]
        with redirect_stdout(stdout), redirect_stderr(stderr):
            result = writer.main(argv)
        return result, stdout.getvalue(), stderr.getvalue()

    def test_appends_exact_verified_outcome(self) -> None:
        result, output, _ = self.run_writer(_outcome())

        self.assertEqual(result, 0)
        rows = [json.loads(line) for line in self.output.read_text().splitlines()]
        self.assertEqual(rows, [_outcome()])
        self.assertIn("recorded", output)

    def test_public_example_matches_the_storage_contract(self) -> None:
        example = Path(__file__).resolve().parents[1] / "examples" / "model-route-outcome.example.json"
        validator = writer.load_validator(self.schema)

        validated = writer.validate_outcome(json.loads(example.read_text()), validator)

        self.assertEqual(validated["schema"], "mq.model-route-outcome.v1")
        self.assertNotIn("candidate", validated)
        self.assertNotIn("raw_model_output", validated)

    def test_identical_retry_is_idempotent(self) -> None:
        self.assertEqual(self.run_writer(_outcome())[0], 0)
        result, output, _ = self.run_writer(_outcome())

        self.assertEqual(result, 0)
        self.assertEqual(len(self.output.read_text().splitlines()), 1)
        self.assertIn("already recorded", output)

    def test_dry_run_validates_without_writing(self) -> None:
        result, output, _ = self.run_writer(_outcome(), "--dry-run")

        self.assertEqual(result, 0)
        self.assertFalse(self.output.exists())
        self.assertEqual(json.loads(output), _outcome())

    def test_failed_verification_is_preserved_as_negative_evidence(self) -> None:
        outcome = _outcome(
            schema_valid=False,
            verification={"status": "FAIL", "checks": []},
            escalated=True,
            escalation_reason="schema-invalid",
        )
        result, _, _ = self.run_writer(outcome)

        self.assertEqual(result, 0)
        stored = json.loads(self.output.read_text())
        self.assertEqual(stored["verification"]["status"], "FAIL")
        self.assertTrue(stored["escalated"])

    def test_non_pass_outcome_cannot_be_accepted(self) -> None:
        outcome = _outcome(
            schema_valid=False,
            verification={"status": "FAIL", "checks": []},
            accepted_by_agent=True,
            escalated=True,
            escalation_reason="schema-invalid",
        )
        result, _, error = self.run_writer(outcome)

        self.assertEqual(result, 2)
        self.assertIn("must not be accepted", error)

    def test_inconsistent_pass_outcome_is_rejected(self) -> None:
        result, _, error = self.run_writer(_outcome(schema_valid=False))

        self.assertEqual(result, 2)
        self.assertIn("schema_valid=true", error)

    def test_unknown_raw_output_field_is_rejected(self) -> None:
        result, _, error = self.run_writer(_outcome(raw_model_output="unsafe raw text"))

        self.assertEqual(result, 2)
        self.assertFalse(self.output.exists())
        self.assertIn("Additional properties", error)

    def test_sensitive_material_is_rejected(self) -> None:
        result, _, error = self.run_writer(_outcome(local_model="sk-example01234567890123456789"))

        self.assertEqual(result, 2)
        self.assertFalse(self.output.exists())
        self.assertIn("sensitive", error)

    def test_corrupt_existing_history_blocks_append(self) -> None:
        self.output.parent.mkdir(parents=True)
        self.output.write_text("not-json\n", encoding="utf-8")
        result, _, error = self.run_writer(_outcome())

        self.assertEqual(result, 2)
        self.assertEqual(self.output.read_text(encoding="utf-8"), "not-json\n")
        self.assertIn("existing history", error)


if __name__ == "__main__":
    unittest.main()
