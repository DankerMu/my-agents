"""Requirement-driven tests for the keep/cut decidability audit.

Requirements under test (phase-flow Phase 8 Cross-Run Loop Accountability,
version 0.28.0):
- R1 keep/cut per fixture level: DECIDABLE (exit 2) only when a canonical
  level reaches --min-sample merged PRs with zero total gate_net_catch;
  below the sample or with any catch it stays informational (exit 0).
- R2 lens rotation: DECIDABLE only at >= --min-multiround merged multi-round
  PRs with round_lenses; later-round catches are attributed core (lens in
  round 1 mix) vs rotated.
- R3 off-vocabulary fixture labels are excluded from keep/cut buckets and
  reported as a NOTE, never crash the audit.
- R4 terminal outcome lines (ceiling-split/abandoned/descoped) are counted
  and reported as a NOTE (sizing-retro obligation) but are not decidable
  by themselves.
- R5 loud failure (exit 2) on a missing log or a malformed line, with the
  line number.
- R6 catch compliance (0.31.1): a catch without a non-negative integer
  `round` or a non-empty string `lens` is unattributable - it is counted in
  `skipped`, never as core or rotated, reported as a NOTE with its PR
  number, and scanned on every entry (including entries with no
  `round_lenses` key). The NOTE alone does not change the exit code.
- R7 seat pairs and phase lenses (0.33.0): a round-1 seat `a+b` seats both
  lens ids in the pinned core, so a later-round catch attributed to either
  id scores core; catches from phase lenses (`fixture-review`,
  `final-review`, `gap-sweep`, `invariant-audit`) are neither core nor
  rotated and are reported in their own `phase=` bucket.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import loop_log_audit  # noqa: E402


def merged(issue: int, *, fixture: str = "compact", catch: int = 0, rounds: int = 1,
           lenses: list[list[str]] | None = None, catches: list[dict] | None = None) -> dict:
    line = {"issue": issue, "pr": issue + 100, "date": "2026-07-23", "fixture": fixture,
            "rounds": rounds, "gate_net_catch": catch,
            "verdicts": {"confirmed": catch, "plausible": 0, "refuted": 0},
            "residual_deferred": 0, "premerge_skip_blocks": 0}
    if lenses is not None:
        line["round_lenses"] = lenses
    if catches is not None:
        line["catches"] = catches
    return line


def terminal(issue: int, outcome: str, rounds: int = 5) -> dict:
    return {"issue": issue, "pr": issue + 100, "date": "2026-07-23", "fixture": "expanded",
            "rounds": rounds, "outcome": outcome}


def write_log(tmp_path: Path, lines: list) -> Path:
    path = tmp_path / "review-loop-log.jsonl"
    path.write_text("".join(json.dumps(line) + "\n" for line in lines), encoding="utf-8")
    return path


def run(path: Path, *argv: str) -> int:
    return loop_log_audit.main(["--log", str(path), *argv])


# --- R1 keep/cut ------------------------------------------------------------


def test_zero_catch_at_threshold_is_decidable(tmp_path, capsys):
    log = write_log(tmp_path, [merged(i) for i in range(8)])
    assert run(log) == 2
    assert "DECIDABLE keep-cut" in capsys.readouterr().out


def test_below_sample_not_decidable(tmp_path, capsys):
    log = write_log(tmp_path, [merged(i) for i in range(7)])
    assert run(log) == 0
    assert "DECIDABLE" not in capsys.readouterr().out


def test_any_catch_in_sample_not_decidable(tmp_path):
    log = write_log(tmp_path, [merged(i) for i in range(7)] + [merged(7, catch=2)])
    assert run(log) == 0


def test_min_sample_override(tmp_path):
    log = write_log(tmp_path, [merged(i) for i in range(3)])
    assert run(log, "--min-sample", "3") == 2


def test_levels_bucketed_separately(tmp_path, capsys):
    lines = [merged(i, fixture="compact") for i in range(8)] + \
            [merged(i + 10, fixture="high", catch=3) for i in range(8)]
    assert run(write_log(tmp_path, lines)) == 2
    out = capsys.readouterr().out
    assert "DECIDABLE keep-cut: fixture compact" in out
    assert "DECIDABLE keep-cut: fixture high" not in out


# --- R2 lens rotation -------------------------------------------------------


def rotation_entry(issue: int) -> dict:
    return merged(issue, catch=2, rounds=3,
                  lenses=[["correctness", "integration"], ["correctness"], ["security"]],
                  catches=[{"round": 1, "lens": "correctness", "class": "c", "severity": "minor"},
                           {"round": 2, "lens": "correctness", "class": "c", "severity": "minor"},
                           {"round": 3, "lens": "security", "class": "c", "severity": "minor"}])


def test_rotation_decidable_at_threshold_with_attribution(tmp_path, capsys):
    log = write_log(tmp_path, [rotation_entry(i) for i in range(8)])
    assert run(log) == 2
    out = capsys.readouterr().out
    # per entry: round-1 catch ignored, one core (correctness) + one rotated (security)
    assert "core=8 rotated=8 phase=0 skipped=0" in out
    assert "DECIDABLE lens-rotation" in out
    assert "non-compliant catches" not in out


def test_rotation_below_threshold_informational(tmp_path, capsys):
    log = write_log(tmp_path, [rotation_entry(i) for i in range(3)] + [merged(50, catch=1)])
    assert run(log) == 0
    assert "rotation attribution: 3 multi-round" in capsys.readouterr().out


# --- R3 off-vocabulary labels ----------------------------------------------


def test_off_vocab_labels_noted_and_excluded(tmp_path, capsys):
    lines = [merged(i, fixture="standard") for i in range(9)] + [merged(20, fixture="light")]
    assert run(write_log(tmp_path, lines)) == 0  # excluded, so no bucket reaches the threshold
    out = capsys.readouterr().out
    assert "off-vocabulary" in out and "standard(9)" in out and "light(1)" in out


# --- R4 terminal outcomes ---------------------------------------------------


def test_terminal_outcomes_noted_not_decidable(tmp_path, capsys):
    lines = [terminal(291, "ceiling-split"), terminal(292, "abandoned"), merged(1, catch=1)]
    assert run(write_log(tmp_path, lines)) == 0
    out = capsys.readouterr().out
    assert "terminal outcomes: abandoned=1, ceiling-split=1" in out
    assert "sizing-retro" in out


# --- R5 loud failures -------------------------------------------------------


def test_missing_log_fails(tmp_path):
    assert run(tmp_path / "absent.jsonl") == 2


def test_malformed_line_fails_with_lineno(tmp_path, capsys):
    path = tmp_path / "review-loop-log.jsonl"
    path.write_text(json.dumps(merged(1)) + "\n{bad json\n", encoding="utf-8")
    assert run(path) == 2
    assert ":2: invalid JSON" in capsys.readouterr().err


# --- R6 catch compliance ----------------------------------------------------


def test_lens_less_later_round_catch_is_skipped_not_rotated(tmp_path, capsys):
    """A round-2 catch with no `lens` used to score as rotated (None is not in
    the core set), inflating the rotation case with unattributable catches."""
    def entry(issue: int) -> dict:
        return merged(issue, catch=2, rounds=2,
                      lenses=[["correctness"], ["security"]],
                      catches=[{"round": 2, "lens": "correctness", "class": "c", "severity": "minor"},
                               {"round": 2, "class": "c", "severity": "minor"}])
    assert run(write_log(tmp_path, [entry(i) for i in range(8)])) == 2
    out = capsys.readouterr().out
    assert "core=8 rotated=0 phase=0 skipped=8" in out
    assert "NOTE non-compliant catches skipped: 8 in 8 entry(ies)" in out


def test_round_less_catch_is_counted_not_silently_defaulted(tmp_path, capsys):
    """A catch with no `round` used to default to round 1 and vanish."""
    line = merged(40, catch=1, rounds=3, lenses=[["correctness"], ["security"]],
                  catches=[{"lens": "security", "class": "c", "severity": "major"}])
    assert run(write_log(tmp_path, [line])) == 0
    out = capsys.readouterr().out
    assert "NOTE non-compliant catches skipped: 1 in 1 entry(ies) (pr 140)" in out
    assert "core=0 rotated=0 phase=0 skipped=1" in out


def test_entry_without_round_lenses_is_still_scanned(tmp_path, capsys):
    """The attribution block never sees this entry; the compliance scan must."""
    line = merged(70, catch=2, rounds=4,
                  catches=[{"round": 1, "class": "exception-safety", "severity": "major"},
                           {"round": 3, "class": "no-operator-entry-point", "severity": "critical"}])
    assert "round_lenses" not in line
    assert run(write_log(tmp_path, [line])) == 0  # a NOTE alone is not decidable
    out = capsys.readouterr().out
    assert "NOTE non-compliant catches skipped: 2 in 1 entry(ies) (pr 170)" in out
    assert "rotation attribution" not in out


def test_non_compliant_shapes_all_counted(tmp_path, capsys):
    line = merged(80, catch=5, rounds=2, lenses=[["correctness"], ["security"]],
                  catches=[{"round": 2, "lens": "security", "class": "c"},   # compliant
                           {"round": "2", "lens": "security", "class": "c"},  # string round
                           {"round": -1, "lens": "security", "class": "c"},   # negative round
                           {"round": True, "lens": "security", "class": "c"}, # bool round
                           {"round": 2, "lens": "", "class": "c"},            # empty lens
                           "round2-p1-legacy-string"])                        # not an object
    assert run(write_log(tmp_path, [line])) == 0
    out = capsys.readouterr().out
    assert "NOTE non-compliant catches skipped: 5 in 1 entry(ies) (pr 180)" in out
    assert "core=0 rotated=1 phase=0 skipped=5" in out


def test_round_zero_fixture_review_catch_is_compliant(tmp_path, capsys):
    line = merged(90, catch=1, rounds=2, lenses=[["correctness"], ["security"]],
                  catches=[{"round": 0, "lens": "fixture-review", "class": "c", "severity": "P2"}])
    assert run(write_log(tmp_path, [line])) == 0
    out = capsys.readouterr().out
    assert "non-compliant catches" not in out
    assert "core=0 rotated=0 phase=0 skipped=0" in out


# --- R7 seat pairs and phase lenses ------------------------------------------


def test_paired_seat_seats_both_lenses_in_core(tmp_path, capsys):
    line = merged(95, catch=3, rounds=2,
                  lenses=[["correctness", "test-evidence+spec-compliance"], ["test-evidence+spec-compliance"]],
                  catches=[{"round": 2, "lens": "spec-compliance", "class": "c", "severity": "minor"},
                           {"round": 2, "lens": "test-evidence", "class": "c", "severity": "minor"},
                           {"round": 2, "lens": "integration", "class": "c", "severity": "minor"}])
    assert run(write_log(tmp_path, [line])) == 0
    assert "core=2 rotated=1 phase=0 skipped=0" in capsys.readouterr().out


def test_phase_lens_catches_are_neither_core_nor_rotated(tmp_path, capsys):
    line = merged(96, catch=3, rounds=2, lenses=[["correctness"], ["correctness"]],
                  catches=[{"round": 2, "lens": "final-review", "class": "c", "severity": "major"},
                           {"round": 3, "lens": "gap-sweep", "class": "c", "severity": "major"},
                           {"round": 2, "lens": "correctness", "class": "c", "severity": "minor"}])
    assert run(write_log(tmp_path, [line])) == 0
    assert "core=1 rotated=0 phase=2 skipped=0" in capsys.readouterr().out
