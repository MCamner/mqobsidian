"""memory/.venv is also the repo's interpreter (VS Code, mypy, release-check),
but uv rebuilds it from memory/pyproject.toml alone — after a Homebrew Python
upgrade it came back without jsonschema/ruff. That file must therefore carry
every requirement in requirements*.txt. It is gitignored, so the check skips
where it does not exist (CI, clean checkouts)."""

from __future__ import annotations

import tomllib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MEMORY_PYPROJECT = ROOT / "memory" / "pyproject.toml"
REQUIREMENTS = (ROOT / "requirements.txt", ROOT / "requirements-dev.txt")


def _requirement_lines(path: Path) -> set[str]:
    lines = (
        line.split("#", 1)[0].strip() for line in path.read_text(encoding="utf-8").splitlines()
    )
    return {line.replace(" ", "") for line in lines if line}


@unittest.skipUnless(MEMORY_PYPROJECT.exists(), "memory/pyproject.toml is local-only")
class MemoryVenvDepsTests(unittest.TestCase):
    def test_dev_group_mirrors_repo_requirements(self) -> None:
        pyproject = tomllib.loads(MEMORY_PYPROJECT.read_text(encoding="utf-8"))
        dev = {dep.replace(" ", "") for dep in pyproject["dependency-groups"]["dev"]}
        required = set().union(*(_requirement_lines(path) for path in REQUIREMENTS))
        self.assertEqual(
            sorted(required - dev),
            [],
            "add these to memory/pyproject.toml [dependency-groups].dev, then `uv lock`",
        )


if __name__ == "__main__":
    unittest.main()
