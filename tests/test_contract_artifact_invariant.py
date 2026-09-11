"""Every `.mq/*.json` that declares a schema must be backed and declared.

`.mq/context-budgets.json` carried `"schema": "context-budget.v1"` for months
while that schema did not exist and the contract was not declared. #84 repaired
that artifact; this repairs the class of error that let it exist unnoticed.

The existing docs freshness gate covers the last link only -- a *declared*
contract must be documented. It cannot see an artifact that names a schema
nobody wrote, because nothing was reading the artifacts.

    artifact -> schema exists -> contract declared -> documentation freshness
    [ this test ....................................]  [ existing gate ]

The chain was walked in one direction only, so a schema nobody reached from an
artifact stayed invisible: `schemas/mq.model-route-outcome.v1.json` shipped with
tests, `docs/ROUTING_OUTCOMES.md` and DEC-006, and was still absent from
`.mq/repo-contract.json` -- the register the rest of the stack reads to learn
what this repo owns. A green suite said nothing, because nothing read the
schema directory. The last test below closes that direction.

Deliberately narrow: no discovery, no contract engine, no new abstraction.
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MQ = ROOT / ".mq"
SCHEMAS = ROOT / "schemas"

# `.mq/repo-contract.json` itself declares the contracts; it is the register,
# not a registered artifact.
NOT_ARTIFACTS = {"repo-contract.json"}


def _declared_name(schema_id: str) -> str:
    """Schema files use hyphens, `repo-contract.json` declares underscores."""
    return schema_id.replace("-", "_")


def _artifacts() -> list[tuple[Path, str]]:
    found = []
    for path in sorted(MQ.glob("*.json")):
        if path.name in NOT_ARTIFACTS:
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict) and isinstance(data.get("schema"), str):
            found.append((path, data["schema"]))
    return found


class ContractArtifactInvariantTests(unittest.TestCase):
    def setUp(self) -> None:
        self.declared = set(
            json.loads((MQ / "repo-contract.json").read_text(encoding="utf-8"))["contracts"]
        )

    def test_there_is_something_to_check(self) -> None:
        # A silent gate is worse than no gate: if the glob ever stops matching,
        # every assertion below passes vacuously.
        self.assertTrue(_artifacts(), "no .mq artifact declares a schema; gate is vacuous")

    def test_every_declared_schema_has_a_schema_file(self) -> None:
        missing = [
            f"{path.relative_to(ROOT)} -> schemas/{schema_id}.json"
            for path, schema_id in _artifacts()
            if not (SCHEMAS / f"{schema_id}.json").is_file()
        ]
        self.assertEqual(
            missing, [], f"artifact names a schema that does not exist: {missing}"
        )

    def test_every_artifact_contract_is_declared(self) -> None:
        missing = [
            f"{path.relative_to(ROOT)} -> {_declared_name(schema_id)}"
            for path, schema_id in _artifacts()
            if _declared_name(schema_id) not in self.declared
        ]
        self.assertEqual(
            missing,
            [],
            f"artifact carries a contract absent from .mq/repo-contract.json: {missing}",
        )

    def test_every_declared_contract_has_a_schema_file(self) -> None:
        missing = sorted(
            name
            for name in self.declared
            if not (SCHEMAS / f"{name.replace('_', '-')}.json").is_file()
        )
        self.assertEqual(
            missing, [], f"declared contracts with no schema file: {missing}"
        )


    def test_every_schema_file_is_declared(self) -> None:
        """A schema in the tree that the register does not name owns nothing.

        Consumers read `.mq/repo-contract.json`, not a directory listing, so an
        undeclared schema is invisible to the stack however well it is tested
        and documented. Declaring one is intentional: it also obliges
        `scripts/check-docs-freshness.py` to find it in `docs/memory-model.md`.
        """
        undeclared = sorted(
            path.name
            for path in SCHEMAS.glob("*.json")
            if _declared_name(path.name[: -len(".json")]) not in self.declared
        )
        self.assertEqual(
            undeclared,
            [],
            f"schema files absent from .mq/repo-contract.json: {undeclared}",
        )

    def test_the_schema_gate_is_not_vacuous(self) -> None:
        self.assertTrue(
            list(SCHEMAS.glob("*.json")), "no schema files found; gate is vacuous"
        )


if __name__ == "__main__":
    unittest.main()
