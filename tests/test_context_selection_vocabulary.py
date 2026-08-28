"""The selection vocabulary is a published contract, not a Python constant.

DEC-005 splits ownership: mqobsidian owns the words that decide whether a task
is source-heavy, mq-agent owns applying them. The failure this guards against is
the one that produced the split -- the same values living in two places with
nothing making them agree.
"""
from __future__ import annotations

import ast
import importlib.util
import json
import sys
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / ".mq" / "context-selection-vocabulary.json"
SCHEMA = ROOT / "schemas" / "context-selection-vocabulary.v1.json"
GENERATOR = ROOT / "scripts" / "generate-context-pack.py"

sys.path.insert(0, str(ROOT / "scripts"))
SPEC = importlib.util.spec_from_file_location("generate_context_pack", GENERATOR)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class VocabularyContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.contract = json.loads(CONTRACT.read_text(encoding="utf-8"))

    def test_contract_validates_against_its_schema(self) -> None:
        Draft202012Validator(json.loads(SCHEMA.read_text(encoding="utf-8"))).validate(
            self.contract
        )

    def test_generator_reads_the_contract_rather_than_a_literal(self) -> None:
        # The point of DEC-005: re-expressing the vocabulary as a Python literal
        # anywhere in the generator would relocate the duplicate instead of
        # removing it. Assert no module-level assignment restates the values.
        tree = ast.parse(GENERATOR.read_text(encoding="utf-8"))
        literals: list[str] = []
        for node in tree.body:
            if not isinstance(node, ast.Assign):
                continue
            target = node.targets[0]
            if not isinstance(target, ast.Name):
                continue
            try:
                value = ast.literal_eval(node.value)
            except ValueError:
                continue
            if isinstance(value, (list, tuple, set)) and any(
                item in self.contract["source_heavy_hints"]
                or item in self.contract["source_heavy_suppress"]
                for item in value
                if isinstance(item, str)
            ):
                literals.append(target.id)
        self.assertEqual(
            literals,
            [],
            f"{', '.join(literals)} restates contract values as a Python literal; "
            "read .mq/context-selection-vocabulary.json instead",
        )

    def test_loaded_values_match_the_contract(self) -> None:
        self.assertEqual(
            list(MODULE.CODEGRAPH_TASK_HINTS), self.contract["source_heavy_hints"]
        )
        self.assertEqual(
            list(MODULE.CODEGRAPH_TASK_SUPPRESS), self.contract["source_heavy_suppress"]
        )
        self.assertEqual(
            MODULE.MAX_CODEGRAPH_QUERIES, self.contract["max_codegraph_queries"]
        )

    def test_suppression_wins_over_a_hint(self) -> None:
        # Both words appear; the documentation suppressor must veto.
        self.assertFalse(MODULE.task_is_source_heavy("update the readme for the caller trace"))
        self.assertTrue(MODULE.task_is_source_heavy("trace callers of export_repo"))


if __name__ == "__main__":
    unittest.main()
