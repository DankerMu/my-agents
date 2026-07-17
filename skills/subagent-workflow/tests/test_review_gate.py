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
- Bookkeeping: every round appends a ledger line; state file is created by
  `open`, removed by `close`.
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


def retro(root: Path, shape: str, *, text: str | None = None, rebuttal: bool = False) -> int:
    if text is None:
        text = DEPTH_EVIDENCE if shape == "depth" else "Review Failure Retro: evidence\n"
    if rebuttal:
        text += SPLIT_REBUTTAL
    path = root / f"retro-{shape}.md"
    path.write_text(text, encoding="utf-8")
    return run(root, "record-retro", "--path", str(path), "--shape", shape)


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
