"""Block 2 — characterization of CURRENT derive_tier behaviour.

These tests assert what `emit_memory_score.derive_tier` does TODAY. They are green
and act as a regression lock. Where today's behaviour diverges from the DD-001
*aspiration* in the test matrix, the test is marked `@pytest.mark.dd001_gap` and the
divergence is documented — but NO future target is locked here (DD-001 is deferred
until real not_helped data exists).

IMPORTANT — what cannot be expressed yet:
  `derive_tier(m)` is STATELESS snapshot scoring. It takes only counts
  (worked/reuse/failed/confidence/helped/not_helped/freshness). It has NO current
  status, NO history, NO evaluation window, NO effective_confidence, and NO
  explicit_contradiction signal. So matrix notions like "one step down",
  "repeated within window", and "starting status PROMOTED" have no representation.
  Rows that depend on them are skipped with a reason, not faked.
"""

from __future__ import annotations

import emit_memory_score as ems
import pytest


def M(worked, reuse, failed, confidence, helped, not_helped, freshness):
    return {
        "worked": worked, "reuse": reuse, "failed": failed, "confidence": confidence,
        "helped": helped, "not_helped": not_helped, "freshness": freshness,
    }


def tier(m):
    return ems.derive_tier(m)[0]


# --- baseline characterizations (current behaviour, matches intent) --------

def test_clean_strong_evidence_with_feedback_promotes():
    assert tier(M(4, 2, 0, 0.85, helped=1, not_helped=0, freshness="current")) == "promoted"


def test_thin_evidence_is_observed():
    assert tier(M(1, 1, 0, 0.60, helped=0, not_helped=0, freshness="current")) == "observed"


def test_t01_below_bar_plus_negative_deprecates():
    """T01: weak memory + 1 real negative → deprecated. Matches DD-001 intent."""
    assert tier(M(1, 1, 0, 0.50, helped=0, not_helped=1, freshness="current")) == "deprecated"


# --- characterizations that DIVERGE from the DD-001 aspiration -------------

@pytest.mark.dd001_gap
def test_t02_strong_single_negative_stays_candidate():
    """T02: strong + 1 negative. Today → candidate (the promoted gate fails on
    not_helped>0). Observably 'one step down, not deprecated', which happens to
    match the matrix guard — but there is NO effective-confidence model behind it;
    the coincidence is the gap to close in DD-001."""
    assert tier(M(5, 2, 0, 0.85, helped=1, not_helped=1, freshness="current")) == "candidate"


@pytest.mark.dd001_gap
def test_t03_strong_repeated_negative_today_stays_candidate():
    """T03: strong + 2 negatives. DD-001 aspiration: DEPRECATED allowed. Today:
    still `candidate` — repeated negatives have no effect once the evidence bar is
    met. Tracked gap (no repeated-negative deprecation, no window)."""
    assert tier(M(5, 2, 0, 0.85, helped=1, not_helped=2, freshness="current")) == "candidate"


@pytest.mark.dd001_gap
def test_t09_strong_stale_not_deprecated_by_freshness_alone():
    """T09: strong + freshness=deprecated, no negative. DD-001: must NOT die from
    freshness alone. Today → `candidate` (the freshness branch is unreachable once
    the evidence bar is met). Satisfies the guard, but because freshness is fully
    IGNORED, not because it is a weighted 'contributing signal'. Tracked gap."""
    assert tier(M(5, 2, 0, 0.90, helped=0, not_helped=0, freshness="deprecated")) == "candidate"


@pytest.mark.dd001_gap
def test_t12_strong_stale_plus_negative_today_stays_candidate():
    """T12: strong + freshness=deprecated + 1 negative. DD-001 aspiration:
    DEPRECATED. Today → `candidate` (neither freshness nor a single negative can
    deprecate an evidence-meeting memory). Tracked gap."""
    assert tier(M(5, 2, 0, 0.85, helped=0, not_helped=1, freshness="deprecated")) == "candidate"


# --- rows whose SUBSTRATE does not exist yet (skipped honestly) ------------

@pytest.mark.skip(reason="no explicit_contradiction signal — vocab is helped/not_helped/uncertain (DD-001 substrate missing)")
def test_t04_explicit_contradiction_deprecates():
    ...


@pytest.mark.skip(reason="derive_tier has no real/fixture distinction; the real guard is the local-only test_two_track_separation (T18/T25)")
def test_t18_fixture_negative_not_counted():
    ...
