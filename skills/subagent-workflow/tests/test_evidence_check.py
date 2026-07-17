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
