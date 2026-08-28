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

    def test_unknown_fields_are_rejected(self) -> None:
        mutated = dict(self.example, routing_score=0.91)
        self.assertTrue(list(self.validator.iter_errors(mutated)))


if __name__ == "__main__":
    unittest.main()
