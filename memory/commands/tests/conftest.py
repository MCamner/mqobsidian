"""Pytest config for the command-memory tests.

The tracked tests run on tmp paths only. Two blocks cover derive_tier
(decision 2026-06-27, Väg B):
  - test_derive_tier_characterization.py — what derive_tier does TODAY (tracked gaps)
  - test_two_track_separation.py — real invariants that pass TODAY. Local-only and
    not tracked: it audits this machine's real inbox, feedback, fixtures/ and local/
    trees, which a clean clone does not have. The mem* fixtures below exist for it.

No DD-001 engine is exercised: there is no effective_confidence, no
explicit_contradiction signal, no evaluation window, and no real/fixture
distinction inside the scorer. DD-001 stays deferred until real not_helped data
exists (ADR-008 DD-001 + memory/fixtures/downgrade/).
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# make emit_memory_score / emit_observation_score importable
COMMANDS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(COMMANDS))


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "dd001_gap: characterizes CURRENT derive_tier behaviour that diverges from the "
        "(undecided, deferred) DD-001 aspiration. Documents a gap; does NOT lock a target.",
    )


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


@pytest.fixture(scope="session")
def mem(repo_root) -> Path:
    return repo_root / "memory"


@pytest.fixture(scope="session")
def mem_local(mem) -> Path:
    return mem / "local"


@pytest.fixture(scope="session")
def mem_fixtures(mem) -> Path:
    return mem / "fixtures"
