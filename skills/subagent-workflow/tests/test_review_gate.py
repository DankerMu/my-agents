"""Requirement-driven tests for the three-round hard-gate state machine.

Requirements under test (subagent-workflow SKILL.md Core Rules + phase-flow
Phase 4/5/6.5, versions 0.20.0/0.21.0):
- Rounds 1-2 not clean: ordinary loop continues (unlocked).
- Round 3 not clean, no retro: three-round hard gate locks; recording a round
  that ran while locked is a tagged violation and stays locked.
- Pivot retro (breadth/depth/noise): budget 1 round; still not clean -> locked.
- Converging retro: budget 2 rounds; round 5 not clean -> locked and
  converging no longer selectable; once per PR.
- Converging eligibility: refused on any failure-class repeat (auto-detected),
  any critical/major in a not-clean round >= 3, non-monotonic trend, or no
  strictly decreasing metric.
- Manual gate (working-day / same-invariant): locks until a retro is
  registered.
- Depth obligations (0.25.0): a depth retro must name the invariant and map
  >=2 recurring findings (form-checked); registering depth while the ledger
  shows no class repeat appends a Depth-without-recurrence warning line.
- Split-default escalation (0.25.0): from the second gate entry, depth/noise
  retros are refused without a non-empty `Split rebuttal:`; breadth needs
  none (it is the split) and converging is exempt.
- Round ceiling (0.26.0): 5 comprehensive rounds per PR, absolute. The 5th
  not-clean round is terminal (only a breadth retro registers, lock persists);
  a 6th round is refused and logged as a violation, even after a clean 5th.
- Per-issue ceiling memory (0.28.0): with `open --issue`, a ceiling event is
  recorded in .review-gate-issues.json (survives `close`); a later PR for the
  same issue refuses depth/noise retros without --user-approved (recorded to
  the ledger), leaves breadth/converging untouched, and `close --outcome`
  records how each PR ended. Without --issue, legacy behavior is unchanged.
- Bookkeeping: every round appends a ledger line; state file is created by
  `open`, removed by `close`.
- Clean-round argument conflicts (0.32.0): `record-round --clean` combined
  with an explicit `--verified`, a non-`none` `--highest`, or a non-empty
  `--classes` is refused (exit 2) with state and ledger untouched; a bare
  `--clean` still records 0 / none / [].
- Round SHA correction (0.32.0): `correct-round --round N --sha S --reason R`
  keeps the old SHA, new SHA, and reason under the round's `shaCorrections`,
  updates the effective SHA (visible in `status`), appends one structured
  `CORRECTION` ledger line without rewriting the original round line, and
  leaves round count, metrics, repeats, lock state, and retro budget
  untouched. Unknown round, empty reason, or identical SHA are refused with
  no state change. Corrections are bookkeeping and stay allowed while locked.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import review_gate  # noqa: E402


def run(root: Path, *argv: str) -> int:
    return review_gate.main(["--root", str(root), *argv])


def state(root: Path) -> dict:
    return json.loads((root / ".review-gate.json").read_text(encoding="utf-8"))


def ledger(root: Path) -> str:
    return (root / ".workplans/pr-7/review/round-ledger.log").read_text(encoding="utf-8")


def open_gate(root: Path) -> None:
    assert run(root, "open", "--pr", "7") == 0


def record(root: Path, sha: str, *, clean: bool = False, verified: int = 1,
           highest: str = "major", classes: str = "misc") -> int:
    if clean:
        return run(root, "record-round", "--sha", sha, "--clean")
    return run(root, "record-round", "--sha", sha, "--not-clean",
               "--verified", str(verified), "--highest", highest, "--classes", classes)


DEPTH_EVIDENCE = """Review Failure Retro:
Failure shape: depth
Invariant: staged artifacts must pass receipt validation before publish
Recurring findings:
- publish-before-receipt in lane A (round 1)
- publish-before-receipt in lane C (round 3, sibling surface)
"""

SPLIT_REBUTTAL = "Split rebuttal: all findings share the receipt-validation helper; child PRs would inherit it\n"


def retro(root: Path, shape: str, *, text: str | None = None, rebuttal: bool = False,
          approved: str | None = None) -> int:
    if text is None:
        text = DEPTH_EVIDENCE if shape == "depth" else "Review Failure Retro: evidence\n"
    if rebuttal:
        text += SPLIT_REBUTTAL
    path = root / f"retro-{shape}.md"
    path.write_text(text, encoding="utf-8")
    argv = ["record-retro", "--path", str(path), "--shape", shape]
    if approved is not None:
        argv += ["--user-approved", approved]
    return run(root, *argv)


# --- happy path -----------------------------------------------------------


def test_two_dirty_rounds_stay_unlocked(tmp_path):
    open_gate(tmp_path)
    assert record(tmp_path, "aaa", classes="wrapper") == 0
    assert record(tmp_path, "bbb", classes="schema") == 0
    assert state(tmp_path)["locked"] is False


def test_clean_third_round_stays_unlocked_and_ledger_appends(tmp_path):
    open_gate(tmp_path)
    record(tmp_path, "aaa", classes="wrapper")
    record(tmp_path, "bbb", classes="schema")
    assert record(tmp_path, "ccc", clean=True) == 0
    assert state(tmp_path)["locked"] is False
    lines = ledger(tmp_path).strip().splitlines()
    assert len(lines) == 3
    assert lines[2].startswith("Round 3 | ccc | clean")


def test_open_close_lifecycle(tmp_path):
    open_gate(tmp_path)
    assert run(tmp_path, "open", "--pr", "7") == 2  # double open refused
    assert run(tmp_path, "close") == 0
    assert not (tmp_path / ".review-gate.json").exists()


# --- three-round hard gate ------------------------------------------------


def test_third_dirty_round_locks(tmp_path):
    open_gate(tmp_path)
    record(tmp_path, "aaa", classes="wrapper")
    record(tmp_path, "bbb", classes="schema")
    assert record(tmp_path, "ccc", classes="paths") == 2
    st = state(tmp_path)
    assert st["locked"] is True
    assert "three-round hard gate" in st["lockReason"]


def test_round_recorded_while_locked_is_violation_and_stays_locked(tmp_path):
    open_gate(tmp_path)
    for sha, cls in (("a", "c1"), ("b", "c2"), ("c", "c3")):
        record(tmp_path, sha, classes=cls)
    assert record(tmp_path, "d", classes="c4") == 2
    st = state(tmp_path)
    assert st["rounds"][-1]["violation"] == "recorded-while-locked"
    assert st["locked"] is True
    assert "VIOLATION" in ledger(tmp_path)


def test_status_assert_unlocked(tmp_path):
    open_gate(tmp_path)
    assert run(tmp_path, "status", "--assert-unlocked") == 0
    for sha, cls in (("a", "c1"), ("b", "c2"), ("c", "c3")):
        record(tmp_path, sha, classes=cls)
    assert run(tmp_path, "status", "--assert-unlocked") == 2


# --- pivot retro budget ---------------------------------------------------


def test_pivot_retro_unlocks_then_budget_relocks(tmp_path):
    open_gate(tmp_path)
    for sha, cls in (("a", "c1"), ("b", "c2"), ("c", "c3")):
        record(tmp_path, sha, classes=cls)
    assert retro(tmp_path, "breadth") == 0
    assert state(tmp_path)["locked"] is False
    assert record(tmp_path, "d", classes="c5") == 2  # budget 1 exhausted
    assert "post-gate budget exhausted" in state(tmp_path)["lockReason"]


def test_pivot_retro_then_clean_round_unlocks(tmp_path):
    open_gate(tmp_path)
    for sha, cls in (("a", "c1"), ("b", "c2"), ("c", "c3")):
        record(tmp_path, sha, classes=cls)
    retro(tmp_path, "breadth")
    assert record(tmp_path, "d", clean=True) == 0
    assert state(tmp_path)["locked"] is False


# --- converging retro -----------------------------------------------------


def converging_setup(tmp_path):
    """Rounds 1-3: distinct classes, decreasing counts, minor severities only."""
    open_gate(tmp_path)
    record(tmp_path, "a", verified=5, highest="minor", classes="c1")
    record(tmp_path, "b", verified=3, highest="minor", classes="c2")
    record(tmp_path, "c", verified=1, highest="minor", classes="c3")


def test_converging_eligible_budget_two_then_relock_excludes_converging(tmp_path):
    converging_setup(tmp_path)
    assert retro(tmp_path, "converging") == 0
    assert record(tmp_path, "d", verified=1, highest="minor", classes="c4") == 0  # round 4 within budget
    assert record(tmp_path, "e", verified=1, highest="minor", classes="c5") == 2  # round 5: terminal ceiling
    st = state(tmp_path)
    assert "round ceiling" in st["lockReason"]
    assert retro(tmp_path, "converging") == 2  # terminal: only breadth registers
    assert retro(tmp_path, "breadth") == 0  # split plan documented
    assert state(tmp_path)["locked"] is True  # ceiling lock persists


def test_converging_refused_on_critical_major_in_round_three(tmp_path):
    open_gate(tmp_path)
    record(tmp_path, "a", verified=5, highest="major", classes="c1")
    record(tmp_path, "b", verified=3, highest="minor", classes="c2")
    record(tmp_path, "c", verified=1, highest="major", classes="c3")
    assert retro(tmp_path, "converging") == 2


def test_converging_refused_on_class_repeat_auto_detected(tmp_path):
    open_gate(tmp_path)
    record(tmp_path, "a", verified=5, highest="minor", classes="wrapper")
    record(tmp_path, "b", verified=3, highest="minor", classes="c2")
    record(tmp_path, "c", verified=1, highest="minor", classes="wrapper")
    assert state(tmp_path)["rounds"][-1]["repeats"] == ["wrapper (also round 1)"]
    assert retro(tmp_path, "converging") == 2


def test_converging_refused_on_increasing_or_flat_trend(tmp_path):
    open_gate(tmp_path)
    record(tmp_path, "a", verified=2, highest="minor", classes="c1")
    record(tmp_path, "b", verified=4, highest="minor", classes="c2")
    record(tmp_path, "c", verified=1, highest="minor", classes="c3")
    assert retro(tmp_path, "converging") == 2

    run(tmp_path, "close")
    open_gate(tmp_path)
    record(tmp_path, "a", verified=3, highest="minor", classes="c1")
    record(tmp_path, "b", verified=3, highest="minor", classes="c2")
    record(tmp_path, "c", verified=3, highest="minor", classes="c3")
    assert retro(tmp_path, "converging") == 2  # no strictly decreasing metric


# --- depth obligations + split-default escalation ---------------------------


def test_depth_refused_without_invariant_evidence(tmp_path):
    open_gate(tmp_path)
    for sha, cls in (("a", "wrapper"), ("b", "c2"), ("c", "wrapper")):
        record(tmp_path, sha, classes=cls)
    assert retro(tmp_path, "depth", text="Review Failure Retro: evidence\n") == 2
    assert state(tmp_path)["locked"] is True
    assert retro(tmp_path, "depth") == 0  # full evidence template passes


def test_depth_without_ledger_repeat_registers_with_warning(tmp_path):
    open_gate(tmp_path)
    for sha, cls in (("a", "c1"), ("b", "c2"), ("c", "c3")):
        record(tmp_path, sha, classes=cls)
    assert retro(tmp_path, "depth") == 0  # never force the forbidden split
    assert state(tmp_path)["locked"] is False
    assert "Depth-without-recurrence" in ledger(tmp_path)


def test_depth_with_ledger_repeat_has_no_warning(tmp_path):
    open_gate(tmp_path)
    for sha, cls in (("a", "wrapper"), ("b", "c2"), ("c", "wrapper")):
        record(tmp_path, sha, classes=cls)
    assert retro(tmp_path, "depth") == 0
    assert "Depth-without-recurrence" not in ledger(tmp_path)


def test_second_gate_entry_requires_split_rebuttal_for_depth_noise(tmp_path):
    open_gate(tmp_path)
    for sha, cls in (("a", "wrapper"), ("b", "c2"), ("c", "wrapper")):
        record(tmp_path, sha, classes=cls)
    assert retro(tmp_path, "noise") == 0  # first entry: no rebuttal needed
    assert record(tmp_path, "d", classes="wrapper") == 2  # budget exhausted, second entry
    assert retro(tmp_path, "depth") == 2  # no rebuttal -> refused
    assert retro(tmp_path, "depth", rebuttal=True) == 0


def test_second_gate_entry_breadth_needs_no_rebuttal(tmp_path):
    open_gate(tmp_path)
    for sha, cls in (("a", "c1"), ("b", "c2"), ("c", "c3")):
        record(tmp_path, sha, classes=cls)
    assert retro(tmp_path, "breadth") == 0
    assert record(tmp_path, "d", classes="c4") == 2
    assert retro(tmp_path, "breadth") == 0


# --- round ceiling ----------------------------------------------------------


def climb_to_four_rounds(root: Path) -> None:
    """Rounds 1-3 (locks), breadth retro, round 4 (budget exhausted), breadth retro."""
    open_gate(root)
    for sha, cls in (("a", "c1"), ("b", "c2"), ("c", "c3")):
        record(root, sha, classes=cls)
    assert retro(root, "breadth") == 0
    assert record(root, "d", classes="c4") == 2
    assert retro(root, "breadth") == 0


def test_fifth_round_not_clean_is_terminal(tmp_path):
    climb_to_four_rounds(tmp_path)
    assert record(tmp_path, "e", classes="c5") == 2
    st = state(tmp_path)
    assert "round ceiling" in st["lockReason"]
    assert retro(tmp_path, "noise") == 2  # only breadth registers at terminal
    assert retro(tmp_path, "depth", rebuttal=True) == 2
    assert retro(tmp_path, "breadth") == 0
    assert state(tmp_path)["locked"] is True
    assert record(tmp_path, "f", classes="c6") == 2  # loop stays closed
    assert len(state(tmp_path)["rounds"]) == 5


def test_sixth_round_refused_even_after_clean_fifth(tmp_path):
    climb_to_four_rounds(tmp_path)
    assert record(tmp_path, "e", clean=True) == 0  # clean round 5 -> merge path stays open
    assert state(tmp_path)["locked"] is False
    assert record(tmp_path, "f", clean=True) == 2  # ceiling is absolute
    assert len(state(tmp_path)["rounds"]) == 5
    assert "beyond the 5-round ceiling" in ledger(tmp_path)


def test_ceiling_ledger_gate_field(tmp_path):
    climb_to_four_rounds(tmp_path)
    record(tmp_path, "e", classes="c5")
    assert "gate: round-ceiling" in ledger(tmp_path)


# --- manual gate + input validation ---------------------------------------


def test_manual_lock_blocks_until_retro(tmp_path):
    open_gate(tmp_path)
    record(tmp_path, "a", classes="c1")
    assert run(tmp_path, "lock", "--reason", "working-day") == 0
    assert state(tmp_path)["locked"] is True
    assert retro(tmp_path, "noise") == 0
    assert state(tmp_path)["locked"] is False


def test_not_clean_requires_finding_fields(tmp_path):
    open_gate(tmp_path)
    assert run(tmp_path, "record-round", "--sha", "a", "--not-clean") == 2
    assert state(tmp_path)["rounds"] == []


def test_retro_requires_persisted_file(tmp_path):
    open_gate(tmp_path)
    for sha, cls in (("a", "c1"), ("b", "c2"), ("c", "c3")):
        record(tmp_path, sha, classes=cls)
    assert run(tmp_path, "record-retro", "--path", str(tmp_path / "missing.md"), "--shape", "depth") == 2
    assert state(tmp_path)["locked"] is True


# --- per-issue ceiling memory (0.28.0) --------------------------------------


def history(root: Path) -> dict:
    return json.loads((root / ".review-gate-issues.json").read_text(encoding="utf-8"))


def hit_ceiling(root: Path, pr: int, issue: int) -> None:
    """Open a PR for the issue and drive it to the terminal 5th not-clean round."""
    assert run(root, "open", "--pr", str(pr), "--issue", str(issue)) == 0
    for sha, cls in (("a", "c1"), ("b", "c2"), ("c", "c3")):
        record(root, sha, classes=cls)
    assert retro(root, "breadth") == 0
    assert record(root, "d", classes="c4") == 2
    assert retro(root, "breadth") == 0
    assert record(root, "e", classes="c5") == 2
    assert "round ceiling" in state(root)["lockReason"]


def test_ceiling_recorded_in_issue_history_and_close_outcome(tmp_path):
    hit_ceiling(tmp_path, 292, 291)
    assert history(tmp_path)["issues"]["291"]["ceilingPrs"] == [292]
    assert run(tmp_path, "close", "--outcome", "superseded-by-split") == 0
    closed = history(tmp_path)["issues"]["291"]["closed"]
    assert closed == [{"pr": 292, "outcome": "superseded-by-split", "rounds": 5}]
    assert not (tmp_path / ".review-gate.json").exists()
    assert (tmp_path / ".review-gate-issues.json").exists()  # memory survives close


def test_successor_pr_refuses_depth_noise_without_user_decision(tmp_path):
    hit_ceiling(tmp_path, 292, 291)
    run(tmp_path, "close", "--outcome", "superseded-by-split")
    assert run(tmp_path, "open", "--pr", "305", "--issue", "291") == 0
    assert state(tmp_path)["issueEscalated"]
    for sha, cls in (("a", "wrapper"), ("b", "c2"), ("c", "wrapper")):
        record(tmp_path, sha, classes=cls)
    assert retro(tmp_path, "depth") == 2       # escalated: no silent digging
    assert retro(tmp_path, "noise") == 2
    assert retro(tmp_path, "breadth") == 0     # the split stays the default exit


def test_successor_pr_depth_with_user_decision_registers_and_logs(tmp_path):
    hit_ceiling(tmp_path, 292, 291)
    run(tmp_path, "close", "--outcome", "superseded-by-split")
    run(tmp_path, "open", "--pr", "305", "--issue", "291")
    for sha, cls in (("a", "wrapper"), ("b", "c2"), ("c", "wrapper")):
        record(tmp_path, sha, classes=cls)
    assert retro(tmp_path, "depth", approved="user chose invariant closure over split") == 0
    ledger_305 = (tmp_path / ".workplans/pr-305/review/round-ledger.log").read_text(encoding="utf-8")
    assert "User decision | post-ceiling depth continuation approved" in ledger_305


def test_successor_pr_converging_unaffected_by_escalation(tmp_path):
    hit_ceiling(tmp_path, 292, 291)
    run(tmp_path, "close", "--outcome", "superseded-by-split")
    run(tmp_path, "open", "--pr", "305", "--issue", "291")
    record(tmp_path, "a", verified=5, highest="minor", classes="c1")
    record(tmp_path, "b", verified=3, highest="minor", classes="c2")
    record(tmp_path, "c", verified=1, highest="minor", classes="c3")
    assert retro(tmp_path, "converging") == 0


def test_same_pr_reopen_is_not_escalated(tmp_path):
    hit_ceiling(tmp_path, 292, 291)
    run(tmp_path, "close")
    run(tmp_path, "open", "--pr", "292", "--issue", "291")
    assert state(tmp_path)["issueEscalated"] is None


def test_without_issue_flag_legacy_behavior_and_no_history(tmp_path):
    open_gate(tmp_path)  # no --issue
    for sha, cls in (("a", "wrapper"), ("b", "c2"), ("c", "wrapper")):
        record(tmp_path, sha, classes=cls)
    assert retro(tmp_path, "depth") == 0
    assert run(tmp_path, "close", "--outcome", "merged") == 0
    assert not (tmp_path / ".review-gate-issues.json").exists()


def test_gate_entries_counted_per_issue(tmp_path):
    assert run(tmp_path, "open", "--pr", "10", "--issue", "8") == 0
    for sha, cls in (("a", "c1"), ("b", "c2"), ("c", "c3")):
        record(tmp_path, sha, classes=cls)
    assert retro(tmp_path, "breadth") == 0
    assert history(tmp_path)["issues"]["8"]["gateEntries"] == 1
    assert history(tmp_path)["issues"]["8"]["ceilingPrs"] == []


# --- clean-round argument conflicts (0.32.0) ---------------------------------


def _ledger_or_none(root: Path) -> str | None:
    path = root / ".workplans/pr-7/review/round-ledger.log"
    return path.read_text(encoding="utf-8") if path.is_file() else None


def test_clean_with_explicit_verified_zero_is_refused(tmp_path, capsys):
    open_gate(tmp_path)
    assert run(tmp_path, "record-round", "--sha", "a", "--clean", "--verified", "0") == 2
    assert state(tmp_path)["rounds"] == []
    assert _ledger_or_none(tmp_path) is None
    err = capsys.readouterr().err
    assert "--verified" in err and "zero FIX_NOW findings" in err


def test_clean_with_highest_is_refused(tmp_path, capsys):
    open_gate(tmp_path)
    assert run(tmp_path, "record-round", "--sha", "a", "--clean", "--highest", "minor") == 2
    assert state(tmp_path)["rounds"] == []
    assert _ledger_or_none(tmp_path) is None
    assert "--highest" in capsys.readouterr().err


def test_clean_with_classes_is_refused(tmp_path, capsys):
    open_gate(tmp_path)
    assert run(tmp_path, "record-round", "--sha", "a", "--clean", "--classes", "doc-citation-accuracy") == 2
    assert state(tmp_path)["rounds"] == []
    assert _ledger_or_none(tmp_path) is None
    assert "--classes" in capsys.readouterr().err


def test_clean_conflict_after_prior_rounds_leaves_state_and_ledger_untouched(tmp_path):
    open_gate(tmp_path)
    assert record(tmp_path, "a", classes="c1") == 0
    before_state, before_ledger = state(tmp_path), ledger(tmp_path)
    assert run(tmp_path, "record-round", "--sha", "b", "--clean",
               "--verified", "8", "--highest", "minor", "--classes", "c9") == 2
    assert state(tmp_path) == before_state
    assert ledger(tmp_path) == before_ledger


def test_bare_clean_still_records_neutral_fields(tmp_path):
    open_gate(tmp_path)
    assert run(tmp_path, "record-round", "--sha", "a", "--clean") == 0
    rd = state(tmp_path)["rounds"][0]
    assert (rd["clean"], rd["verified"], rd["highest"], rd["classes"], rd["repeats"]) == (True, 0, "none", [], [])
    assert "Round 1 | a | clean | verified findings: 0 | highest severity: none | failure classes: none" in ledger(tmp_path)


# --- round SHA correction (0.32.0) --------------------------------------------


def _without_sha(rd: dict) -> dict:
    return {k: v for k, v in rd.items() if k not in ("sha", "shaCorrections")}


def test_correct_round_updates_sha_and_appends_audit_line(tmp_path, capsys):
    open_gate(tmp_path)
    assert record(tmp_path, "aaa1", classes="c1") == 0
    assert record(tmp_path, "bbb2", classes="c2") == 0
    before_state, before_ledger = state(tmp_path), ledger(tmp_path)
    assert run(tmp_path, "correct-round", "--round", "2", "--sha", "ccc3",
               "--reason", "reviewers reviewed the pre-fix head") == 0
    after = state(tmp_path)
    rd = after["rounds"][1]
    assert rd["sha"] == "ccc3"
    assert rd["shaCorrections"] == [{"from": "bbb2", "to": "ccc3", "reason": "reviewers reviewed the pre-fix head"}]
    # nothing else moved: round 1 identical, round 2 identical apart from the corrected fields,
    # lock/retro/issue fields identical
    assert after["rounds"][0] == before_state["rounds"][0]
    assert _without_sha(rd) == _without_sha(before_state["rounds"][1])
    assert {k: v for k, v in after.items() if k != "rounds"} == {k: v for k, v in before_state.items() if k != "rounds"}
    # ledger: original lines preserved verbatim, exactly one structured correction appended
    after_ledger = ledger(tmp_path)
    assert after_ledger.startswith(before_ledger)
    added = after_ledger[len(before_ledger):].splitlines()
    assert added == ["CORRECTION | sha bbb2 -> ccc3 | reason: reviewers reviewed the pre-fix head | round 2"]
    assert "Round 2 | bbb2 |" in after_ledger
    # status reports the corrected SHA
    capsys.readouterr()
    assert run(tmp_path, "status") == 0
    assert "Round 2 | ccc3 |" in capsys.readouterr().out


def test_correct_round_repeated_corrections_keep_full_history(tmp_path):
    open_gate(tmp_path)
    assert record(tmp_path, "a", classes="c1") == 0
    assert run(tmp_path, "correct-round", "--round", "1", "--sha", "b", "--reason", "first fix") == 0
    assert run(tmp_path, "correct-round", "--round", "1", "--sha", "c", "--reason", "second fix") == 0
    rd = state(tmp_path)["rounds"][0]
    assert rd["sha"] == "c"
    assert [(x["from"], x["to"]) for x in rd["shaCorrections"]] == [("a", "b"), ("b", "c")]
    assert ledger(tmp_path).count("CORRECTION |") == 2


def test_correct_round_does_not_change_gate_math(tmp_path):
    open_gate(tmp_path)
    for sha, cls in (("a", "c1"), ("b", "c2"), ("c", "c3")):
        record(tmp_path, sha, classes=cls)
    assert state(tmp_path)["locked"] is True  # three-round hard gate
    before = state(tmp_path)
    assert run(tmp_path, "correct-round", "--round", "3", "--sha", "c-prime", "--reason", "misrecorded head") == 0
    after = state(tmp_path)
    assert after["locked"] is True and after["lockReason"] == before["lockReason"]
    assert len(after["rounds"]) == 3
    # a retro registers exactly as it would have, with the same budget
    assert retro(tmp_path, "noise") == 0
    assert state(tmp_path)["retros"][-1]["budget"] == 1
    assert state(tmp_path)["locked"] is False
    # repeats still computed from classes, unaffected by SHA edits
    assert record(tmp_path, "d", classes="c1") == 2  # budget exhausted -> relock
    assert state(tmp_path)["rounds"][-1]["repeats"] == ["c1 (also round 1)"]


def test_correct_round_refuses_unknown_round_empty_reason_and_same_sha(tmp_path):
    open_gate(tmp_path)
    assert record(tmp_path, "a", classes="c1") == 0
    before_state, before_ledger = state(tmp_path), ledger(tmp_path)
    assert run(tmp_path, "correct-round", "--round", "2", "--sha", "b", "--reason", "r") == 2
    assert run(tmp_path, "correct-round", "--round", "0", "--sha", "b", "--reason", "r") == 2
    assert run(tmp_path, "correct-round", "--round", "1", "--sha", "b", "--reason", "   ") == 2
    assert run(tmp_path, "correct-round", "--round", "1", "--sha", "a", "--reason", "r") == 2
    assert state(tmp_path) == before_state
    assert ledger(tmp_path) == before_ledger
    assert "shaCorrections" not in state(tmp_path)["rounds"][0]
