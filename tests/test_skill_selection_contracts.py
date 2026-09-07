"""Owner contract validation; selection execution remains in mq-agent."""

import copy
import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, ValidationError

ROOT = Path(__file__).resolve().parents[1]


class SkillSelectionContracts(unittest.TestCase):
    def validator(self, name):
        schema = json.loads((ROOT / "schemas" / f"{name}.json").read_text())
        Draft202012Validator.check_schema(schema)
        return Draft202012Validator(schema)

    def test_vocabulary_valid_and_strict(self):
        data = json.loads((ROOT / ".mq/skill-selection-vocabulary.json").read_text())
        validator = self.validator("skill-selection-vocabulary.v1")
        validator.validate(data)
        for field, value in [
            ("max_selected_skills", 0),
            ("max_optional_skills", -1),
            ("intents", []),
            ("extra", True),
        ]:
            with self.subTest(field=field), self.assertRaises(ValidationError):
                validator.validate({**data, field: value})

    def test_profile_all_fields_required(self):
        data = dict(
            schema="mq.skill-profile.v1",
            skill="safe",
            status="active",
            supported_targets=["codex", "claude"],
            scope=["repo"],
            intents=[],
            domains=["security"],
            risks=["secret_exposure"],
            required_for=["secret_exposure"],
            supersedes=[],
            description="Check secrets.",
        )
        validator = self.validator("mq.skill-profile.v1")
        validator.validate(data)
        for field in data:
            candidate = copy.deepcopy(data)
            del candidate[field]
            with self.subTest(field=field), self.assertRaises(ValidationError):
                validator.validate(candidate)
        with self.assertRaises(ValidationError):
            validator.validate({**data, "supported_targets": ["both"]})

    def test_route_reason_codes_and_shape(self):
        data = dict(
            schema="mq.skill-route.v1",
            task="secret",
            repo="mq-agent",
            target="both",
            profile=dict(intents=[], domains=["security"], risks=["secret_exposure"]),
            selected=[],
            missing_required=[dict(skill="safe", targets=["claude"])],
            selection_state="partial",
            reasons=[
                dict(
                    code="SKS005_REQUIRED_SKILL_UNAVAILABLE",
                    skill="safe",
                    target="claude",
                    message="Unavailable",
                )
            ],
            candidate_count=1,
        )
        validator = self.validator("mq.skill-route.v1")
        validator.validate(data)
        with self.assertRaises(ValidationError):
            validator.validate({**data, "selected_skills": []})
        with self.assertRaises(ValidationError):
            validator.validate({**data, "selection_state": "healthy"})
        data["reasons"][0]["code"] = "invented"
        with self.assertRaises(ValidationError):
            validator.validate(data)

    def test_published_examples_match_declared_strict_contracts(self):
        declared = json.loads((ROOT / ".mq/repo-contract.json").read_text())["contracts"]
        examples = {
            "skill-selection-vocabulary.v1": ".mq/skill-selection-vocabulary.json",
            "mq.skill-profile.v1": "examples/skill-profile.example.json",
            "mq.skill-route.v1": "examples/skill-route.example.json",
        }
        for name, relative in examples.items():
            with self.subTest(contract=name):
                self.assertIn(name.replace("-", "_"), declared)
                schema = json.loads((ROOT / "schemas" / f"{name}.json").read_text())
                self.assertIs(schema["additionalProperties"], False)
                self.assertEqual(schema["properties"]["schema"]["const"], name)
                example = json.loads((ROOT / relative).read_text())
                self.assertEqual(example["schema"], name)
                self.validator(name).validate(example)
