#!/usr/bin/env python3
"""Measure whether context selection picked the *right* blocks, not just few ones.

`measure-context-effect.py` answers "how little context did we send?". It cannot
answer "did we send the correct context?" — a pack that is 96% smaller and wrong
scores identically to one that is 96% smaller and right.

This reads the Phase 11c feedback surface and turns the judgments mq-agent
already emits into selection-quality numbers. It introduces **no new contract**:
`feedback-signal.v1` is the gold label. Its vocabulary maps onto the standard
retrieval confusion matrix:

    useful  -> selected and earned its place   (true positive)
    noise   -> selected and wasted tokens      (false positive)
    missing -> needed but not selected         (false negative)

`stale` is deliberately excluded from precision and recall. Per
`docs/FEEDBACK_LOOP.md` it is a *freshness* signal, not a relevance one: the
block was selected correctly and its content had aged. Folding it into either
axis would blend two axes the repo keeps separate on purpose, so it is reported
as its own rate.

Rank metrics (Recall@K, MRR) are NOT computed. `feedback-signal.v1` records
judgments as an unordered set with no rank field, so any such number would be an
artifact of list order rather than a measurement.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "feedback-signal.v1.json"
DEFAULT_INPUT = Path(os.environ.get("MQ_OBSIDIAN_DIR", ROOT)) / "feedback"

# A verdict on a single block needs enough judgments to be more than an anecdote.
DEFAULT_MIN_BLOCK_SIGNALS = 3
# Below this many signals the corpus is reported as too thin to act on. The
# bottleneck for this repo is observation volume, not scoring (ROADMAP_NOTES).
DEFAULT_MIN_SIGNALS = 5

JUDGMENTS = ("useful", "noise", "missing", "stale")


def load_validator() -> Draft202012Validator:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema, format_checker=FormatChecker())


def iter_record_sources(paths: list[Path]) -> list[tuple[Path, int, str]]:
    """Return (path, line_number, raw_json) for every record in the inputs.

    A `.json` file holds one record; a `.jsonl` file holds one per line. A
    directory is expanded to both, sorted, so runs are reproducible.
    """
    sources: list[tuple[Path, int, str]] = []
    for path in paths:
        if path.is_dir():
            files = sorted(
                item
                for pattern in ("*.json", "*.jsonl")
                for item in path.glob(pattern)
            )
        else:
            files = [path]
        for file in files:
            if not file.is_file():
                raise ValueError(f"not a readable file: {file}")
            text = file.read_text(encoding="utf-8")
            if file.suffix == ".jsonl":
                for number, line in enumerate(text.splitlines(), 1):
                    if line.strip():
                        sources.append((file, number, line))
            else:
                sources.append((file, 0, text))
    return sources


def load_signals(paths: list[Path], validator: Draft202012Validator) -> list[dict[str, Any]]:
    """Parse and contract-validate every feedback signal in the inputs.

    Invalid records fail the run rather than being skipped: dropping them
    silently would bias the very metrics this script exists to report.
    """
    signals: list[dict[str, Any]] = []
    for file, number, raw in iter_record_sources(paths):
        where = f"{file}" if number == 0 else f"{file}:{number}"
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{where}: invalid JSON: {exc}") from exc
        errors = sorted(validator.iter_errors(data), key=lambda error: list(error.absolute_path))
        if errors:
            details = "; ".join(error.message for error in errors[:3])
            raise ValueError(f"{where}: not a valid feedback-signal.v1: {details}")
        signals.append(data)
    return signals


def select_repo(signals: list[dict[str, Any]], repo: str | None) -> list[dict[str, Any]]:
    if repo is None:
        return signals
    return [signal for signal in signals if signal.get("repo") == repo]


def count_judgments(signals: list[dict[str, Any]]) -> Counter[str]:
    counts: Counter[str] = Counter({judgment: 0 for judgment in JUDGMENTS})
    for signal in signals:
        for entry in signal.get("judgments", []):
            counts[entry["judgment"]] += 1
    return counts


def ratio(numerator: int, denominator: int) -> float | None:
    """Return the ratio, or None when the denominator carries no evidence."""
    if denominator == 0:
        return None
    return numerator / denominator


def harmonic_mean(first: float | None, second: float | None) -> float | None:
    if first is None or second is None or first + second == 0:
        return None
    return 2 * first * second / (first + second)


def summarize(signals: list[dict[str, Any]], min_signals: int) -> dict[str, Any]:
    counts = count_judgments(signals)
    selected = counts["useful"] + counts["noise"] + counts["stale"]
    precision = ratio(counts["useful"], counts["useful"] + counts["noise"])
    recall = ratio(counts["useful"], counts["useful"] + counts["missing"])
    sufficient = sum(1 for signal in signals if signal.get("outcome") == "sufficient")
    return {
        "signals": len(signals),
        "judgments": sum(counts[judgment] for judgment in JUDGMENTS),
        "selected_blocks": selected,
        "useful": counts["useful"],
        "noise": counts["noise"],
        "missing": counts["missing"],
        "stale": counts["stale"],
        "precision": precision,
        "recall": recall,
        "f1": harmonic_mean(precision, recall),
        "stale_rate": ratio(counts["stale"], selected),
        "sufficiency_rate": ratio(sufficient, len(signals)),
        "insufficient_corpus": len(signals) < min_signals,
    }


def block_verdict(counts: Counter[str], min_block_signals: int) -> str:
    """Name the action the feedback loop already defines for this block.

    Vocabulary is `docs/FEEDBACK_LOOP.md`'s, not a new one: recurring `useful` is
    a promotion candidate, recurring `noise` a downgrade candidate, recurring
    `missing` a create/widen candidate, recurring `stale` a freshness flip.
    """
    total = sum(counts[judgment] for judgment in JUDGMENTS)
    if total < min_block_signals:
        return "insufficient-data"
    ranked = sorted(JUDGMENTS, key=lambda judgment: (-counts[judgment], JUDGMENTS.index(judgment)))
    top = ranked[0]
    if counts[top] == counts[ranked[1]]:
        return "mixed"
    return {
        "useful": "keep",
        "noise": "downgrade",
        "missing": "widen-or-create",
        "stale": "refresh",
    }[top]


def per_block(signals: list[dict[str, Any]], min_block_signals: int) -> list[dict[str, Any]]:
    tally: dict[str, Counter[str]] = {}
    for signal in signals:
        for entry in signal.get("judgments", []):
            counts = tally.setdefault(entry["block"], Counter({j: 0 for j in JUDGMENTS}))
            counts[entry["judgment"]] += 1
    # Annotated, not inferred: the literal below is heterogeneous (str, int,
    # str), so mypy joins the value types to `object` and then rejects the
    # `-row["total"]` in the sort key. The declared return type does not
    # propagate backwards into the comprehension.
    rows: list[dict[str, Any]] = [
        {
            "block": block,
            **{judgment: counts[judgment] for judgment in JUDGMENTS},
            "total": sum(counts[judgment] for judgment in JUDGMENTS),
            "verdict": block_verdict(counts, min_block_signals),
        }
        for block, counts in tally.items()
    ]
    rows.sort(key=lambda row: (-row["total"], row["block"]))
    return rows


def format_ratio(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.3f}"


def render_text(summary: dict[str, Any], blocks: list[dict[str, Any]]) -> str:
    lines = [
        f"signals={summary['signals']}",
        f"judgments={summary['judgments']}",
        f"selected_blocks={summary['selected_blocks']}",
        f"useful={summary['useful']}",
        f"noise={summary['noise']}",
        f"missing={summary['missing']}",
        f"stale={summary['stale']}",
        f"precision={format_ratio(summary['precision'])}",
        f"recall={format_ratio(summary['recall'])}",
        f"f1={format_ratio(summary['f1'])}",
        f"stale_rate={format_ratio(summary['stale_rate'])}",
        f"sufficiency_rate={format_ratio(summary['sufficiency_rate'])}",
        f"insufficient_corpus={str(summary['insufficient_corpus']).lower()}",
    ]
    for row in blocks:
        lines.append(
            f"block\t{row['block']}\tuseful={row['useful']}\tnoise={row['noise']}"
            f"\tmissing={row['missing']}\tstale={row['stale']}\tverdict={row['verdict']}"
        )
    return "\n".join(lines) + "\n"


def render_markdown(summary: dict[str, Any], blocks: list[dict[str, Any]], repo: str | None) -> str:
    lines = [
        "# Retrieval Quality",
        "",
        f"Scope: {repo or 'all repos'}",
        f"Signals: {summary['signals']} (`feedback-signal.v1`)",
        "",
        "## Selection quality",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| Precision (useful / selected-and-judged) | {format_ratio(summary['precision'])} |",
        f"| Recall (useful / needed) | {format_ratio(summary['recall'])} |",
        f"| F1 | {format_ratio(summary['f1'])} |",
        f"| Stale rate (freshness axis, not relevance) | {format_ratio(summary['stale_rate'])} |",
        f"| Pack sufficiency rate | {format_ratio(summary['sufficiency_rate'])} |",
        "",
        "## Raw judgments",
        "",
        "| Judgment | Count |",
        "| --- | ---: |",
        f"| useful | {summary['useful']} |",
        f"| noise | {summary['noise']} |",
        f"| missing | {summary['missing']} |",
        f"| stale | {summary['stale']} |",
        "",
    ]
    if summary["insufficient_corpus"]:
        lines.extend([
            "> Corpus is below the acting threshold. Treat these numbers as a",
            "> direction, not a verdict — the bottleneck is signal volume.",
            "",
        ])
    if blocks:
        lines.extend([
            "## Per block",
            "",
            "| Block | useful | noise | missing | stale | Verdict |",
            "| --- | ---: | ---: | ---: | ---: | --- |",
        ])
        for row in blocks:
            lines.append(
                f"| `{row['block']}` | {row['useful']} | {row['noise']} "
                f"| {row['missing']} | {row['stale']} | {row['verdict']} |"
            )
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Score context selection quality from feedback-signal.v1 records. "
            "Reports precision, recall, and per-block verdicts; adds no contract."
        )
    )
    parser.add_argument(
        "input",
        nargs="*",
        type=Path,
        default=[DEFAULT_INPUT],
        help="feedback signal files or directories (default: the local feedback/ surface)",
    )
    parser.add_argument("--repo", help="only score signals whose `repo` matches")
    parser.add_argument("--min-signals", type=int, default=DEFAULT_MIN_SIGNALS)
    parser.add_argument("--min-block-signals", type=int, default=DEFAULT_MIN_BLOCK_SIGNALS)
    parser.add_argument("--format", choices=["text", "markdown"], default="text")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    paths = [path.expanduser() for path in (args.input or [DEFAULT_INPUT])]
    missing = [path for path in paths if not path.exists()]
    if missing:
        print(f"no feedback surface to score: {missing[0]}", file=sys.stderr)
        return 2
    try:
        signals = select_repo(load_signals(paths, load_validator()), args.repo)
    except (OSError, ValueError) as exc:
        print(f"invalid feedback signal: {exc}", file=sys.stderr)
        return 2

    summary = summarize(signals, args.min_signals)
    blocks = per_block(signals, args.min_block_signals)
    if args.format == "markdown":
        sys.stdout.write(render_markdown(summary, blocks, args.repo))
    else:
        sys.stdout.write(render_text(summary, blocks))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
