"""Requirement-driven tests for the evidence-hygiene linter.

Requirements under test (phase-flow Phase 4 spawn precondition + Phase 8
evidence checklist, version 0.24.0):
- R1 placeholder/marker scan runs only on orchestrator-authored --file
  targets; reviewer reports in the evidence dir are exempt; code generics
  and autolinks are not flagged.
- R2 current/frozen-head SHA claims must prefix-match actual HEAD;
  historical anchors (`Last clean reviewed SHA`) are exempt.
- R3 "Round K pending" claims are stale once the gate state recorded round
  K; future rounds pass; no state file -> check skipped, others still run.
- R4 exit codes: 0 clean, 2 findings; loud failure (2) on nothing to check,
  missing --file target, or unresolvable HEAD.
- R5 gate-lock (0.28.0): a locked .review-gate.json fails the check even when
  every scanned file is clean - the out-of-band bypass (corrective action run
  before the gate transition) is caught at the next spawn/post point.
- R6 loop-log entry (0.28.0): --loop-log-entry validates a pending
  review-loop-log line: canonical single-token fixture vocabulary (composites
  and ad-hoc labels rejected), outcome vocabulary, date format, required keys;
  merged lines need gate_net_catch/verdicts, terminal outcomes are exempt;
  works standalone without --file.
- R7 catch schema (0.31.1): on a merged line every `catches[i]` must carry a
  non-negative integer `round` (`0` = fixture review, bool rejected) and a
  non-empty string `lens`; each violation is one finding naming `catches[i]`.
- R8 lens vocabulary and seat caps (0.33.0): `catches[i].lens` is exactly one
  canonical lens id - a seat lens or a phase lens - never an `a+b` pair; when
  `round_lenses` is present each seat is a canonical id or `a+b` pair, no lens
  sits in two seats of one round, round 1 is within the fixture level's cap
  (none 1, compact 2, expanded 3, high/broad-expanded 4), later rounds within
  3, and the list length equals `rounds`.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import evidence_check  # noqa: E402
import review_gate  # noqa: E402

HEAD = "a1b2c3d4e5f60718293a4b5c6d7e8f9012345678"


def run(root: Path, *argv: str) -> int:
    return evidence_check.main(["--root", str(root), "--head", HEAD, *argv])


def review_dir(root: Path) -> Path:
    path = root / ".workplans/pr-7/review"
    path.mkdir(parents=True, exist_ok=True)
    return path


def open_gate_with_rounds(root: Path, n: int) -> None:
    assert review_gate.main(["--root", str(root), "open", "--pr", "7"]) == 0
    for i in range(n):
        assert review_gate.main([
            "--root", str(root), "record-round", "--sha", f"sha{i}", "--lenses", "correctness",
            "--not-clean", "--verified", "1", "--highest", "minor", "--classes", f"c{i}",
        ]) == 0


def write(path: Path, text: str) -> Path:
    path.write_text(text, encoding="utf-8")
    return path


# --- happy path -------------------------------------------------------------


def test_clean_bundle_passes(tmp_path):
    open_gate_with_rounds(tmp_path, 2)
    write(review_dir(tmp_path) / "r1-correctness.md", "Focused suite green; `uv run pytest` all pass.\n")
    body = write(tmp_path / "pr-body.md",
                 f"Current head: {HEAD[:12]} - full run green.\nRound 3 pending on new head.\n")
    assert run(tmp_path, "--file", str(body)) == 0


def test_prefix_and_full_sha_claims_pass(tmp_path):
    body = write(tmp_path / "pr-body.md",
                 f"Frozen SHA: {HEAD}\nCurrent head sha {HEAD[:7]} verified.\n")
    assert run(tmp_path, "--file", str(body)) == 0


# --- R1 placeholder / marker scan --------------------------------------------


def test_unreplaced_template_token_in_authored_file_fails(tmp_path, capsys):
    body = write(tmp_path / "manifest.md", "Ruff: `ruff check <path>` on <n> files\n")
    assert run(tmp_path, "--file", str(body)) == 2
    out = capsys.readouterr().out
    assert "[placeholder]" in out and "<path>" in out and "manifest.md:1" in out


def test_todo_marker_in_authored_file_fails(tmp_path):
    body = write(tmp_path / "pr-body.md", "Evidence: TBD after CI\n")
    assert run(tmp_path, "--file", str(body)) == 2


def test_reviewer_report_in_evidence_dir_exempt_from_placeholder_scan(tmp_path):
    open_gate_with_rounds(tmp_path, 1)
    write(review_dir(tmp_path) / "r1-report.md",
          "The diff still has a TODO at line 42 and uses Vec<i32> unsafely.\n")
    assert run(tmp_path) == 0


def test_code_generics_and_autolinks_not_flagged(tmp_path):
    body = write(tmp_path / "pr-body.md",
                 "Uses Vec<i32> internally; see <https://github.com/o/r/pull/7> and <mail@example.com>.\n")
    assert run(tmp_path, "--file", str(body)) == 0


# --- R2 head-sha claims -------------------------------------------------------


def test_stale_current_head_claim_fails(tmp_path, capsys):
    stale = "b" * 12
    body = write(tmp_path / "pr-body.md", f"Current head: {stale} focused results attached.\n")
    assert run(tmp_path, "--file", str(body)) == 2
    assert "[head-sha]" in capsys.readouterr().out


def test_historical_anchor_sha_exempt(tmp_path):
    body = write(tmp_path / "pr-body.md", f"Last clean reviewed SHA: {'c' * 40}\n")
    assert run(tmp_path, "--file", str(body)) == 0


# --- R3 round-status vs recorded rounds ----------------------------------------


def test_recorded_round_claimed_pending_fails(tmp_path, capsys):
    open_gate_with_rounds(tmp_path, 2)
    body = write(tmp_path / "pr-body.md", "Round 2 pending, results to follow.\n")
    assert run(tmp_path, "--file", str(body)) == 2
    assert "[round-status]" in capsys.readouterr().out


def test_future_round_pending_passes(tmp_path):
    open_gate_with_rounds(tmp_path, 2)
    body = write(tmp_path / "pr-body.md", "Round 3 pending on the new head.\n")
    assert run(tmp_path, "--file", str(body)) == 0


def test_correction_ledger_line_with_status_like_reason_passes(tmp_path):
    # The CORRECTION line keeps free text ahead of its `round N` field, so a reason that
    # starts with a round-status trigger word cannot land inside the round-status window.
    open_gate_with_rounds(tmp_path, 2)
    assert review_gate.main([
        "--root", str(tmp_path), "correct-round", "--round", "2", "--sha", "sha2-fixed",
        "--reason", "pending re-review: reviewers read the pre-fix head, not yet the fixed one",
    ]) == 0
    text = (review_dir(tmp_path) / review_gate.LEDGER_NAME).read_text(encoding="utf-8")
    assert "CORRECTION |" in text and "round 2" in text
    body = write(tmp_path / "pr-body.md", "Round 3 pending on the corrected head.\n")
    assert run(tmp_path, "--file", str(body)) == 0


def test_no_state_file_skips_round_check_but_runs_others(tmp_path):
    body = write(tmp_path / "pr-body.md", "Round 1 pending.\nManifest: <command>\n")
    assert run(tmp_path, "--file", str(body)) == 2  # placeholder still caught
    clean = write(tmp_path / "clean.md", "Round 1 pending.\n")
    assert run(tmp_path, "--file", str(clean)) == 0  # round check skipped


# --- R4 loud failures ----------------------------------------------------------


def test_nothing_to_check_fails_loud(tmp_path):
    assert run(tmp_path) == 2


def test_missing_file_target_fails(tmp_path):
    assert run(tmp_path, "--file", str(tmp_path / "absent.md")) == 2


def test_unresolvable_head_fails(tmp_path):
    body = write(tmp_path / "pr-body.md", "fine\n")
    assert evidence_check.main(["--root", str(tmp_path), "--file", str(body)]) == 2


# --- R5 gate-lock -------------------------------------------------------------


def lock_gate(root: Path) -> None:
    """Three not-clean rounds; the third locks the gate (its exit code 2 is the lock signal)."""
    open_gate_with_rounds(root, 2)
    assert review_gate.main([
        "--root", str(root), "record-round", "--sha", "sha2", "--lenses", "correctness", "--not-clean",
        "--verified", "1", "--highest", "minor", "--classes", "c2",
    ]) == 2


def test_locked_gate_fails_even_with_clean_files(tmp_path, capsys):
    lock_gate(tmp_path)
    body = write(tmp_path / "pr-body.md", "All evidence current.\n")
    assert run(tmp_path, "--file", str(body)) == 2
    assert "[gate-lock]" in capsys.readouterr().out


def test_unlocked_gate_after_retro_passes(tmp_path):
    lock_gate(tmp_path)
    retro = write(tmp_path / "retro.md", "Review Failure Retro: evidence\n")
    assert review_gate.main(["--root", str(tmp_path), "record-retro",
                             "--path", str(retro), "--shape", "breadth"]) == 0
    body = write(tmp_path / "pr-body.md", "All evidence current.\n")
    assert run(tmp_path, "--file", str(body)) == 0


# --- R6 loop-log entry ---------------------------------------------------------


MERGED_LINE = {
    "issue": 88, "pr": 128, "date": "2026-07-23", "fixture": "expanded", "rounds": 3,
    "gate_net_catch": 2, "verdicts": {"confirmed": 2, "plausible": 0, "refuted": 1},
    "residual_deferred": 0, "premerge_skip_blocks": 0,
}


def entry(tmp_path: Path, **overrides) -> Path:
    import json
    data = {**MERGED_LINE, **overrides}
    for key, value in list(data.items()):
        if value is None:
            del data[key]
    return write(tmp_path / "pending-line.json", json.dumps(data) + "\n")


def test_valid_merged_line_passes_standalone(tmp_path):
    assert run(tmp_path, "--loop-log-entry", str(entry(tmp_path))) == 0


def test_off_vocabulary_fixture_labels_fail(tmp_path, capsys):
    assert run(tmp_path, "--loop-log-entry", str(entry(tmp_path, fixture="standard"))) == 2
    assert "off-vocabulary" in capsys.readouterr().out
    assert run(tmp_path, "--loop-log-entry", str(entry(tmp_path, fixture="expanded/high"))) == 2


def test_terminal_outcome_exempt_from_merged_keys(tmp_path):
    line = entry(tmp_path, outcome="ceiling-split", gate_net_catch=None, verdicts=None,
                 residual_deferred=None, premerge_skip_blocks=None)
    assert run(tmp_path, "--loop-log-entry", str(line)) == 0


def test_merged_line_missing_net_catch_fails(tmp_path):
    assert run(tmp_path, "--loop-log-entry", str(entry(tmp_path, gate_net_catch=None))) == 2


def test_invalid_outcome_date_rounds_and_missing_key_fail(tmp_path):
    assert run(tmp_path, "--loop-log-entry", str(entry(tmp_path, outcome="split"))) == 2
    assert run(tmp_path, "--loop-log-entry", str(entry(tmp_path, date="07/23"))) == 2
    assert run(tmp_path, "--loop-log-entry", str(entry(tmp_path, rounds=-1))) == 2
    assert run(tmp_path, "--loop-log-entry", str(entry(tmp_path, fixture=None))) == 2


def test_malformed_or_missing_entry_file_fails(tmp_path):
    bad = write(tmp_path / "pending-line.json", "{not json\n")
    assert run(tmp_path, "--loop-log-entry", str(bad)) == 2
    assert run(tmp_path, "--loop-log-entry", str(tmp_path / "absent.json")) == 2


# --- R7 catch schema ------------------------------------------------------------


GOOD_CATCH = {"round": 2, "lens": "correctness", "class": "spec-drift", "severity": "major"}


def catch_findings(tmp_path, capsys, catch: object) -> list[str]:
    """Run one entry whose catches[1] is `catch`; return the [loop-log] findings."""
    path = entry(tmp_path, catches=[GOOD_CATCH, catch])
    assert run(tmp_path, "--loop-log-entry", str(path)) == 2
    return [line for line in capsys.readouterr().out.splitlines() if "[loop-log]" in line]


def assert_single_catch_finding(tmp_path, capsys, catch: object, expected: str) -> None:
    found = catch_findings(tmp_path, capsys, catch)
    assert len(found) == 1, found
    assert "catches[1]" in found[0], found[0]
    assert expected in found[0], found[0]


def test_compliant_catches_pass(tmp_path):
    catches = [{"round": 0, "lens": "fixture-review", "class": "test-semantics", "severity": "P2"},
               GOOD_CATCH]
    assert run(tmp_path, "--loop-log-entry", str(entry(tmp_path, catches=catches))) == 0


def test_catch_missing_round_fails(tmp_path, capsys):
    assert_single_catch_finding(tmp_path, capsys,
                                {"lens": "correctness", "class": "c", "severity": "minor"},
                                "missing `round`")


def test_catch_missing_lens_fails(tmp_path, capsys):
    assert_single_catch_finding(tmp_path, capsys,
                                {"round": 2, "class": "c", "severity": "minor"},
                                "missing `lens`")


def test_catch_string_round_fails(tmp_path, capsys):
    assert_single_catch_finding(tmp_path, capsys,
                                {"round": "2", "lens": "correctness", "class": "c"},
                                "round must be a non-negative integer")


def test_catch_negative_round_fails(tmp_path, capsys):
    assert_single_catch_finding(tmp_path, capsys,
                                {"round": -1, "lens": "correctness", "class": "c"},
                                "round must be a non-negative integer")


def test_catch_bool_round_fails(tmp_path, capsys):
    assert_single_catch_finding(tmp_path, capsys,
                                {"round": True, "lens": "correctness", "class": "c"},
                                "round must be a non-negative integer")


def test_catch_empty_lens_fails(tmp_path, capsys):
    assert_single_catch_finding(tmp_path, capsys,
                                {"round": 2, "lens": "", "class": "c"},
                                "lens must be a non-empty string")


def test_non_mapping_catch_fails(tmp_path, capsys):
    assert_single_catch_finding(tmp_path, capsys, "round3-p0-legacy-string",
                                "must be an object")


def test_catches_must_be_a_list(tmp_path, capsys):
    path = entry(tmp_path, catches={"round": 2, "lens": "correctness"})
    assert run(tmp_path, "--loop-log-entry", str(path)) == 2
    assert "catches must be a list" in capsys.readouterr().out


def test_catch_lens_off_vocabulary_fails(tmp_path, capsys):
    assert_single_catch_finding(tmp_path, capsys,
                                {"round": 2, "lens": "security", "class": "c"},
                                "off-vocabulary")


def test_catch_lens_pair_is_rejected(tmp_path, capsys):
    assert_single_catch_finding(tmp_path, capsys,
                                {"round": 2, "lens": "test-evidence+spec-compliance", "class": "c"},
                                "never to an `a+b` seat pair")


def test_catch_phase_lenses_pass(tmp_path):
    catches = [{"round": 0, "lens": "fixture-review", "class": "c", "severity": "P2"},
               {"round": 2, "lens": "final-review", "class": "c", "severity": "P1"},
               {"round": 2, "lens": "gap-sweep", "class": "c", "severity": "P1"},
               {"round": 1, "lens": "invariant-audit", "class": "c", "severity": "P1"}]
    assert run(tmp_path, "--loop-log-entry", str(entry(tmp_path, catches=catches))) == 0


# --- R8 round_lenses seat caps ------------------------------------------------


HIGH_SEATS = ["correctness", "invariant-state", "test-evidence+spec-compliance", "security-perf+integration"]


def lens_findings(tmp_path, capsys, **overrides) -> list[str]:
    path = entry(tmp_path, **overrides)
    rc = run(tmp_path, "--loop-log-entry", str(path))
    found = [line for line in capsys.readouterr().out.splitlines() if "round_lenses" in line]
    assert (rc == 2) == bool(found), (rc, found)
    return found


def test_valid_seat_plan_passes(tmp_path, capsys):
    assert lens_findings(tmp_path, capsys, fixture="high", rounds=3,
                         round_lenses=[HIGH_SEATS, ["correctness", "invariant-state"], ["correctness"]]) == []


def test_round1_over_fixture_cap_fails(tmp_path, capsys):
    five = HIGH_SEATS[:3] + ["security-perf", "integration"]
    found = lens_findings(tmp_path, capsys, fixture="high", rounds=1, round_lenses=[five])
    assert len(found) == 1 and "ran 5 seats; the round-1 cap for `high` is 4" in found[0]
    found = lens_findings(tmp_path, capsys, fixture="expanded", rounds=1, round_lenses=[HIGH_SEATS])
    assert len(found) == 1 and "cap for `expanded` is 3" in found[0]


def test_review_prefix_and_long_alias_accepted_in_round_lenses(tmp_path, capsys):
    assert lens_findings(tmp_path, capsys, fixture="high", rounds=1, round_lenses=[[
        "review-correctness", "review-invariant-state", "review-test-evidence+review-spec-compliance",
        "security-performance+integration"]]) == []
    found = lens_findings(tmp_path, capsys, fixture="high", rounds=1,
                          round_lenses=[["review-correctness", "review-correctness"]])
    assert len(found) == 1 and "more than one seat" in found[0]


def test_none_level_allows_one_seat(tmp_path, capsys):
    assert lens_findings(tmp_path, capsys, fixture="none", rounds=1, round_lenses=[["correctness+test-evidence"]]) == []
    found = lens_findings(tmp_path, capsys, fixture="none", rounds=1, round_lenses=[["correctness", "integration"]])
    assert len(found) == 1 and "cap for `none` is 1" in found[0]


def test_later_round_over_three_fails(tmp_path, capsys):
    found = lens_findings(tmp_path, capsys, fixture="high", rounds=2, round_lenses=[HIGH_SEATS, HIGH_SEATS])
    assert len(found) == 1 and "[1] (round 2) ran 4 seats; post-fix rounds are capped at 3" in found[0]


def test_seat_off_vocabulary_and_duplicate_lens_fail(tmp_path, capsys):
    found = lens_findings(tmp_path, capsys, fixture="expanded", rounds=1,
                          round_lenses=[["correctness", "security", "test-evidence+correctness"]])
    assert any("off-vocabulary lens id `security`" in f for f in found)
    assert any("lens `correctness` sits in more than one seat" in f for f in found)


def test_round_lenses_length_must_match_rounds(tmp_path, capsys):
    found = lens_findings(tmp_path, capsys, fixture="high", rounds=3, round_lenses=[HIGH_SEATS])
    assert len(found) == 1 and "lists 1 round(s) but `rounds` is 3" in found[0]


def test_round_lenses_shape_errors(tmp_path, capsys):
    assert lens_findings(tmp_path, capsys, rounds=1, round_lenses="correctness")[0].endswith(
        "must be a list of per-round seat lists")
    found = lens_findings(tmp_path, capsys, rounds=1, round_lenses=["correctness"])
    assert "must be a list of non-empty seat strings" in found[0]


def test_round_lenses_checked_on_terminal_lines_too(tmp_path, capsys):
    found = lens_findings(tmp_path, capsys, outcome="ceiling-split", gate_net_catch=None, verdicts=None,
                          residual_deferred=None, premerge_skip_blocks=None, fixture="compact", rounds=5,
                          round_lenses=[HIGH_SEATS] + [["correctness"]] * 4)
    assert len(found) == 1 and "cap for `compact` is 2" in found[0]


def test_terminal_outcome_catches_not_schema_checked(tmp_path):
    """Terminal lines are exempt from the merged-line keys and from this schema."""
    line = entry(tmp_path, outcome="abandoned", gate_net_catch=None, verdicts=None,
                 residual_deferred=None, premerge_skip_blocks=None,
                 catches=[{"phase": "cross-review", "class": "c"}])
    assert run(tmp_path, "--loop-log-entry", str(line)) == 0
