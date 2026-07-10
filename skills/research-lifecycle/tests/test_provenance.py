from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

from _loader import load_script_module

provenance = load_script_module("provenance")


def _make_study(tmp_path: Path, protocol: str = "# Protocol\nDo X.\n") -> Path:
    study = tmp_path / "studies" / "s1"
    study.mkdir(parents=True)
    (study / "protocol.md").write_text(protocol, encoding="utf8")
    return study


def _freeze(study: Path) -> int:
    return provenance.main(["freeze", str(study), "--approver", "PI"])


def _run_ok(study: Path, run_id: str = "r1") -> int:
    return provenance.main(
        ["run", str(study), "--id", run_id, "--", sys.executable, "-c", "print('ok')"]
    )


def test_freeze_records_digest_and_approver(tmp_path):
    study = _make_study(tmp_path)
    assert _freeze(study) == 0
    lock = json.loads((study / "protocol.lock.json").read_text(encoding="utf8"))
    expected = hashlib.sha256((study / "protocol.md").read_bytes()).hexdigest()
    assert lock["protocol_sha256"] == expected
    assert lock["approver"] == "PI"


def test_freeze_requires_protocol_and_refuses_refreeze(tmp_path):
    empty = tmp_path / "empty-study"
    empty.mkdir()
    assert provenance.main(["freeze", str(empty), "--approver", "PI"]) == 1

    study = _make_study(tmp_path)
    assert _freeze(study) == 0
    assert _freeze(study) == 1


def test_run_requires_frozen_protocol(tmp_path):
    study = _make_study(tmp_path)
    assert _run_ok(study) == 1
    assert not (study / "runs").exists()


def test_run_records_command_logs_and_exit_code(tmp_path):
    study = _make_study(tmp_path)
    assert _freeze(study) == 0
    assert _run_ok(study) == 0

    run_dir = study / "runs" / "r1"
    record = json.loads((run_dir / "run.json").read_text(encoding="utf8"))
    assert record["exit_code"] == 0
    assert record["protocol_amended_at_run"] is False
    assert (run_dir / "command.txt").read_text(encoding="utf8").strip()
    assert "ok" in (run_dir / "logs" / "stdout.log").read_text(encoding="utf8")


def test_run_propagates_failing_exit_code(tmp_path):
    study = _make_study(tmp_path)
    assert _freeze(study) == 0
    code = provenance.main(
        ["run", str(study), "--id", "bad", "--", sys.executable, "-c", "raise SystemExit(3)"]
    )
    assert code == 3
    record = json.loads((study / "runs" / "bad" / "run.json").read_text(encoding="utf8"))
    assert record["exit_code"] == 3


def test_run_blocks_silent_protocol_drift_but_allows_amended(tmp_path):
    study = _make_study(tmp_path)
    assert _freeze(study) == 0
    (study / "protocol.md").write_text("# Protocol\nDo Y instead.\n", encoding="utf8")

    assert _run_ok(study, "drift") == 1
    assert not (study / "runs" / "drift").exists()

    amendments = study / "amendments"
    amendments.mkdir()
    (amendments / "0001-scope-change.md").write_text("Reason: scope change\n", encoding="utf8")
    assert _run_ok(study, "amended") == 0
    record = json.loads((study / "runs" / "amended" / "run.json").read_text(encoding="utf8"))
    assert record["protocol_amended_at_run"] is True


def test_index_and_verify_clean_study(tmp_path):
    study = _make_study(tmp_path)
    assert _freeze(study) == 0
    assert _run_ok(study) == 0
    output = study / "runs" / "r1" / "result.csv"
    output.write_text("a,b\n1,2\n", encoding="utf8")

    assert provenance.main(["index", str(study), "--run", "r1", str(output)]) == 0
    index = json.loads((study / "runs" / "r1" / "outputs.index.json").read_text(encoding="utf8"))
    assert len(index["outputs"]) == 1
    assert provenance.main(["verify", str(study)]) == 0


def test_verify_fails_on_silent_protocol_edit(tmp_path):
    study = _make_study(tmp_path)
    assert _freeze(study) == 0
    (study / "protocol.md").write_text("# Protocol\nrewritten\n", encoding="utf8")
    assert provenance.main(["verify", str(study)]) == 1

    amendments = study / "amendments"
    amendments.mkdir()
    (amendments / "0001-fix.md").write_text("Reason: fix\n", encoding="utf8")
    assert provenance.main(["verify", str(study)]) == 0


def test_verify_fails_on_changed_output_or_missing_run_record(tmp_path):
    study = _make_study(tmp_path)
    assert _freeze(study) == 0
    assert _run_ok(study) == 0
    output = study / "runs" / "r1" / "result.csv"
    output.write_text("a,b\n1,2\n", encoding="utf8")
    assert provenance.main(["index", str(study), "--run", "r1", str(output)]) == 0

    output.write_text("a,b\n9,9\n", encoding="utf8")
    assert provenance.main(["verify", str(study)]) == 1

    output.write_text("a,b\n1,2\n", encoding="utf8")
    (study / "runs" / "r1" / "run.json").unlink()
    assert provenance.main(["verify", str(study)]) == 1
