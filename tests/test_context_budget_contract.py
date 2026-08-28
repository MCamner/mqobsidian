"""`.mq/context-budgets.json` is a declared contract and must behave like one.

It has declared `"schema": "context-budget.v1"` since it was written, but that
schema did not exist, nothing validated the artifact, and the contract was not
among the repo's declared contracts. The vocabulary contract added in DEC-005 is
held to a higher standard than the older one it was modelled on; this raises the
older one rather than treating the gap as licence to lower the new.

The invariant that matters is not structural. Every consumer indexes the budget
map by name -- `CONTEXT_BUDGETS[name]` in `check-token-budget.py` and
`generate-repo-context-export.py` -- so a name without a budget is a KeyError at
run time rather than a readable failure.
"""
from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / ".mq" / "context-budgets.json"
SCHEMA = ROOT / "schemas" / "context-budget.v1.json"

sys.path.insert(0, str(ROOT / "scripts"))
SPEC = importlib.util.spec_from_file_location(
    "context_budgets", ROOT / "scripts" / "context_budgets.py"
)
assert SPEC and SPEC.loader
BUDGETS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BUDGETS)


class ContextBudgetContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
        self.schema = json.loads(SCHEMA.read_text(encoding="utf-8"))

    def test_artifact_validates_against_its_schema(self) -> None:
        Draft202012Validator(self.schema).validate(self.contract)

    def test_declared_schema_id_matches_the_schema_file(self) -> None:
        # The drift the artifact could not previously express: it named a schema
        # nobody had to provide.
        self.assertEqual(
            self.contract["schema"],
            self.schema["properties"]["schema"]["const"],
        )
        self.assertEqual(self.schema["title"], self.contract["schema"])

    def test_every_rendered_row_has_a_budget(self) -> None:
        missing = [
            name
            for name in self.contract["rendered_order"]
            if name not in self.contract["budgets"]
        ]
        self.assertEqual(
            missing, [], f"rendered_order names {missing} with no budget: KeyError at render"
        )

    def test_every_consumed_file_has_a_budget(self) -> None:
        consumed = set(BUDGETS.LOCAL_CONTEXT_FILES) | set(BUDGETS.EXPORTED_CONTEXT_FILES)
        missing = sorted(consumed - set(self.contract["budgets"]))
        self.assertEqual(
            missing,
            [],
            f"{missing} are indexed as CONTEXT_BUDGETS[name] but carry no budget",
        )

    def test_contract_is_declared_by_the_repo(self) -> None:
        declared = json.loads((ROOT / ".mq" / "repo-contract.json").read_text())["contracts"]
        self.assertIn("context_budget.v1", declared)


if __name__ == "__main__":
    unittest.main()
