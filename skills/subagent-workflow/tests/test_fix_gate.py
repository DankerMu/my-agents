"""Requirement: at most two fix passes per PR, enforced mechanically.

Round 1 not clean -> fix pass 1; round 2 not clean -> fix pass 2; round 3 not
clean -> the gate locks and the review-gate hook denies implementer/reviewer
spawns until a user decision is recorded.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

SKILL_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = SKILL_DIR.parents[1]
sys.path.insert(0, str(SKILL_DIR / "scripts"))

import fix_gate  # noqa: E402

HOOK_SCRIPT = REPO_ROOT / "hooks" / "review-gate" / "scripts" / "review-gate.sh"


def run(root: Path, *argv: str) -> int:
    return fix_gate.main(["--root", str(root), *argv])


def state(root: Path) -> dict:
    return json.loads((root / ".review-gate.json").read_text())


def hook_exit(root: Path, subagent: str) -> int:
    payload = json.dumps({"tool_name": "Task", "tool_input": {"subagent_type": subagent}})
    proc = subprocess.run(
        ["bash", str(HOOK_SCRIPT)],
        input=payload,
        capture_output=True,
        text=True,
        env={**os.environ, "CLAUDE_PROJECT_DIR": str(root)},
    )
    return proc.returncode


def test_open_creates_unlocked_state(tmp_path: Path) -> None:
    assert run(tmp_path, "open", "--pr", "7") == 0
    s = state(tmp_path)
    assert s["pr"] == 7 and s["maxFixPasses"] == 2 and s["locked"] is False and s["rounds"] == []


def test_open_is_idempotent_for_same_pr_and_refuses_other_pr(tmp_path: Path) -> None:
    run(tmp_path, "open", "--pr", "7")
    assert run(tmp_path, "open", "--pr", "7") == 0
    with pytest.raises(SystemExit):
        run(tmp_path, "open", "--pr", "8")


def test_record_round_requires_open(tmp_path: Path) -> None:
    with pytest.raises(SystemExit):
        run(tmp_path, "record-round", "--sha", "a", "--not-clean")


def test_two_fix_passes_allowed_third_not_clean_round_locks(tmp_path: Path, capsys) -> None:
    run(tmp_path, "open", "--pr", "7")
    assert run(tmp_path, "record-round", "--sha", "a1", "--not-clean") == 0  # -> fix pass 1
    assert state(tmp_path)["locked"] is False
    assert run(tmp_path, "record-round", "--sha", "a2", "--not-clean") == 0  # -> fix pass 2
    assert state(tmp_path)["locked"] is False
    assert run(tmp_path, "record-round", "--sha", "a3", "--not-clean") == 2  # would be pass 3
    s = state(tmp_path)
    assert s["locked"] is True
    assert "2/2 fix passes" in s["lockReason"]
    assert "LOCKED" in capsys.readouterr().err


def test_clean_round_never_locks(tmp_path: Path) -> None:
    run(tmp_path, "open", "--pr", "7")
    run(tmp_path, "record-round", "--sha", "a1", "--not-clean")
    run(tmp_path, "record-round", "--sha", "a2", "--not-clean")
    assert run(tmp_path, "record-round", "--sha", "a3", "--clean") == 0
    assert state(tmp_path)["locked"] is False


def test_locked_gate_refuses_further_rounds_until_user_extends(tmp_path: Path) -> None:
    run(tmp_path, "open", "--pr", "7")
    for sha in ("a1", "a2", "a3"):
        run(tmp_path, "record-round", "--sha", sha, "--not-clean")
    assert run(tmp_path, "record-round", "--sha", "a4", "--not-clean") == 2
    assert len(state(tmp_path)["rounds"]) == 3
    assert run(tmp_path, "status") == 2
    assert run(tmp_path, "extend", "--user-approved", "split is worse; one more pass") == 0
    s = state(tmp_path)
    assert s["locked"] is False and s["maxFixPasses"] == 3
    assert s["approvals"][0]["decision"].startswith("split is worse")
    assert run(tmp_path, "record-round", "--sha", "a4", "--not-clean") == 2  # pass 3 used, round 4 dirty


def test_close_removes_state(tmp_path: Path) -> None:
    run(tmp_path, "open", "--pr", "7")
    assert run(tmp_path, "close") == 0
    assert not (tmp_path / ".review-gate.json").exists()
    assert run(tmp_path, "close") == 0


@pytest.mark.skipif(not HOOK_SCRIPT.is_file(), reason="review-gate hook not present")
def test_hook_denies_implementer_and_reviewer_only_while_locked(tmp_path: Path) -> None:
    assert hook_exit(tmp_path, "implementer") == 0  # no state file: no-op
    run(tmp_path, "open", "--pr", "7")
    run(tmp_path, "record-round", "--sha", "a1", "--not-clean")
    assert hook_exit(tmp_path, "implementer") == 0
    for sha in ("a2", "a3"):
        run(tmp_path, "record-round", "--sha", sha, "--not-clean")
    assert hook_exit(tmp_path, "implementer") == 2
    assert hook_exit(tmp_path, "reviewer") == 2
    assert hook_exit(tmp_path, "verifier") == 0
    run(tmp_path, "extend", "--user-approved", "one more pass")
    assert hook_exit(tmp_path, "implementer") == 0
