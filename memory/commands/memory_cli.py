#!/usr/bin/env python3
"""`mqobsidian memory` — the operator control plane for the autonomous scoring loop.

Tracked code over local-only data: stdlib-only (argparse), reads only local evidence. This is
NOT a moderation queue: the scoring engine (emit_generic_score) moves observations
between tiers automatically. This CLI is the *inspect/explain* surface so the operator
can see and understand what the machine did — without becoming the bottleneck.

    mqobsidian memory score --dry-run     # show what WOULD change; write nothing (default)
    mqobsidian memory score --apply       # run scoring; write memory-score.v1 + promotion-event.v1
    mqobsidian memory score --apply --writeback-promoted  # + write learn files for promoted memories
    mqobsidian memory status              # tier tally + held + quarantined
    mqobsidian memory explain <memory-id> # exactly why a memory got its tier
    mqobsidian memory quarantine          # invalid / conflicting / risky / superseding review queues
    mqobsidian memory promote-from-review <memory-id> --apply   # land a held promotion proposal
    mqobsidian memory resolve-supersede <memory-id> --accept|--reject --apply  # action a conflict

Invoke directly today as `python3 memory_cli.py <cmd>` (no console-script entrypoint
exists yet; the whole scoring layer is local-only). No auto-publication; promotion is
not publication (public export stays a separate, gated step).
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import emit_generic_score as egs
import emit_learn_writeback as lw
import emit_memory_score as ems
import transition_journal as tj

VAULT = Path(__file__).resolve().parents[2]


def _builder():
    """Load the export builder (a dashed script name, so not importable)."""
    path = VAULT / "scripts" / "build-truth-exports.py"
    spec = importlib.util.spec_from_file_location("build_truth_exports", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _add_paths(p: argparse.ArgumentParser) -> None:
    """Advanced/test overrides; default to the real local-only surfaces."""
    p.add_argument("--inbox", type=Path, default=egs.INBOX_DIR, help=argparse.SUPPRESS)
    p.add_argument("--out", type=Path, default=egs.OUT, help=argparse.SUPPRESS)
    p.add_argument("--feedback", type=Path, default=ems.FEEDBACK, help=argparse.SUPPRESS)


def _evaluate(args) -> dict:
    """Read-only computation against the current local inbox + promotions trail."""
    promotions = egs._promotions_path(args.out)
    return egs.evaluate(
        args.inbox,
        feedback_path=args.feedback,
        prior=egs._last_known_tiers(promotions),
        promoted_dates=egs._first_promoted_dates(promotions),
        snapshots=egs._load_snapshots(args.out),
        resolved=egs._load_resolved_supersedes(args.out),
    )


def cmd_score(args) -> int:
    dry = not args.apply
    summary = egs.run(args.inbox, args.out, feedback_path=args.feedback, dry_run=dry)
    t = summary["tally"]
    held = (summary["review"]["conflicting"] + summary["review"]["risky"]
            + summary["review"]["superseding"] + summary["review"]["promotion-review"])
    verb = "would write" if dry else "written"
    print("Observation scoring summary" + ("  (dry-run — nothing written)" if dry else ""))
    print()
    print(f"observed:     {t['observed']}")
    print(f"candidate:    {t['candidate']}")
    print(f"promoted:     {t['promoted']}")
    print(f"deprecated:   {t['deprecated']}")
    print(f"held:         {held}")
    print(f"quarantined:  {summary['invalid']}")
    print()
    print(f"promotion events {verb}: {summary['new_events']}")
    print(f"scores {verb}: {summary['memories']}")
    if getattr(args, "writeback_promoted", False):
        # Convenience: chain learn-writeback in the same run. scoring writes the
        # scores first (in --apply), then writeback consumes them; same dry/apply
        # mode, so `score --dry-run --writeback-promoted` previews both steps.
        print()
        _writeback(args, dry)
    return 0


def cmd_status(args) -> int:
    summary = _evaluate(args)["summary"]
    t = summary["tally"]
    held = (summary["review"]["conflicting"] + summary["review"]["risky"]
            + summary["review"]["superseding"] + summary["review"]["promotion-review"])
    if getattr(args, "json", False):
        # Consumed by mq-agent `memory review-status --json`; keep the shape stable.
        print(json.dumps({
            "schema": "mqobsidian.memory-status.v1",
            "observations": {"total": summary["observations"], "valid": summary["valid"],
                             "invalid": summary["invalid"]},
            "memories": summary["memories"],
            "tiers": {k: t[k] for k in ("observed", "candidate", "promoted", "deprecated")},
            "held": {"total": held, **{k: summary["review"][k] for k in
                     ("conflicting", "risky", "superseding", "promotion-review")}},
            "quarantined": summary["invalid"],
            "tier_changes": summary["new_events"],
        }, indent=2))
        return 0
    print("Memory status (computed from the current local inbox)")
    print()
    print(f"observations: {summary['observations']}  (valid: {summary['valid']}, invalid: {summary['invalid']})")
    print(f"memories:     {summary['memories']}")
    print()
    print(f"observed:     {t['observed']}")
    print(f"candidate:    {t['candidate']}")
    print(f"promoted:     {t['promoted']}")
    print(f"deprecated:   {t['deprecated']}")
    print(f"held:         {held}  (conflicting: {summary['review']['conflicting']}, "
          f"risky: {summary['review']['risky']}, superseding: {summary['review']['superseding']}, "
          f"promotion-review: {summary['review']['promotion-review']})")
    print(f"quarantined:  {summary['invalid']}")
    print(f"tier changes vs last run: {summary['new_events']}")
    return 0


def cmd_explain(args) -> int:
    result = _evaluate(args)
    d = result["decisions"].get(args.memory_id)
    if d is None:
        ids = sorted(result["decisions"])
        print(f"unknown memory_id: {args.memory_id!r}", file=sys.stderr)
        if ids:
            print("known memory ids:", file=sys.stderr)
            for mid in ids:
                print(f"  {mid}", file=sys.stderr)
        return 1
    f = d["score_record"]["factors"]
    print(f"memory_id: {args.memory_id}")
    print(f"status: {d['tier']}")
    print(f"ebms_state: {d['ebms_state']}")
    print(f"score: {d['score']}")
    print(f"risk: {d['risk_level']}")
    print("factors:")
    for k in ("frequency", "source_count", "confidence", "recency", "usage_score", "manual_boost"):
        print(f"  {k}: {f[k]}")
    print("reason:")
    for line in d["rationale"]:
        print(f"  {line}")
    return 0


def cmd_quarantine(args) -> int:
    result = _evaluate(args)
    print("Review queues (held for human — the only exceptions)")
    print()
    invalid = result["invalid"]
    print(f"invalid ({len(invalid)}):")
    for it in invalid:
        print(f"  - {it['reason']}")
    if not invalid:
        print("  (none)")
    for bucket in ("conflicting", "risky", "promotion-review"):
        items = result["review"][bucket]
        print(f"{bucket} ({len(items)}):")
        for it in items:
            risk = f" ({it['risk_level']})" if it.get("risk_level") and it["risk_level"] != "low" else ""
            print(f"  - {it['memory_id']}{risk}: {it['reason']}")
        if not items:
            print("  (none)")

    # Deep conflict: promoted memories with a proposed supersede, held for human resolution.
    superseding = result["review"]["superseding"]
    print(f"superseding ({len(superseding)}):")
    for it in superseding:
        print(f"  - {it['memory_id']} ({it['trigger']}): "
              f"promoted=\"{it['promoted_directive']}\" → current=\"{it['current_directive']}\"")
    if not superseding:
        print("  (none)")
    return 0


def _writeback(args, dry: bool) -> dict:
    """Run learn-writeback for PROMOTED memories and print its summary.

    Shared by `learn-writeback` and `score --writeback-promoted` so the two
    surfaces can never drift. Reads the scores dir (written by `score --apply`);
    candidate/observed never write to memory/learn/."""
    s = lw.writeback(
        scores_dir=egs._scores_dir(args.out),
        inbox_dir=args.inbox,
        promotions_path=egs._promotions_path(args.out),
        learn_dir=args.learn_dir,
        dry_run=dry,
    )
    verb = "would write" if dry else "wrote"
    print("Learn-writeback" + ("  (dry-run — nothing written)" if dry else ""))
    print()
    print(f"promoted memories: {s['promoted']}")
    print(f"{verb}: {s['written']}    unchanged: {s['unchanged']}")
    print()
    for d in s["details"]:
        print(f"  [{d['category']}] learn/{d['rel']}  ({d['status']})")
    if not s["details"]:
        print("  (no promoted memories — nothing to write)")
    return s


def cmd_learn_writeback(args) -> int:
    """Explicit operator action: materialise durable agent-readable memory for PROMOTED
    memories only. Separate from `score --apply` on purpose — scoring decides, writeback
    consumes. candidate/observed never write to memory/learn/."""
    _writeback(args, not args.apply)
    return 0


def cmd_promote_from_review(args) -> int:
    """Operator action: approve a memory in the promotion-review queue → promote it.
    Co-change never auto-promotes, so this is how a human lands a strong cluster: it
    appends a promotion-event.v1 (-> promoted) and snapshots the directive."""
    result = _evaluate(args)
    queued = {it["memory_id"] for it in result["review"]["promotion-review"]}
    d = result["decisions"].get(args.memory_id)
    if args.memory_id not in queued:
        print(f"{args.memory_id!r} is not in the promotion-review queue.", file=sys.stderr)
        if d is not None:
            print(f"  (current status: {d['tier']})", file=sys.stderr)
        for mid in sorted(queued):
            print(f"  in queue: {mid}", file=sys.stderr)
        return 1
    dry = not args.apply
    m = result["metrics"][args.memory_id]
    print("Promote from review" + ("  (dry-run — nothing written)" if dry else ""))
    print()
    print(f"memory_id: {args.memory_id}")
    print(f"from: {d['tier']}  ->  promoted")
    print(f"directive: {d['directive']}")
    if dry:
        print("\nwould: append promotion-event.v1 (-> promoted) + capture directive snapshot")
        return 0
    egs.record_promotion(args.out, args.memory_id, m, d["tier"], d["directive"], d["directive_hash"],
                         reason="Promoted by human review (promotion-review queue).")
    print("\npromoted: promotion-event.v1 appended + snapshot captured")
    return 0


def cmd_resolve_supersede(args) -> int:
    """Operator action: accept (adopt the new directive as authoritative) or reject (keep
    the promoted directive; dismiss the conflict) a supersede proposal. The promoted memory
    is never auto-rewritten — this is the only way to change it."""
    result = _evaluate(args)
    items = {it["memory_id"]: it for it in result["review"]["superseding"]}
    if args.memory_id not in items:
        print(f"{args.memory_id!r} has no open supersede proposal.", file=sys.stderr)
        for mid in sorted(items):
            print(f"  open: {mid}", file=sys.stderr)
        return 1
    it = items[args.memory_id]
    dry = not args.apply
    action = "accept (adopt new directive)" if args.accept else "reject (keep promoted directive)"
    print("Resolve supersede" + ("  (dry-run — nothing written)" if dry else ""))
    print()
    print(f"memory_id: {args.memory_id}  ({it['trigger']})")
    print(f"promoted: {it['promoted_directive']}")
    print(f"current:  {it['current_directive']}")
    print(f"resolution: {action}")
    if dry:
        return 0
    if args.accept:
        egs._write_snapshot_file(args.out, args.memory_id, it["current_directive"],
                                 it["current_hash"], it.get("promoted_at"))
        egs.append_resolved_supersede(args.out, args.memory_id, it["current_hash"], "accepted",
                                      note="adopted current directive as authoritative")
        print("\naccepted: snapshot updated to the current directive; memory stays promoted")
    else:
        egs.append_resolved_supersede(args.out, args.memory_id, it["current_hash"], "rejected",
                                      note="kept promoted directive; conflict dismissed")
        print("\nrejected: promoted directive kept; this conflict will no longer be re-proposed")
    return 0


def _load_evidence_manifest(exports: Path) -> dict:
    """Evidence authority is the exported manifest, not the raw observations.

    A transition may only cite evidence that has actually been published, so an
    unbuilt export blocks transitions rather than letting them cite anything.
    """
    path = exports / "memory-evidence-manifest.json"
    if not path.exists():
        raise tj.TransitionError(
            f"no evidence manifest at {path}; run build-truth-exports.py first"
        )
    return json.loads(path.read_text(encoding="utf-8"))


def _projected_score(plan: dict) -> dict:
    """The score record as the transition will leave it (for the projection)."""
    score = dict(plan["score"])
    score["status"] = plan["to"]
    score["_path"] = Path(plan["score_path"]).name
    if plan["to"] == "promoted":
        score["promoted_at"] = datetime.now(timezone.utc).date().isoformat()
    return score


def _learn_target(plan: dict, *, inbox_dir: Path, learn_dir: Path) -> tuple[Path | None, Any]:
    """Where the learn projection lives, and how to build it.

    Only promote writes one and only rollback removes one; the other three
    verbs have no learn effect, so they stage no learn path at all.
    """
    if not (plan["writes_learn"] or plan["removes_learn"]):
        return None, None
    memory_id = plan["memory_id"]
    observations = lw.observations_by_key(inbox_dir).get(memory_id, [])
    score = _projected_score(plan)
    subdir, fname, _ = lw.build_learning(score, observations, "")
    path = learn_dir / subdir / fname
    if plan["removes_learn"]:
        return path, None

    def builder(event: dict) -> str:
        # Built from the event so the record cites the promotion that authorises it.
        _, _, content = lw.build_learning(score, observations, event["id"])
        return content

    return path, builder


def _durable_effect(plan: dict, learn_path: Path | None) -> dict:
    if plan["writes_learn"]:
        return {"learn": "write", "path": str(learn_path)}
    if plan["removes_learn"]:
        return {"learn": "remove", "path": str(learn_path)}
    return {"learn": "none", "path": None}


def _revert(plan: dict, *, learn_path: Path | None, prior_learn: str | None) -> None:
    """Put score and projection back as they were before the transition."""
    Path(plan["score_path"]).write_text(
        json.dumps(plan["score"], indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    if learn_path is None:
        return
    if prior_learn is None:
        if learn_path.exists():
            learn_path.unlink()
    else:
        learn_path.parent.mkdir(parents=True, exist_ok=True)
        learn_path.write_text(prior_learn, encoding="utf-8")


def _point_builder_at(builder, args, scores_dir: Path) -> None:
    """Bind the builder to this invocation's sources (defaults are the real ones)."""
    builder.SCORES_DIR = scores_dir
    builder.OBSERVATIONS_DIR = args.inbox
    builder.EXPORTS = args.exports
    if args.policy is not None:
        builder.POLICY_SOURCE = args.policy


