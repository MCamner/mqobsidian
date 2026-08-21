from __future__ import annotations

import importlib.util
import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "eval-retrieval.py"
SPEC = importlib.util.spec_from_file_location("eval_retrieval", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
evaluator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(evaluator)


def signal(*judgments: tuple[str, str], outcome: str = "sufficient", repo: str = "mq-mcp") -> dict:
    return {
        "schema": "feedback-signal.v1",
        "task": "score selection quality",
        "generated_at": "2026-08-19T00:00:00Z",
        "repo": repo,
        "outcome": outcome,
        "judgments": [{"block": block, "judgment": judgment} for block, judgment in judgments],
    }


def write(directory: Path, name: str, records: list[dict]) -> Path:
    path = directory / name
    if name.endswith(".jsonl"):
        path.write_text(
            "\n".join(json.dumps(record) for record in records) + "\n", encoding="utf-8"
        )
    else:
        path.write_text(json.dumps(records[0]), encoding="utf-8")
    return path


class SummaryTest(unittest.TestCase):
    def test_confusion_matrix_maps_judgments_to_precision_and_recall(self) -> None:
        signals = [signal(("a", "useful"), ("b", "useful"), ("c", "noise"), ("d", "missing"))]
        summary = evaluator.summarize(signals, min_signals=1)
        # precision = useful / (useful + noise) = 2/3; recall = useful / (useful + missing) = 2/3
        self.assertAlmostEqual(summary["precision"], 2 / 3)
        self.assertAlmostEqual(summary["recall"], 2 / 3)
        self.assertAlmostEqual(summary["f1"], 2 / 3)

    def test_stale_is_excluded_from_relevance_and_reported_on_its_own_axis(self) -> None:
        signals = [signal(("a", "useful"), ("b", "stale"))]
        summary = evaluator.summarize(signals, min_signals=1)
        self.assertEqual(summary["precision"], 1.0)
        self.assertEqual(summary["recall"], 1.0)
        self.assertEqual(summary["selected_blocks"], 2)
        self.assertAlmostEqual(summary["stale_rate"], 0.5)

    def test_absent_evidence_yields_none_not_zero(self) -> None:
        summary = evaluator.summarize([signal(("a", "missing"))], min_signals=1)
        self.assertIsNone(summary["precision"])
        self.assertEqual(summary["recall"], 0.0)
        self.assertIsNone(summary["f1"])
        self.assertEqual(evaluator.format_ratio(summary["precision"]), "n/a")

    def test_sufficiency_rate_counts_pack_outcomes(self) -> None:
        signals = [
            signal(("a", "useful"), outcome="sufficient"),
            signal(("a", "missing"), outcome="insufficient"),
        ]
        summary = evaluator.summarize(signals, min_signals=1)
        self.assertEqual(summary["sufficiency_rate"], 0.5)

    def test_thin_corpus_is_flagged_rather_than_scored_confidently(self) -> None:
        summary = evaluator.summarize([signal(("a", "useful"))], min_signals=5)
        self.assertTrue(summary["insufficient_corpus"])


class BlockVerdictTest(unittest.TestCase):
    def verdict(self, *judgments: str, minimum: int = 3) -> str:
        signals = [signal(*(("a", judgment) for judgment in judgments))]
        rows = evaluator.per_block(signals, minimum)
        return rows[0]["verdict"]

    def test_recurring_noise_is_a_downgrade_candidate(self) -> None:
        self.assertEqual(self.verdict("noise", "noise", "useful"), "downgrade")

    def test_recurring_missing_is_a_create_or_widen_candidate(self) -> None:
        self.assertEqual(self.verdict("missing", "missing", "useful"), "widen-or-create")

    def test_recurring_stale_is_a_freshness_flip(self) -> None:
        self.assertEqual(self.verdict("stale", "stale", "useful"), "refresh")

    def test_too_few_judgments_never_produce_a_verdict(self) -> None:
        self.assertEqual(self.verdict("noise", "noise"), "insufficient-data")

    def test_a_tie_is_reported_as_mixed_not_resolved_arbitrarily(self) -> None:
        self.assertEqual(self.verdict("useful", "noise", "missing"), "mixed")


class LoadTest(unittest.TestCase):
    def test_reads_json_and_jsonl_from_a_directory(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            directory = Path(raw)
            write(directory, "one.json", [signal(("a", "useful"))])
            write(directory, "many.jsonl", [signal(("b", "noise")), signal(("c", "missing"))])
            signals = evaluator.load_signals([directory], evaluator.load_validator())
        self.assertEqual(len(signals), 3)

    def test_invalid_record_fails_the_run_instead_of_being_skipped(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            directory = Path(raw)
            broken = signal(("a", "useful"))
            broken["judgments"][0]["judgment"] = "helpful"
            write(directory, "bad.json", [broken])
            with self.assertRaises(ValueError) as caught:
                evaluator.load_signals([directory], evaluator.load_validator())
        self.assertIn("not a valid feedback-signal.v1", str(caught.exception))

    def test_repo_filter_scopes_the_corpus(self) -> None:
        signals = [signal(("a", "useful"), repo="mq-mcp"), signal(("b", "noise"), repo="mq-agent")]
        self.assertEqual(len(evaluator.select_repo(signals, "mq-agent")), 1)
        self.assertEqual(len(evaluator.select_repo(signals, None)), 2)


class CliTest(unittest.TestCase):
    def run_cli(self, argv: list[str]) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = evaluator.main(argv)
        return code, out.getvalue(), err.getvalue()

    def test_text_output_reports_metrics_and_per_block_rows(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            directory = Path(raw)
            write(directory, "signals.jsonl", [signal(("a", "useful"), ("b", "noise"))])
            code, out, _ = self.run_cli([str(directory), "--min-signals", "1"])
        self.assertEqual(code, 0)
        self.assertIn("precision=0.500", out)
        self.assertIn("insufficient_corpus=false", out)
        self.assertIn("block\ta\t", out)

    def test_markdown_output_names_the_contract_it_scores(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            directory = Path(raw)
            write(directory, "signals.jsonl", [signal(("a", "useful"))])
            code, out, _ = self.run_cli([str(directory), "--format", "markdown"])
        self.assertEqual(code, 0)
        self.assertIn("feedback-signal.v1", out)
        self.assertIn("Corpus is below the acting threshold", out)

    def test_missing_surface_exits_two_without_a_traceback(self) -> None:
        code, _, err = self.run_cli(["/nonexistent/feedback/surface"])
        self.assertEqual(code, 2)
        self.assertIn("no feedback surface to score", err)

    def test_shipped_example_validates_against_the_schema(self) -> None:
        example = Path(__file__).resolve().parents[1] / "examples" / "feedback-signal.example.json"
        signals = evaluator.load_signals([example], evaluator.load_validator())
        summary = evaluator.summarize(signals, min_signals=1)
        self.assertEqual(summary["useful"], 1)
        self.assertEqual(summary["noise"], 1)
        self.assertEqual(summary["missing"], 1)


if __name__ == "__main__":
    unittest.main()
