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

# The contract itself, not a copy of it. An inline fixture here used to be a
# third source of truth and had silently drifted from the real schema.
CANONICAL_SCHEMA = Path(__file__).resolve().parents[1] / "schemas" / "mq.model-route-outcome.v1.json"



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
        self.schema = CANONICAL_SCHEMA
        self.input = self.root / "outcome.json"
        self.output = self.root / "routing" / "outcomes.jsonl"

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

    def test_the_default_schema_is_the_canonical_contract_in_this_repo(self) -> None:
        # Resolution used to walk to a sibling mq-agent checkout via MQ_AGENT_DIR,
        # so validation depended on a machine-local path and whichever revision
        # that checkout was on. The contract lives here now.
        self.assertEqual(writer.default_schema_path(), CANONICAL_SCHEMA)
        self.assertTrue(CANONICAL_SCHEMA.is_file())

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


class ExecutionCorrelationContractTests(unittest.TestCase):
    """ADR-010 D3: correlation is a separate field, never a redefinition.

    `mq.model-route-outcome.v1` and `mq.execution-outcome.v1` both carry a
    field named `run_id` meaning different things — this observation's identity
    here, the operator run's identity there. The cheap "fix" for correlation is
    to write the execution's id into the existing `run_id`; that would silently
    destroy duplicate detection while appearing to add correlation. These tests
    make that impossible to do by accident.

    Semantics, not wording: the descriptions may be rewritten freely.
    """

    def setUp(self) -> None:
        self.schema = json.loads(CANONICAL_SCHEMA.read_text(encoding="utf-8"))

    def test_run_id_and_execution_run_id_are_two_distinct_properties(self) -> None:
        properties = self.schema["properties"]

        self.assertIn("run_id", properties)
        self.assertIn("execution_run_id", properties)
        self.assertIsNot(properties["run_id"], properties["execution_run_id"])

    def test_correlation_is_optional(self) -> None:
        # A routing observation can occur outside any execution — `route shadow`
        # from the CLI. Requiring correlation would make those records invalid.
        self.assertNotIn("execution_run_id", self.schema["required"])

    def test_run_id_did_not_become_required_or_change_shape(self) -> None:
        # Pre-existing state, recorded so a later change is deliberate: the
        # emitter writes run_id on every record, but the contract has never
        # required it. D3 does not change that.
        self.assertNotIn("run_id", self.schema["required"])
        self.assertEqual(self.schema["properties"]["run_id"]["type"], "string")

    def test_a_record_carrying_correlation_validates(self) -> None:
        validator = writer.load_validator(CANONICAL_SCHEMA)

        validated = writer.validate_outcome(
            _outcome(run_id="obs-1", execution_run_id="exec-1"), validator
        )

        self.assertEqual(validated["run_id"], "obs-1")
        self.assertEqual(validated["execution_run_id"], "exec-1")

    def test_a_historical_record_without_correlation_stays_valid(self) -> None:
        # The 130 observations recorded before this field existed are not
        # backfilled. Absence means correlation was not recorded, not that the
        # observation is invalid.
        validator = writer.load_validator(CANONICAL_SCHEMA)

        validated = writer.validate_outcome(_outcome(run_id="obs-1"), validator)

        self.assertNotIn("execution_run_id", validated)


class ApplicationModeContractTests(unittest.TestCase):
    """ADR-010 D7: applied versus shadow is its own field, and readiness counts
    only `applied`.

    `approved-local` is deliberately not reused. It already exists as a
    `selected_route` value that `model_routing.py:817` reads as an unauthorized
    write, so loading a second meaning onto it would repeat the mistake D3's
    invariant guards against, one field over.

    Semantics, not wording.
    """

    def setUp(self) -> None:
        self.schema = json.loads(CANONICAL_SCHEMA.read_text(encoding="utf-8"))

    def test_application_distinguishes_advisory_shadow_and_applied(self) -> None:
        self.assertEqual(
            self.schema["properties"]["application"]["enum"],
            ["advisory", "shadow", "applied"],
        )

    def test_application_is_optional_so_older_observations_stay_valid(self) -> None:
        # The 130 observations recorded before this field are not backfilled.
        # Absent means the mode was not recorded — and since readiness counts an
        # explicit `applied` only, absence contributes nothing on its own.
        self.assertNotIn("application", self.schema["required"])

    def test_applied_is_not_expressed_through_selected_route(self) -> None:
        # `application` and `selected_route` answer different questions: which
        # route, and whether it governed anything.
        self.assertNotIn("applied", self.schema["properties"]["selected_route"]["enum"])
        self.assertIn("approved-local", self.schema["properties"]["selected_route"]["enum"])

    def test_each_application_mode_validates(self) -> None:
        validator = writer.load_validator(CANONICAL_SCHEMA)

        for mode in ("advisory", "shadow", "applied"):
            with self.subTest(mode=mode):
                validated = writer.validate_outcome(
                    _outcome(application=mode, execution_run_id="exec-1"), validator
                )
                self.assertEqual(validated["application"], mode)

    def test_an_unknown_application_mode_is_rejected(self) -> None:
        validator = writer.load_validator(CANONICAL_SCHEMA)

        with self.assertRaises(ValueError):
            writer.validate_outcome(_outcome(application="maybe"), validator)


