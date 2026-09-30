#!/usr/bin/env python3
"""Assert the local release gate and the Public Safe Check gate agree.

`release-check.sh` says in its own header that it mirrors the Public Safe Check
workflow minus the export-staleness step. Nothing checked that claim, and it
had drifted: `check-context-links.py` and ruff ran in CI and not locally, so a
green local gate was silent about them rather than clean.

Every named step of an in-scope workflow must be declared here, mapped to the
local check it corresponds to, marked as setup, or marked `CiOnly` with a
written reason. A step added without a declaration fails this check, and so
does a local check no step claims, so the mirror cannot drift unnoticed. A new
workflow file fails until it is declared in or out of scope.

Read-only. Run standalone or from release-check.sh.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GATE = ROOT / "release-check.sh"
WORKFLOWS = ROOT / ".github" / "workflows"

SETUP = "__setup__"


class CiOnly(str):
    """A reason a step has no local counterpart, not a gate label."""


# Which workflows carry releasability assertions the local gate mirrors.
# A workflow mapped to a string is out of scope, and the string says why.
WORKFLOW_SCOPE: dict[str, object] = {
    "public-safe-check.yml": True,
    "markdownlint.yml": (
        "out of scope: markdown style is not a releasability assertion, and "
        "release-check.sh mirrors the Public Safe Check gate specifically."
    ),
    "pages.yml": "out of scope: publishes the site after a release, not a gate on one.",
    "release.yml": "out of scope: runs on a tag, after the gate rather than as one.",
}

# Every named step of an in-scope workflow.
STEPS: dict[str, object] = {
    "Checkout": SETUP,
    "Set up Python": SETUP,
    "Install validation dependencies": SETUP,
    "Validate export scaffolding": "validate-export.py",
    "Check for sensitive content": "check-sensitive-content.py",
    "Check token budget": "check-token-budget.py",
    "Check context front doors": "check-context-links.py",
    "Check published docs freshness": "check-docs-freshness.py",
    "Lint Python (ruff, pinned)": "ruff",
    "Local gate and CI check the same things": "check-gate-parity.py",
    "Run focused unit tests": "unittest",
    "Check agent-entrypoint canonical contract": "check-agent-entrypoints.py",
    "Check this repo's own context export is fresh": "check-context-export-fresh.py",
    "Check context exports are regenerated": CiOnly(
        "CI-only by design, and release-check.sh's header says so: the step runs "
        "generate-repo-context-export.py --all and diffs the result, so it "
        "rewrites examples/repo-context-exports. The local gate is read-only and "
        "must stay that way; making it writable to gain symmetry would trade a "
        "real property for a cosmetic one. CI enforces staleness on every push."
    ),
}

# Local checks with no CI counterpart, and why.
LOCAL_ONLY: dict[str, str] = {
    "check-clean-checkout.py": (
        "local-only because it is redundant in CI: the CI working tree already IS "
        "a clean checkout of tracked files, so running the suite against "
        "git archive HEAD there proves nothing new. Its value is catching the "
        "divergence locally, before the push -- a test that reads gitignored files "
        "is green in a working tree that has them and red in CI, which is exactly "
        "how check-skills-built.py turned main red on the push that added it."
    ),
    "check-skills-built.py": (
        "local-only: .gitignore keeps skills-src/ and all three built skill trees "
        "out of the repo apart from two force-added source skills, so CI has "
        "almost nothing to compare. The drift it catches -- editing a built copy, "
        "or adding a skill and not rebuilding -- happens where the source lives."
    ),
    "check-learn-namespace.py": (
        "local-only by necessity: it inspects memory/learn/, which .gitignore keeps "
        "out of the repo, so CI has no vault to check. The defect it guards against "
        "is local damage -- an export overwriting an authored note that was placed "
        "in the generator's namespace -- and it is caught where the vault exists."
    ),
}


def workflow_steps() -> dict[str, list[str]]:
    """Named steps of every in-scope workflow, keyed by step name.

    Parsed with a regex rather than a YAML library so the gate has no
    third-party import: this repo's runtime requirements do not include one,
    and a release gate that cannot run without an extra install is a gate
    people learn to skip.
    """
    found: dict[str, list[str]] = {}
    undeclared = sorted(
        p.name for p in WORKFLOWS.glob("*.yml") if p.name not in WORKFLOW_SCOPE
    )
    if undeclared:
        for name in undeclared:
            print(f"FAIL: {name} is not listed in WORKFLOW_SCOPE in {Path(__file__).name}")
        raise SystemExit(1)

    name_re = re.compile(r"^\s*-\s+name:\s*(.+?)\s*$")
    for name, in_scope in WORKFLOW_SCOPE.items():
        if in_scope is not True:
            continue
        path = WORKFLOWS / name
        if not path.exists():
            print(f"FAIL: WORKFLOW_SCOPE lists {name}, which does not exist")
            raise SystemExit(1)
        for line in path.read_text().splitlines():
            m = name_re.match(line)
            if m:
                found.setdefault(m.group(1).strip("\"'"), []).append(name)
    return found


def gate_labels() -> set[str]:
    """Labels of every check release-check.sh runs through run()."""
    pattern = re.compile(r'^\s*run\s+"([^"]+)"')
    return {
        m.group(1)
        for m in (pattern.match(line) for line in GATE.read_text().splitlines())
        if m
    }


def main() -> int:
    steps = workflow_steps()
    labels = gate_labels()
    failed = False

    for name in sorted(set(steps) - set(STEPS)):
        where = ", ".join(steps[name])
        print(f"FAIL: workflow step '{name}' ({where}) is not declared in STEPS")
        failed = True

    for name in sorted(set(STEPS) - set(steps)):
        print(f"FAIL: STEPS declares '{name}', which no in-scope workflow runs")
        failed = True

    mapped: set[str] = set()
    for name, target in sorted(STEPS.items()):
        if name not in steps or target == SETUP:
            continue
        if isinstance(target, CiOnly):
            print(f"SKIP: '{name}' is CI-only -- {target}")
            continue
        if target in labels:
            mapped.add(str(target))
            continue
        print(
            f"FAIL: workflow step '{name}' maps to release-check.sh label "
            f"'{target}', which it does not run"
        )
        failed = True

    for label in sorted(labels - mapped):
        if label in LOCAL_ONLY:
            print(f"SKIP: '{label}' is local-only -- {LOCAL_ONLY[label]}")
            continue
        print(
            f"FAIL: release-check.sh runs '{label}' and no in-scope workflow "
            "step declares it"
        )
        failed = True

    if failed:
        print("check-gate-parity: FAILED")
        return 1
    print(f"PASS: local gate and CI agree on {len(mapped)} checks")
    return 0


if __name__ == "__main__":
    sys.exit(main())
