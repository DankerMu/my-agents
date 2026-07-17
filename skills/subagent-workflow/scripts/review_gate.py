#!/usr/bin/env python3
"""review_gate.py - mechanical state machine for the subagent-workflow three-round hard gate.

The orchestrator records every comprehensive cross-review round here. The CLI
recomputes the gate lock, appends the human-readable ledger line, and refuses
illegal transitions (recording a round that ran while locked, a `converging`
retro that does not qualify) at the moment they are attempted - not at the
pre-merge gate. The optional `review-gate` hook (Claude Code PreToolUse)
denies implementer/reviewer subagent spawns whenever the persisted state says
`locked`; it reads the precomputed `locked`/`lockReason` fields and contains
no gate logic of its own.

State file: <root>/.review-gate.json. Deterministic, stdlib-only.

Commands:
  open         --pr N [--review-dir PATH]
  record-round --sha SHA (--clean | --not-clean) [--verified N]
               [--highest critical|major|minor|none] [--classes a,b]
  record-retro --path FILE --shape breadth|depth|noise|converging
  lock         --reason TEXT        (working-day / same-invariant triggers)
  status       [--assert-unlocked]
  close

Exit codes: 0 = ok/unlocked, 2 = refused or locked (attention required).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

STATE_NAME = ".review-gate.json"
LEDGER_NAME = "round-ledger.log"
SEVERITIES = ["none", "minor", "major", "critical"]
SHAPES = ["breadth", "depth", "noise", "converging"]
DEFAULT_BLOCKED = ["implementer", "reviewer"]


def state_path(root: str) -> Path:
    return Path(root).resolve() / STATE_NAME


def load_state(root: str) -> dict:
    path = state_path(root)
    if not path.is_file():
        raise SystemExit(f"review_gate: no {STATE_NAME} at {path.parent} - run `open --pr <N>` first")
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def save_state(root: str, state: dict) -> None:
    locked, reason = compute_lock(state)
    state["locked"] = locked
    state["lockReason"] = reason
    state_path(root).write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def compute_lock(state: dict) -> tuple[bool, str | None]:
    if state.get("manualLock"):
        return True, (
            f"manual gate ({state['manualLock']}): persist a Review Failure Retro and register it "
            "with record-retro before any further review/fix action"
        )
    rounds = state.get("rounds", [])
    if not rounds or rounds[-1]["clean"] or rounds[-1]["n"] < 3:
        return False, None
    last = rounds[-1]
    retros = state.get("retros", [])
    if not retros:
        return True, (
            f"three-round hard gate: round {last['n']} is not clean and no Review Failure Retro is "
            "registered - persist the retro and run record-retro before any implementer fix, "
            "review round, Phase 7, CI wait, or merge"
        )
    retro = retros[-1]
    if last["n"] < retro["atRound"] + retro["budget"]:
        return False, None
    suffix = "; `converging` is no longer selectable" if any(r["shape"] == "converging" for r in retros) else ""
    return True, (
        f"post-gate budget exhausted: round {last['n']} is not clean after the {retro['shape']} retro "
        f"at round {retro['atRound']} (budget {retro['budget']} round(s)) - register a new retro with a "
        f"stronger corrective action{suffix}"
    )


def severity_rank(sev: str) -> int:
    return SEVERITIES.index(sev)


def compute_repeats(rounds: list[dict], classes: list[str]) -> list[str]:
    first_seen: dict[str, int] = {}
    for rd in rounds:
        for cls in rd.get("classes", []):
            first_seen.setdefault(cls, rd["n"])
    return [f"{cls} (also round {first_seen[cls]})" for cls in classes if cls in first_seen]


def converging_disqualifiers(state: dict) -> list[str]:
    out = []
    rounds = state.get("rounds", [])
    for rd in rounds:
        if rd.get("repeats"):
            out.append(f"failure-class repeat in round {rd['n']}: {'; '.join(rd['repeats'])}")
        if rd["n"] >= 3 and not rd["clean"] and rd.get("highest") in ("critical", "major"):
            out.append(f"{rd['highest']} finding in round {rd['n']}")
    for prev, cur in zip(rounds, rounds[1:]):
        if cur["verified"] > prev["verified"] or severity_rank(cur["highest"]) > severity_rank(prev["highest"]):
            out.append(
                f"trend not non-increasing: round {prev['n']} -> {cur['n']} "
                f"(verified {prev['verified']} -> {cur['verified']}, highest {prev['highest']} -> {cur['highest']})"
            )
    if len(rounds) >= 2 and not any(
        cur["verified"] < prev["verified"] or severity_rank(cur["highest"]) < severity_rank(prev["highest"])
        for prev, cur in zip(rounds, rounds[1:])
    ):
        out.append("no strictly decreasing round-over-round metric (verified count or highest severity)")
    if any(r["shape"] == "converging" for r in state.get("retros", [])):
        out.append("converging already used once for this PR")
    if rounds and rounds[-1]["n"] >= 5:
        out.append("round 5 reached - converging is no longer selectable")
    return out


def ledger_line(rd: dict, gate: str) -> str:
    classes = ", ".join(rd["classes"]) if rd["classes"] else "none"
    repeats = f"yes ({'; '.join(rd['repeats'])})" if rd["repeats"] else "no"
    return (
        f"Round {rd['n']} | {rd['sha']} | {'clean' if rd['clean'] else 'not-clean'} | "
        f"verified findings: {rd['verified']} | highest severity: {rd['highest']} | "
        f"failure classes: {classes} | repeats prior class: {repeats} | gate: {gate}"
    )


def append_ledger(root: str, state: dict, line: str) -> None:
    review_dir = Path(root).resolve() / state["reviewDir"]
    review_dir.mkdir(parents=True, exist_ok=True)
    with (review_dir / LEDGER_NAME).open("a", encoding="utf-8") as fh:
        fh.write(line + "\n")


def cmd_open(args) -> int:
    path = state_path(args.root)
    if path.is_file():
        print(f"review_gate: {path} already exists - run `close` first if the previous PR is done", file=sys.stderr)
        return 2
    state = {
        "enabled": True,
        "pr": args.pr,
        "reviewDir": args.review_dir,
        "rounds": [],
        "retros": [],
        "manualLock": None,
        "blockedSubagents": DEFAULT_BLOCKED,
    }
    save_state(args.root, state)
    print(f"review_gate: opened for PR #{args.pr} (state: {path}, ledger: {args.review_dir}/{LEDGER_NAME})")
    return 0


def cmd_record_round(args) -> int:
    state = load_state(args.root)
    was_locked, prior_reason = state.get("locked", False), state.get("lockReason")
    clean = args.clean
    classes = [c.strip() for c in (args.classes or "").split(",") if c.strip()]
    if not clean and (args.verified is None or args.verified < 1 or args.highest == "none" or not classes):
        print("review_gate: --not-clean requires --verified >= 1, --highest, and --classes "
              "(a not-clean round has at least one actionable finding)", file=sys.stderr)
        return 2
    rd = {
        "n": (state["rounds"][-1]["n"] + 1) if state["rounds"] else 1,
        "sha": args.sha,
        "clean": clean,
        "verified": 0 if clean else args.verified,
        "highest": "none" if clean else args.highest,
        "classes": [] if clean else classes,
        "repeats": [] if clean else compute_repeats(state["rounds"], classes),
        "violation": "recorded-while-locked" if was_locked else None,
    }
    state["rounds"].append(rd)
    save_state(args.root, state)
    locked, reason = state["locked"], state["lockReason"]
    gate = "none"
    if locked:
        gate = "manual" if state.get("manualLock") else ("three-round" if not state["retros"] else "post-gate-budget")
    line = ledger_line(rd, gate)
    append_ledger(args.root, state, line)
    print(line)
    if was_locked:
        append_ledger(args.root, state, f"VIOLATION | round {rd['n']} ran while locked: {prior_reason}")
        print(f"review_gate: VIOLATION - this round ran while the gate was locked ({prior_reason}). "
              f"It is recorded for the accountability log; the gate stays locked.", file=sys.stderr)
        return 2
    if locked:
        print(f"review_gate: GATE LOCKED - {reason}", file=sys.stderr)
        return 2
    return 0


def cmd_record_retro(args) -> int:
    state = load_state(args.root)
    retro_file = Path(args.path)
    if not retro_file.is_file() or not retro_file.read_text(encoding="utf-8").strip():
        print(f"review_gate: retro file missing or empty: {args.path} - persist the retro first", file=sys.stderr)
        return 2
    if args.shape == "converging":
        disqualifiers = converging_disqualifiers(state)
        if disqualifiers:
            print("review_gate: `converging` refused - disqualifiers:", file=sys.stderr)
            for item in disqualifiers:
                print(f"  - {item}", file=sys.stderr)
            print("choose breadth, depth, or noise instead", file=sys.stderr)
            return 2
    at_round = state["rounds"][-1]["n"] if state["rounds"] else 0
    retro = {"atRound": at_round, "shape": args.shape, "path": str(retro_file), "budget": 2 if args.shape == "converging" else 1}
    state["retros"].append(retro)
    state["manualLock"] = None
    save_state(args.root, state)
    line = f"Retro | shape: {args.shape} | at round {at_round} | {retro_file} | budget: {retro['budget']} round(s)"
    append_ledger(args.root, state, line)
    print(f"review_gate: retro registered ({line}); gate unlocked - next action must be the retro's corrective action")
    return 0


def cmd_lock(args) -> int:
    state = load_state(args.root)
    state["manualLock"] = args.reason
    save_state(args.root, state)
    append_ledger(args.root, state, f"Manual gate | {args.reason}")
    print(f"review_gate: locked ({args.reason}) - persist and register a Review Failure Retro to continue")
    return 0


def cmd_status(args) -> int:
    state = load_state(args.root)
    rounds = state["rounds"]
    last = rounds[-1] if rounds else None
    print(f"PR #{state['pr']} | rounds: {len(rounds)} | latest: "
          f"{'-' if not last else ledger_line(last, 'n/a')}")
    print(f"locked: {state['locked']}" + (f" | {state['lockReason']}" if state["locked"] else ""))
    if args.assert_unlocked and state["locked"]:
        print(f"review_gate: assert-unlocked failed - {state['lockReason']}", file=sys.stderr)
        return 2
    return 0


def cmd_close(args) -> int:
    path = state_path(args.root)
    if path.is_file():
        os.remove(path)
        print(f"review_gate: closed ({path} removed)")
    else:
        print("review_gate: nothing to close")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", default=os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd(),
                        help="project root holding %s (default: CLAUDE_PROJECT_DIR or cwd)" % STATE_NAME)
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("open", help="start gate tracking for a PR")
    p.add_argument("--pr", type=int, required=True)
    p.add_argument("--review-dir", default=None)
    p.set_defaults(fn=cmd_open)

    p = sub.add_parser("record-round", help="record a comprehensive cross-review round")
    p.add_argument("--sha", required=True)
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument("--clean", action="store_true")
    group.add_argument("--not-clean", dest="clean", action="store_false")
    p.add_argument("--verified", type=int, default=None, help="verified finding count (CONFIRMED + blocking PLAUSIBLE)")
    p.add_argument("--highest", choices=SEVERITIES, default="none")
    p.add_argument("--classes", default="", help="comma-separated failure classes")
    p.set_defaults(fn=cmd_record_round)

    p = sub.add_parser("record-retro", help="register a persisted Review Failure Retro")
    p.add_argument("--path", required=True)
    p.add_argument("--shape", choices=SHAPES, required=True)
    p.set_defaults(fn=cmd_record_retro)

    p = sub.add_parser("lock", help="manual gate trigger (working-day, same-invariant)")
    p.add_argument("--reason", required=True)
    p.set_defaults(fn=cmd_lock)

    p = sub.add_parser("status", help="print gate state")
    p.add_argument("--assert-unlocked", action="store_true")
    p.set_defaults(fn=cmd_status)

    p = sub.add_parser("close", help="remove gate state (PR merged or abandoned)")
    p.set_defaults(fn=cmd_close)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "open" and args.review_dir is None:
        args.review_dir = f".workplans/pr-{args.pr}/review"
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
