#!/usr/bin/env python3
"""Run the unit suite against a clean checkout of HEAD, not the working tree.

Most of this repo is gitignored -- `memory/`, `systems/`, `skills-src/`, the
built skill trees, the root agent entrypoints. A test that reads those passes in
a working tree that has them and fails in CI, which checks out only tracked
files.

That is not hypothetical. `check-skills-built.py` turned main red on the push
that added it: in CI `skills-src/` exists, because two source skills are
force-added, while all three built trees are absent, and the check read a fresh
checkout as a stale build. The suite was green locally the whole time.

So this reproduces what CI sees -- `git archive HEAD` into a temporary
directory -- and runs the suite there. It is the parity check between "green on
my machine" and "green on a checkout", and it belongs in the gate rather than in
the recovery after an incident.

Read-only with respect to the repo: it writes only inside a temporary directory.

Requires a git repo with at least one commit. Uncommitted work is invisible to
it by design; that is the point, and it means a failure here can mean "the fix
is real but not committed yet".
"""

from __future__ import annotations

import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TEST_DIR = "tests"


def _run(args: list[str], cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True)


def run_suite_on_clean_checkout(root: Path = REPO_ROOT) -> tuple[int, str]:
    """Export HEAD to a temp dir and run the unit suite there.

    Returns the suite's return code and its combined output.
    """
    with tempfile.TemporaryDirectory() as tmp:
        target = Path(tmp) / "checkout"
        target.mkdir()
        archive = Path(tmp) / "head.tar"

        exported = _run(["git", "archive", "--output", str(archive), "HEAD"], root)
        if exported.returncode != 0:
            return exported.returncode, f"git archive failed: {exported.stderr.strip()}"

        with tarfile.open(archive) as tar:
            tar.extractall(target)  # noqa: S202 - our own archive of tracked files

        if not (target / TEST_DIR).is_dir():
            return 0, f"no {TEST_DIR}/ in the checkout; nothing to run"

        suite = _run(
            [sys.executable, "-m", "unittest", "discover", "-s", TEST_DIR, "-q"],
            target,
        )
        return suite.returncode, (suite.stdout + suite.stderr).strip()


def main() -> int:
    if not (REPO_ROOT / ".git").exists():
        print("clean-checkout check skipped: not a git repository")
        return 0

    code, output = run_suite_on_clean_checkout()
    if code != 0:
        print("the unit suite fails on a clean checkout of HEAD:", file=sys.stderr)
        for line in output.splitlines():
            print(f"  {line}", file=sys.stderr)
        print(
            "\nThe working tree holds gitignored files a clean checkout does not. "
            "A test that needs them must skip when they are absent. Reproduce with:\n"
            "  git archive HEAD | tar -x -C <scratch> && "
            "cd <scratch> && python3 -m unittest discover -s tests -q",
            file=sys.stderr,
        )
        return 1

    summary = next(
        (line for line in reversed(output.splitlines()) if line.startswith("Ran ")),
        "suite ran",
    )
    print(f"clean-checkout parity passed: {summary} against git archive HEAD")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
