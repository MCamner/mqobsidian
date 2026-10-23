"""Transition state machine tests (v1.22 Task 4).

Acceptance: the five locked transitions apply, illegal state and unresolved
evidence are refused before anything changes, and a crash after ANY commit
step recovers to either complete old state or complete new state — never a
half-applied one. The event log is append-only.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import transition_journal as tj


def _score(memory_id: str, status: str) -> dict:
    return {
        "schema": "memory-score.v1",
        "memory_id": memory_id,
        "timestamp": "2026-07-16T00:00:00Z",
        "status": status,
        "score": 0.8,
        "factors": {"frequency": 1.0, "source_count": 2.0, "confidence": 0.9,
                    "recency": 1.0, "usage_score": 0.0, "manual_boost": 0.0},
        "observed_by": ["repo-signal"],
        "first_seen": "2026-07-01",
        "last_seen": "2026-07-15",
    }


def _manifest(*refs: str) -> dict:
    return {
        "schema": "memory-evidence-manifest.v1",
        "source": "mqobsidian-export",
        "generated_at": "2026-07-16T00:00:00Z",
        "evidence": {
            ref: {"ref": ref, "producer": "claude", "schema_id": "memory-observation.v1",
                  "candidate_id": "m-1", "kind": "observation",
                  "observed_at": "2026-07-15T12:00:00Z", "summary": "seen twice"}
            for ref in refs
        },
    }


class Fixture:
    def __init__(self, root: Path, status: str = "candidate", memory_id: str = "m-1"):
        self.root = root
        self.memory_id = memory_id
        self.scores = root / "scores"
        self.scores.mkdir(parents=True, exist_ok=True)
        self.score_path = self.scores / f"{memory_id}.json"
        self.score_path.write_text(json.dumps(_score(memory_id, status)), encoding="utf-8")
        self.journal_dir = root / "journal"
        self.events = root / "promotions" / "events.jsonl"
        self.learn_path = root / "learn" / "agent" / f"{memory_id}.md"

    def plan(self, verb: str, refs: tuple[str, ...] = ("observation:o1",), reason: str = "two sources agree"):
        return tj.plan_transition(
            verb, self.memory_id,
            scores_dir=self.scores,
            evidence_manifest=_manifest(*refs),
            evidence_refs=list(refs),
            reason=reason,
        )

    def status(self) -> str:
        return json.loads(self.score_path.read_text(encoding="utf-8"))["status"]

    def events_list(self) -> list[dict]:
        return tj._read_jsonl(self.events)


class TransitionTableTests(unittest.TestCase):
    def test_locked_table_is_exactly_the_five_verbs(self) -> None:
        self.assertEqual(
            tj.TRANSITIONS,
            {
                "promote": ("candidate", "promoted"),
                "reject": ("candidate", "archived"),
                "defer": ("candidate", "observed"),
                "rollback": ("promoted", "candidate"),
                "deprecate": ("promoted", "deprecated"),
            },
        )

    def test_each_verb_applies_its_transition(self) -> None:
        cases = [
            ("promote", "candidate", "promoted"),
            ("reject", "candidate", "archived"),
            ("defer", "candidate", "observed"),
            ("rollback", "promoted", "candidate"),
            ("deprecate", "promoted", "deprecated"),
        ]
        for verb, start, end in cases:
            with self.subTest(verb=verb), TemporaryDirectory() as d:
                f = Fixture(Path(d), status=start)
                plan = f.plan(verb)
                tj.apply_transition(
                    plan,
                    journal_dir=f.journal_dir,
                    events_path=f.events,
                    learn_path=f.learn_path if verb in ("promote", "rollback") else None,
                    learn_content="# learn\n" if verb == "promote" else None,
                )
                self.assertEqual(f.status(), end)
                self.assertEqual(f.events_list()[-1]["to"], end)
                self.assertEqual(f.events_list()[-1]["verb"], verb)

    def test_illegal_state_is_refused_before_anything_changes(self) -> None:
        with TemporaryDirectory() as d:
            f = Fixture(Path(d), status="promoted")
            with self.assertRaises(tj.TransitionError) as ctx:
                f.plan("promote")  # promote requires candidate
            self.assertIn("illegal transition", str(ctx.exception))
            self.assertEqual(f.status(), "promoted")
            self.assertEqual(f.events_list(), [])

    def test_unknown_verb_is_refused(self) -> None:
        with TemporaryDirectory() as d:
            f = Fixture(Path(d))
            with self.assertRaises(tj.TransitionError):
                f.plan("obliterate")

    def test_missing_score_record_is_refused(self) -> None:
        with TemporaryDirectory() as d:
            f = Fixture(Path(d))
            with self.assertRaises(tj.TransitionError) as ctx:
                tj.plan_transition("promote", "nope", scores_dir=f.scores,
                                   evidence_manifest=_manifest("observation:o1"),
                                   evidence_refs=["observation:o1"], reason="r")
            self.assertIn("no score record", str(ctx.exception))


class EvidenceTests(unittest.TestCase):
    def test_unresolved_ref_blocks_the_transition(self) -> None:
        with TemporaryDirectory() as d:
            f = Fixture(Path(d))
            with self.assertRaises(tj.TransitionError) as ctx:
                tj.plan_transition("promote", "m-1", scores_dir=f.scores,
                                   evidence_manifest=_manifest("observation:o1"),
                                   evidence_refs=["observation:o1", "observation:ghost"],
                                   reason="r")
            self.assertIn("unresolved evidence refs: observation:ghost", str(ctx.exception))

    def test_promote_requires_evidence(self) -> None:
        with TemporaryDirectory() as d:
            f = Fixture(Path(d))
            with self.assertRaises(tj.TransitionError) as ctx:
                tj.plan_transition("promote", "m-1", scores_dir=f.scores,
                                   evidence_manifest=_manifest(), evidence_refs=[], reason="r")
            self.assertIn("traceable source evidence", str(ctx.exception))

    def test_refs_are_copied_into_the_event(self) -> None:
        with TemporaryDirectory() as d:
            f = Fixture(Path(d))
            plan = f.plan("promote", refs=("observation:o1",))
            tj.apply_transition(plan, journal_dir=f.journal_dir, events_path=f.events,
                                learn_path=f.learn_path, learn_content="# learn\n")
            self.assertEqual(f.events_list()[-1]["source_evidence_refs"], ["observation:o1"])

    def test_a_reason_is_required(self) -> None:
        with TemporaryDirectory() as d:
            f = Fixture(Path(d))
            with self.assertRaises(tj.TransitionError):
                f.plan("defer", reason="   ")


class DurableEffectTests(unittest.TestCase):
    def test_promote_writes_the_learn_projection(self) -> None:
        with TemporaryDirectory() as d:
            f = Fixture(Path(d))
            tj.apply_transition(f.plan("promote"), journal_dir=f.journal_dir,
                                events_path=f.events, learn_path=f.learn_path,
                                learn_content="# learn\n")
            self.assertTrue(f.learn_path.exists())

    def test_reject_and_defer_write_no_learn_record(self) -> None:
        for verb in ("reject", "defer"):
            with self.subTest(verb=verb), TemporaryDirectory() as d:
                f = Fixture(Path(d))
                tj.apply_transition(f.plan(verb), journal_dir=f.journal_dir,
                                    events_path=f.events)
                self.assertFalse(f.learn_path.exists())

    def test_rollback_removes_only_the_projection(self) -> None:
        with TemporaryDirectory() as d:
            f = Fixture(Path(d), status="promoted")
            f.learn_path.parent.mkdir(parents=True, exist_ok=True)
            f.learn_path.write_text("# generated\n", encoding="utf-8")
            tj.apply_transition(f.plan("rollback"), journal_dir=f.journal_dir,
                                events_path=f.events, learn_path=f.learn_path)
            self.assertFalse(f.learn_path.exists())
            self.assertTrue(f.score_path.exists(), "rollback must not delete the score record")
            self.assertEqual(f.status(), "candidate")

    def test_deprecate_retains_the_record(self) -> None:
        with TemporaryDirectory() as d:
            f = Fixture(Path(d), status="promoted")
            f.learn_path.parent.mkdir(parents=True, exist_ok=True)
            f.learn_path.write_text("# generated\n", encoding="utf-8")
            tj.apply_transition(f.plan("deprecate"), journal_dir=f.journal_dir,
                                events_path=f.events, learn_path=f.learn_path)
            self.assertTrue(f.learn_path.exists(), "deprecate retains the record")
            self.assertEqual(f.status(), "deprecated")


class JournalTests(unittest.TestCase):
    def test_journal_records_prior_hashes_and_staged_paths(self) -> None:
        with TemporaryDirectory() as d:
            f = Fixture(Path(d))
            plan = f.plan("promote")
            journal = tj.begin_journal(plan, journal_dir=f.journal_dir,
                                       staged_paths=[f.score_path, f.learn_path])
            snaps = {Path(s["path"]).name: s for s in journal["snapshots"]}
            self.assertTrue(snaps[f.score_path.name]["existed"])
            self.assertEqual(len(snaps[f.score_path.name]["sha256"]), 64)
            self.assertFalse(snaps[f.learn_path.name]["existed"])
            self.assertIsNone(snaps[f.learn_path.name]["sha256"])
            self.assertEqual(journal["state"], "pending")
            self.assertEqual(journal["steps"], list(tj.COMMIT_STEPS))

    def test_completed_transition_leaves_no_journal_or_snapshots(self) -> None:
        with TemporaryDirectory() as d:
            f = Fixture(Path(d))
            tj.apply_transition(f.plan("promote"), journal_dir=f.journal_dir,
                                events_path=f.events, learn_path=f.learn_path,
                                learn_content="# learn\n")
            self.assertEqual(list(f.journal_dir.glob("*.json")), [])
            self.assertEqual(list(f.journal_dir.glob("*.snapshots")), [])


class FaultInjectionTests(unittest.TestCase):
    """A crash after any commit step must recover to complete old or new state."""

    def _crash_after(self, step: str, verb: str = "promote"):
        """Run a transition that dies immediately after `step`."""
        d = TemporaryDirectory()
        f = Fixture(Path(d.name))
        plan = f.plan(verb)
        staged = [f.score_path, f.learn_path]
        journal = tj.begin_journal(plan, journal_dir=f.journal_dir, staged_paths=staged)
        jid = journal["journal_id"]

        if step in ("score", "learn", "event"):
            tj.commit_score(plan)
        if step in ("learn", "event"):
            tj.commit_learn(plan, learn_path=f.learn_path, learn_content="# learn\n")
        if step == "event":
            tj.commit_event(plan, events_path=f.events, journal_id=jid)
        # journal deliberately not completed: this is the crash
        return d, f, jid

    def test_crash_after_score_rolls_back_to_old_state(self) -> None:
        d, f, jid = self._crash_after("score")
        with d:
            self.assertEqual(f.status(), "promoted", "state changed before the crash")
            results = tj.recover(f.journal_dir, events_path=f.events)
            self.assertEqual(results[0]["outcome"], "rolled-back")
            self.assertEqual(f.status(), "candidate", "must restore complete old state")
            self.assertFalse(f.learn_path.exists())
            self.assertEqual(f.events_list(), [])

    def test_crash_after_learn_rolls_back_both_score_and_projection(self) -> None:
        d, f, jid = self._crash_after("learn")
        with d:
            self.assertTrue(f.learn_path.exists())
            results = tj.recover(f.journal_dir, events_path=f.events)
            self.assertEqual(results[0]["outcome"], "rolled-back")
            self.assertEqual(f.status(), "candidate")
            self.assertFalse(f.learn_path.exists(), "created projection must be removed")

    def test_crash_after_event_finishes_forward(self) -> None:
        d, f, jid = self._crash_after("event")
        with d:
            results = tj.recover(f.journal_dir, events_path=f.events)
            self.assertEqual(results[0]["outcome"], "finished-forward")
            self.assertEqual(f.status(), "promoted", "must keep complete new state")
            self.assertTrue(f.learn_path.exists())
            self.assertEqual(len(f.events_list()), 1)

    def test_recovery_is_idempotent(self) -> None:
        d, f, jid = self._crash_after("score")
        with d:
            tj.recover(f.journal_dir, events_path=f.events)
            again = tj.recover(f.journal_dir, events_path=f.events)
            self.assertEqual(again, [], "no journals left to resolve")
            self.assertEqual(f.status(), "candidate")

    def test_rollback_of_a_modified_projection_restores_prior_bytes(self) -> None:
        """rollback replaces an existing projection; a crash must restore it."""
        with TemporaryDirectory() as d:
            f = Fixture(Path(d), status="promoted")
            f.learn_path.parent.mkdir(parents=True, exist_ok=True)
            f.learn_path.write_text("# original\n", encoding="utf-8")
            plan = f.plan("rollback")
            tj.begin_journal(plan, journal_dir=f.journal_dir,
                             staged_paths=[f.score_path, f.learn_path])
            tj.commit_score(plan)
            tj.commit_learn(plan, learn_path=f.learn_path, learn_content=None)
            self.assertFalse(f.learn_path.exists(), "rollback removed it")

            tj.recover(f.journal_dir, events_path=f.events)
            self.assertEqual(f.learn_path.read_text(encoding="utf-8"), "# original\n")
            self.assertEqual(f.status(), "promoted")

    def test_corrupt_snapshot_fails_loudly_and_keeps_the_journal(self) -> None:
        d, f, jid = self._crash_after("score")
        with d:
            backup_dir = f.journal_dir / f"{jid}.snapshots"
            for item in backup_dir.iterdir():
                item.write_bytes(b"corrupted")
            results = tj.recover(f.journal_dir, events_path=f.events)
            self.assertEqual(results[0]["outcome"], "unrecoverable")
            self.assertIn("hash verification", results[0]["error"])
            self.assertTrue((f.journal_dir / f"{jid}.json").exists(),
                            "journal is kept so a later pass can retry")


class CompensationTests(unittest.TestCase):
    def test_compensation_appends_an_inverse_event_and_never_truncates(self) -> None:
        with TemporaryDirectory() as d:
            f = Fixture(Path(d))
            result = tj.apply_transition(f.plan("promote"), journal_dir=f.journal_dir,
                                         events_path=f.events, learn_path=f.learn_path,
                                         learn_content="# learn\n")
            original = result["event"]
            inverse = tj.compensate(original, events_path=f.events,
                                    reason="forward recovery could not complete")

            events = f.events_list()
            self.assertEqual(len(events), 2, "log is append-only")
            self.assertEqual(events[0]["id"], original["id"], "history is never rewritten")
            self.assertEqual(inverse["compensates"], original["id"])
            self.assertEqual(inverse["from"], original["to"])
            self.assertEqual(inverse["to"], original["from"])


if __name__ == "__main__":
    unittest.main()
