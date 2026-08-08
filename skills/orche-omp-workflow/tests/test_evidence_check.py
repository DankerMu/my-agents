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
            "--root", str(root), "record-round", "--sha", f"sha{i}", "--not-clean",
            "--verified", "1", "--highest", "minor", "--classes", f"c{i}",
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
        "--root", str(root), "record-round", "--sha", "sha2", "--not-clean",
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