class ExecutionRouteDeprecationTests(unittest.TestCase):
    """ADR-010 D6: `route` on the execution contract is deprecated, not removed.

    Its only writer filled it with the swarm's `config.name` — the same string
    the record already carries as `task_class`, which is the identity confusion
    D5 forbids. Deprecating is the honest move; removing it in v1 would
    invalidate records already written.
    """

    EXECUTION_SCHEMA = Path(__file__).resolve().parents[1] / "schemas" / "mq.execution-outcome.v1.json"

    def setUp(self) -> None:
        self.schema = json.loads(self.EXECUTION_SCHEMA.read_text(encoding="utf-8"))

    def test_route_is_marked_deprecated(self) -> None:
        self.assertIs(self.schema["properties"]["route"].get("deprecated"), True)

    def test_route_is_still_accepted_so_existing_records_stay_valid(self) -> None:
        self.assertIn("route", self.schema["properties"])
        self.assertNotIn("route", self.schema["required"])


class RouteIdentityContractTests(unittest.TestCase):
    """ADR-010 D8: `selected_route` names the execution strategy, never the model.

    `route_readiness` counts distinct `selected_route` per routing task class, so
    what this field is allowed to mean decides what "two candidate routes"
    proves. A second local model would not register at all — `local_model` is a
    separate field and both observations still read `local-shadow` — and the
    tempting repair, writing `qwen-local` or `gpt-cloud` into the route, collapses
    route identity into model identity. These tests exist to make that collapse
    fail loudly rather than pass quietly.
    """

    def setUp(self) -> None:
        self.schema = json.loads(CANONICAL_SCHEMA.read_text(encoding="utf-8"))

    def test_a_deterministic_local_strategy_is_a_route(self) -> None:
        self.assertIn(
            "deterministic-local", self.schema["properties"]["selected_route"]["enum"]
        )

    def test_the_route_vocabulary_names_strategies_not_models(self) -> None:
        # Semantics, not wording: no route value may carry a model or vendor name.
        # Enumerating the forbidden shapes rather than the allowed ones is the
        # point — the failure mode is someone *adding* `qwen-local` later.
        routes = self.schema["properties"]["selected_route"]["enum"]
        for route in routes:
            with self.subTest(route=route):
                for model_word in ("qwen", "llama", "gpt", "claude", "mistral", "phi"):
                    self.assertNotIn(model_word, route.lower())

    def test_existing_route_values_are_untouched(self) -> None:
        # D8 adds a value. It reclassifies nothing, so every previously valid
        # observation stays valid without being rewritten.
        for route in ("local-shadow", "cloud-required", "approved-local"):
            with self.subTest(route=route):
                self.assertIn(route, self.schema["properties"]["selected_route"]["enum"])

    def test_a_strategy_that_runs_no_model_records_no_model(self) -> None:
        # `null`, never a placeholder string. A route with no model has no model
        # identity, and "deterministic" in `local_model` would put the strategy
        # name back into the field D8 just separated it from.
        validator = writer.load_validator(CANONICAL_SCHEMA)

        validated = writer.validate_outcome(
            _outcome(
                selected_route="deterministic-local",
                local_model=None,
                application="applied",
                execution_run_id="exec-1",
            ),
            validator,
        )

        self.assertEqual(validated["selected_route"], "deterministic-local")
        self.assertIsNone(validated["local_model"])

    def test_local_model_stays_required_so_its_absence_cannot_be_silent(self) -> None:
        # Nullable, not optional. A missing key would let a strategy leave the
        # question unanswered; `null` answers it.
        self.assertIn("local_model", self.schema["required"])
        self.assertEqual(self.schema["properties"]["local_model"]["type"], ["string", "null"])

    def test_an_unknown_route_is_rejected(self) -> None:
        validator = writer.load_validator(CANONICAL_SCHEMA)

        with self.assertRaises(ValueError):
            writer.validate_outcome(_outcome(selected_route="qwen-local"), validator)