def cmd_transition(args) -> int:
    """One of the five locked verbs. Preview by default; --apply writes.

    An applied transition is only reported as success once the full canonical
    export bundle has been rebuilt and validated. If the rebuild fails the
    transition is compensated and prior truth is rebuilt; if that also fails,
    the index is marked drifted and this fails closed rather than leaving
    published truth quietly wrong.
    """
    scores_dir = egs._scores_dir(args.out)
    try:
        plan = tj.plan_transition(
            args.verb,
            args.memory_id,
            scores_dir=scores_dir,
            evidence_manifest=_load_evidence_manifest(args.exports),
            evidence_refs=list(args.evidence or []),
            reason=args.reason,
        )
        learn_path, learn_builder = _learn_target(
            plan, inbox_dir=args.inbox, learn_dir=args.learn_dir
        )
    except tj.TransitionError as exc:
        print(json.dumps({"ok": False, "verb": args.verb, "memory_id": args.memory_id,
                          "error": str(exc)}, indent=2))
        return 1

    transition = {
        "verb": plan["verb"],
        "memory_id": plan["memory_id"],
        "from": plan["from"],
        "to": plan["to"],
        "reason": plan["reason"],
    }
    evidence = {"source_evidence_refs": plan["source_evidence_refs"], "resolved": True}
    effect = _durable_effect(plan, learn_path)

    if not args.apply:
        print(json.dumps({
            "ok": True, "mode": "preview", "transition": transition,
            "evidence": evidence, "event": None, "durable_effect": effect,
        }, indent=2))
        return 0

    prior_learn = (
        learn_path.read_text(encoding="utf-8")
        if learn_path is not None and learn_path.exists()
        else None
    )
    result = tj.apply_transition(
        plan,
        journal_dir=args.out / "journal",
        events_path=egs._promotions_path(args.out),
        learn_path=learn_path,
        learn_builder=learn_builder,
    )
    event = result["event"]

    builder = _builder()
    _point_builder_at(builder, args, scores_dir)
    problems = builder.rebuild()
    if not problems:
        print(json.dumps({
            "ok": True, "mode": "applied", "transition": transition, "evidence": evidence,
            "event": event, "durable_effect": effect, "journal_id": result["journal_id"],
        }, indent=2))
        return 0

    # Rebuild failed: published truth is unchanged but local state has moved.
    failure: dict[str, Any] = {
        "ok": False, "mode": "applied", "transition": transition, "event": event,
        "error": "export rebuild failed after the transition",
        "problems": problems,
    }
    try:
        compensation = tj.compensate(
            event,
            events_path=egs._promotions_path(args.out),
            reason="export rebuild failed; transition compensated",
        )
        _revert(plan, learn_path=learn_path, prior_learn=prior_learn)
        recovery = builder.rebuild()
        if recovery:
            raise tj.TransitionError(
                "rebuild of prior truth also failed: " + "; ".join(recovery)
            )
        failure["compensated"] = compensation["id"]
        failure["recovery"] = "prior truth rebuilt"
    except Exception as exc:  # compensation itself failed: fail closed, loudly
        failure["compensation_error"] = str(exc)
        try:
            builder.mark_drift()
            failure["recovery"] = "index marked drift: true; published truth is not current"
        except Exception as drift_exc:
            failure["recovery"] = f"could not even mark drift: {drift_exc}"
    print(json.dumps(failure, indent=2))
    return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="mqobsidian memory", description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)

    p_score = sub.add_parser("score", help="score the inbox (dry-run by default)")
    mode = p_score.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="show what would change; write nothing (default)")
    mode.add_argument("--apply", action="store_true", help="run scoring and persist outputs")
    p_score.add_argument(
        "--writeback-promoted", action="store_true",
        help="after scoring, also write learn files for promoted memories "
             "(combines score + learn-writeback in one run; honours --dry-run/--apply)",
    )
    _add_paths(p_score)
    p_score.add_argument("--learn-dir", type=Path, default=lw.LEARN_DIR, help=argparse.SUPPRESS)
    p_score.set_defaults(func=cmd_score)

    for name, fn, help_ in (
        ("status", cmd_status, "tier tally + held + quarantined"),
        ("quarantine", cmd_quarantine, "show the invalid / conflicting / risky / superseding queues"),
    ):
        p = sub.add_parser(name, help=help_)
        _add_paths(p)
        p.set_defaults(func=fn)
        if name == "status":
            p.add_argument("--json", action="store_true", help="machine-readable output")

    p_explain = sub.add_parser("explain", help="explain exactly why a memory got its tier")
    p_explain.add_argument("memory_id")
    _add_paths(p_explain)
    p_explain.set_defaults(func=cmd_explain)

    p_lw = sub.add_parser("learn-writeback", help="write durable agent-readable memory for PROMOTED memories")
    lw_mode = p_lw.add_mutually_exclusive_group()
    lw_mode.add_argument("--dry-run", action="store_true", help="show what would be written; write nothing (default)")
    lw_mode.add_argument("--apply", action="store_true", help="write learning files for promoted memories")
    _add_paths(p_lw)
    p_lw.add_argument("--learn-dir", type=Path, default=lw.LEARN_DIR, help=argparse.SUPPRESS)
    p_lw.set_defaults(func=cmd_learn_writeback)

    p_pfr = sub.add_parser("promote-from-review", help="approve a promotion-review memory → promote it")
    pfr_mode = p_pfr.add_mutually_exclusive_group()
    pfr_mode.add_argument("--dry-run", action="store_true", help="show what would happen; write nothing (default)")
    pfr_mode.add_argument("--apply", action="store_true", help="append the promotion-event and snapshot")
    p_pfr.add_argument("memory_id")
    _add_paths(p_pfr)
    p_pfr.set_defaults(func=cmd_promote_from_review)

    p_rs = sub.add_parser("resolve-supersede", help="accept/reject a supersede proposal")
    rs_res = p_rs.add_mutually_exclusive_group(required=True)
    rs_res.add_argument("--accept", action="store_true", help="adopt the new directive as authoritative")
    rs_res.add_argument("--reject", action="store_true", help="keep the promoted directive; dismiss the conflict")
    rs_mode = p_rs.add_mutually_exclusive_group()
    rs_mode.add_argument("--dry-run", action="store_true", help="show what would happen; write nothing (default)")
    rs_mode.add_argument("--apply", action="store_true", help="persist the resolution")
    p_rs.add_argument("memory_id")
    _add_paths(p_rs)
    p_rs.set_defaults(func=cmd_resolve_supersede)

    # The five locked transition verbs. Named subcommands, not a generic
    # `transition --to <state>` passthrough: an owner verb is a contract, and
    # the from-state is enforced by the state machine, not by the caller.
    for verb, (from_state, to_state) in tj.TRANSITIONS.items():
        p_t = sub.add_parser(verb, help=f"{from_state} -> {to_state} (preview by default)")
        t_mode = p_t.add_mutually_exclusive_group()
        t_mode.add_argument("--dry-run", action="store_true",
                            help="show the planned transition; write nothing (default)")
        t_mode.add_argument("--apply", action="store_true",
                            help="apply the transition and rebuild the export bundle")
        p_t.add_argument("memory_id")
        p_t.add_argument("--reason", required=True, help="why this transition is justified")
        p_t.add_argument("--evidence", action="append", metavar="REF",
                         help="published evidence ref (repeatable; required for promote)")
        _add_paths(p_t)
        p_t.add_argument("--learn-dir", type=Path, default=lw.LEARN_DIR, help=argparse.SUPPRESS)
        p_t.add_argument("--exports", type=Path, default=VAULT / "exports", help=argparse.SUPPRESS)
        p_t.add_argument("--policy", type=Path, default=None, help=argparse.SUPPRESS)
        p_t.set_defaults(func=cmd_transition, verb=verb)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
