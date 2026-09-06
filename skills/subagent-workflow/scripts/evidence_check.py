#!/usr/bin/env python3
"""evidence_check.py - mechanical evidence-hygiene linter for the subagent workflow.

The orchestrator runs this before spawning any comprehensive cross-review
round (initial or Phase 6.5 rerun) and again on the drafted PR body/evidence
files before posting at Phase 8. It lints the orchestrator's own bookkeeping -
the artifacts reviewers and the merge gate consume - so stale-evidence
findings stop burning comprehensive review rounds. A review round is the most
expensive linter there is; this closes the classes a script can catch and
leaves reviewers only what machines cannot judge.

Checks:
  placeholder   unreplaced template tokens (`<sha>`, `<fix summary>`, ...) and
                TODO/TBD/FIXME markers. Runs only on orchestrator-authored
                files passed via --file (PR body draft, evidence manifest,
                comment drafts); reviewer-authored reports may legitimately
                quote code or discuss TODOs and are exempt by design.
  head-sha      lines labeling a SHA as the current/frozen head must
                prefix-match the actual HEAD of --root (`git rev-parse HEAD`,
                or --head). Historical anchors such as `Last clean reviewed
                SHA` are not current-head claims and are not checked.
  round-status  "Round K pending/in progress/..." claims are stale once
                .review-gate.json has recorded round K. Skipped with a note
                when no state file exists.
  gate-lock     .review-gate.json says `locked` - the mechanical gate
                transition was skipped or its corrective action has not been
                registered. Spawning reviewers or posting while locked is the
                out-of-band bypass this check exists to catch; a deliberate
                override (e.g. a user-approved descope merge at the terminal
                ceiling) proceeds as a recorded skip block, never silently.
  loop-log      --loop-log-entry validates a pending review-loop-log line
                before it is appended: required keys, fixture level must be a
                single canonical token (none|compact|expanded|high|
                broad-expanded - composites like `expanded/high` and ad-hoc
                labels like `standard` fragment the keep/cut sample), outcome
                vocabulary, date format, and - on a merged line - the schema
                of every `catches[i]`: a `round` (non-negative integer, `0` =
                the fixture-review round) and a `lens` that is exactly one
                canonical lens id (a seat lens or a phase lens, never an
                `a+b` pair). A catch missing either key is unattributable, so
                it silently distorts the lens-rotation figures
                loop_log_audit.py reports. When `round_lenses` is present it
                is checked too: each seat is a canonical lens id or `a+b`
                pair, no lens sits in two seats of one round, round 1 is
                within the fixture level's seat cap (none 1, compact 2,
                expanded 3, high/broad-expanded 4), every later round within
                3, and the number of rounds listed equals `rounds`.

Scanned files: every --file target (all checks) plus *.md/*.txt/*.log under
the review dir from .review-gate.json or --evidence-dir (head-sha and
round-status only).

Exit codes: 0 = clean, 2 = findings or nothing checkable (attention required).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import review_gate

TEXT_SUFFIXES = {".md", ".txt", ".log"}
PLACEHOLDER_RE = re.compile(r"(?<![0-9A-Za-z_])<[A-Za-z][^<>\n]{0,40}>")
MARKER_RE = re.compile(r"\b(TODO|TBD|FIXME)\b")
HEAD_CLAIM_RE = re.compile(
    r"(?i)(?:\bcurrent\s+head\b(?:\s+sha)?|\bfrozen\b[^\n]{0,12}?\bsha\b|\bfull_sha\b|冻结[^\n]{0,8}?SHA)"
    r"[^0-9a-f\n]{0,20}\b([0-9a-f]{7,40})\b"
)
ROUND_CLAIM_RE = re.compile(
    r"(?i)\bround\s*#?\s*(\d+)\b[^\n]{0,40}?"
    r"(?:\bpending\b|\bin[- ]progress\b|\bnot\s+yet\b|待复审|待审|待跑|进行中|未完成)"
)
FIXTURE_LEVELS = ("none", "compact", "expanded", "high", "broad-expanded")
OUTCOMES = ("merged", "ceiling-split", "abandoned", "descoped")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
ENTRY_REQUIRED_KEYS = ("issue", "pr", "date", "fixture", "rounds")
# Canonical lens ids: risk-adaptive-cross-review references/reviewer-packages.md.
SEAT_LENS_IDS = ("correctness", "integration", "security-perf", "test-evidence",
                 "spec-compliance", "invariant-state")
# Lenses that log catches from phases that are not comprehensive rounds.
PHASE_LENS_IDS = ("fixture-review", "final-review", "gap-sweep", "invariant-audit")
ROUND1_SEAT_CAP = {"none": 1, "compact": 2, "expanded": 3, "high": 4, "broad-expanded": 4}
LATER_ROUND_SEAT_CAP = 3

LENS_ALIASES = {"security-performance": "security-perf"}


def canonical_lens(lens: str) -> str:
    """Normalise the spellings the live orchestrators actually emit: a
    `review-` task-id prefix and the `security-performance` long form."""
    lens = lens.strip()
    if lens.startswith("review-"):
        lens = lens[len("review-"):]
    return LENS_ALIASES.get(lens, lens)



def check_catch(raw_path: str, index: int, catch: object, findings: list[str]) -> None:
    """One finding per violation of the compliant-catch schema.

    A catch is attributable only when it carries a non-negative integer
    `round` (`0` is the fixture-review round; bool is not an integer) and a
    non-empty string `lens`. Same definition as loop_log_audit.py.
    """
    where = f"{raw_path}:1: [loop-log] catches[{index}]"
    if not isinstance(catch, dict):
        findings.append(f"{where} must be an object")
        return
    if "round" not in catch:
        findings.append(f"{where} missing `round`")
    else:
        value = catch["round"]
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            findings.append(f"{where} round must be a non-negative integer")
    if "lens" not in catch:
        findings.append(f"{where} missing `lens`")
    else:
        lens = catch["lens"]
        if not isinstance(lens, str) or not lens:
            findings.append(f"{where} lens must be a non-empty string")
        elif canonical_lens(lens) not in SEAT_LENS_IDS and lens not in PHASE_LENS_IDS:
            findings.append(f"{where} lens `{lens}` is off-vocabulary - exactly one lens id: a seat lens "
                            f"({'|'.join(SEAT_LENS_IDS)}) or a phase lens ({'|'.join(PHASE_LENS_IDS)}); "
                            "a finding is attributed to the lens whose checklist produced it, never to an "
                            "`a+b` seat pair")


def check_round_lenses(raw_path: str, entry: dict, findings: list[str]) -> None:
    """Seat-list checks for `round_lenses` (index 0 = round 1), when present."""
    rounds_listed = entry.get("round_lenses")
    if rounds_listed is None:
        return
    where = f"{raw_path}:1: [loop-log] round_lenses"
    if not isinstance(rounds_listed, list):
        findings.append(f"{where} must be a list of per-round seat lists")
        return
    fixture = entry.get("fixture")
    for index, seats in enumerate(rounds_listed):
        label = f"{where}[{index}] (round {index + 1})"
        if not isinstance(seats, list) or not all(isinstance(s, str) and s for s in seats):
            findings.append(f"{label} must be a list of non-empty seat strings")
            continue
        seen: set[str] = set()
        for seat in seats:
            for part in seat.split("+"):
                part = canonical_lens(part)
                if part not in SEAT_LENS_IDS:
                    findings.append(f"{label} seat `{seat}` uses off-vocabulary lens id `{part}` "
                                    f"(canonical: {'|'.join(SEAT_LENS_IDS)}; a paired seat is `a+b`)")
                elif part in seen:
                    findings.append(f"{label} lens `{part}` sits in more than one seat")
                seen.add(part)
        if index == 0:
            cap = ROUND1_SEAT_CAP.get(fixture) if isinstance(fixture, str) else None
            if cap is not None and len(seats) > cap:
                findings.append(f"{label} ran {len(seats)} seats; the round-1 cap for `{fixture}` is {cap}")
        elif len(seats) > LATER_ROUND_SEAT_CAP:
            findings.append(f"{label} ran {len(seats)} seats; post-fix rounds are capped at "
                            f"{LATER_ROUND_SEAT_CAP} (pinned core plus at most one rotated-in seat)")
    rounds = entry.get("rounds")
    if isinstance(rounds, int) and not isinstance(rounds, bool) and rounds >= 0 and len(rounds_listed) != rounds:
        findings.append(f"{where} lists {len(rounds_listed)} round(s) but `rounds` is {rounds} - both count "
                        "comprehensive rounds (index 0 = round 1)")


def check_loop_log_entry(raw_path: str, findings: list[str]) -> None:
    path = Path(raw_path)
    if not path.is_file():
        findings.append(f"{raw_path}:0: [loop-log] --loop-log-entry target missing")
        return
    text = path.read_text(encoding="utf-8").strip()
    try:
        entry = json.loads(text)
    except json.JSONDecodeError as exc:
        findings.append(f"{raw_path}:1: [loop-log] not valid JSON ({exc.msg})")
        return
    if not isinstance(entry, dict):
        findings.append(f"{raw_path}:1: [loop-log] entry must be a single JSON object")
        return
    for key in ENTRY_REQUIRED_KEYS:
        if key not in entry:
            findings.append(f"{raw_path}:1: [loop-log] missing required key `{key}`")
    fixture = entry.get("fixture")
    if fixture is not None and fixture not in FIXTURE_LEVELS:
        findings.append(
            f"{raw_path}:1: [loop-log] fixture `{fixture}` is off-vocabulary - use exactly one of "
            f"{'|'.join(FIXTURE_LEVELS)} (the effective tier, never composites or ad-hoc labels: "
            "off-vocabulary levels fragment the keep/cut sample)"
        )
    outcome = entry.get("outcome", "merged")
    if outcome not in OUTCOMES:
        findings.append(f"{raw_path}:1: [loop-log] outcome `{outcome}` invalid - one of {'|'.join(OUTCOMES)}")
    date = entry.get("date")
    if date is not None and not (isinstance(date, str) and DATE_RE.match(date)):
        findings.append(f"{raw_path}:1: [loop-log] date must be YYYY-MM-DD")
    rounds = entry.get("rounds")
    if rounds is not None and not (isinstance(rounds, int) and rounds >= 0):
        findings.append(f"{raw_path}:1: [loop-log] rounds must be a non-negative integer")
    check_round_lenses(raw_path, entry, findings)
    if outcome == "merged":
        for key in ("gate_net_catch", "verdicts"):
            if key not in entry:
                findings.append(f"{raw_path}:1: [loop-log] merged line missing `{key}` "
                                "(terminal outcomes are exempt)")
        catches = entry.get("catches")
        if catches is not None:
            if not isinstance(catches, list):
                findings.append(f"{raw_path}:1: [loop-log] catches must be a list")
            else:
                for index, catch in enumerate(catches):
                    check_catch(raw_path, index, catch, findings)


def resolve_head(root: Path, head: str | None) -> str | None:
    if head:
        return head.lower()
    proc = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD"],
        capture_output=True, text=True, check=False,
    )
    if proc.returncode != 0:
        return None
    return proc.stdout.strip().lower()


def load_state(root: Path) -> dict | None:
    path = root / review_gate.STATE_NAME
    if not path.is_file():
        return None
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def is_placeholder(token: str) -> bool:
    inner = token[1:-1]
    if "://" in inner or "@" in inner or inner.lower().startswith("http"):
        return False  # autolinks and mail addresses, not template tokens
    return True


def rel(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def scan_file(path: Path, root: Path, head: str, last_round: int | None,
              authored: bool, findings: list[str]) -> None:
    text = path.read_text(encoding="utf-8", errors="replace")
    name = rel(path, root)
    for lineno, line in enumerate(text.splitlines(), 1):
        if authored:
            for m in PLACEHOLDER_RE.finditer(line):
                if is_placeholder(m.group(0)):
                    findings.append(f"{name}:{lineno}: [placeholder] unreplaced template token {m.group(0)}")
            for m in MARKER_RE.finditer(line):
                findings.append(f"{name}:{lineno}: [placeholder] unfinished-work marker {m.group(1)}")
        for m in HEAD_CLAIM_RE.finditer(line):
            claim = m.group(1).lower()
            if not head.startswith(claim):
                findings.append(
                    f"{name}:{lineno}: [head-sha] current/frozen head claim {claim} "
                    f"does not match actual HEAD {head[:12]}"
                )
        if last_round is not None:
            for m in ROUND_CLAIM_RE.finditer(line):
                claimed = int(m.group(1))
                if claimed <= last_round:
                    findings.append(
                        f"{name}:{lineno}: [round-status] round {claimed} claimed pending "
                        f"but the ledger already recorded round {last_round}"
                    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", default=os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd(),
                        help="project root holding %s (default: CLAUDE_PROJECT_DIR or cwd)" % review_gate.STATE_NAME)
    parser.add_argument("--head", default=None,
                        help="expected HEAD SHA (default: git rev-parse HEAD in --root)")
    parser.add_argument("--file", dest="files", action="append", default=[],
                        help="orchestrator-authored artifact (PR body draft, manifest); repeatable, gets all checks")
    parser.add_argument("--evidence-dir", default=None,
                        help="override the review dir from %s" % review_gate.STATE_NAME)
    parser.add_argument("--loop-log-entry", default=None,
                        help="pending review-loop-log line (single JSON object in a file) to validate "
                             "before appending")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    head = resolve_head(root, args.head)
    if head is None:
        print(f"evidence_check: cannot resolve HEAD in {root} - not a git repo? pass --head", file=sys.stderr)
        return 2

    state = load_state(root)
    rounds = (state or {}).get("rounds", [])
    last_round = max((rd["n"] for rd in rounds), default=None) if rounds else None
    if last_round is None:
        print("evidence_check: no recorded rounds - round-status check skipped")

    findings: list[str] = []
    if state and state.get("locked"):
        findings.append(
            f"{review_gate.STATE_NAME}:0: [gate-lock] review gate is locked "
            f"({state.get('lockReason')}) - register the persisted retro (record-retro) before "
            "spawning reviewers or posting; proceeding anyway is a recorded skip block, not a default"
        )
    if args.loop_log_entry:
        check_loop_log_entry(args.loop_log_entry, findings)

    authored: list[Path] = []
    for raw in args.files:
        path = Path(raw)
        if not path.is_file():
            findings.append(f"{raw}:0: [input] --file target missing")
        else:
            authored.append(path.resolve())

    evidence_files: list[Path] = []
    ev_dir = args.evidence_dir or (state or {}).get("reviewDir")
    if ev_dir:
        ev_path = (root / ev_dir).resolve()
        if ev_path.is_dir():
            evidence_files = sorted(
                p.resolve() for p in ev_path.rglob("*")
                if p.is_file() and p.suffix in TEXT_SUFFIXES
            )
        else:
            print(f"evidence_check: review dir not present yet ({ev_path}) - skipped")

    authored_set = set(authored)
    scanned = authored + [p for p in evidence_files if p not in authored_set]
    if not scanned and not args.loop_log_entry and not findings:
        print("evidence_check: nothing to check - pass --file and/or ensure the review dir exists", file=sys.stderr)
        return 2

    for path in scanned:
        scan_file(path, root, head, last_round, path in authored_set, findings)

    for line in findings:
        print(line)
    if findings:
        print(f"evidence_check: {len(findings)} finding(s) - fix the bookkeeping before spawning reviewers or posting",
              file=sys.stderr)
        return 2
    checked = len(scanned) + (1 if args.loop_log_entry else 0)
    print(f"evidence_check: clean ({checked} file(s), head {head[:12]})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
