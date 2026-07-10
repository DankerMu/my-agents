#!/usr/bin/env python3
"""Mechanical provenance for research studies: freeze, run, index, verify.

Enforces the artifact-model invariants that must not rely on narration:
the frozen protocol cannot change silently, runs bind to the frozen digest,
and indexed evidence files cannot drift after the fact.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import shlex
import subprocess
import sys
from pathlib import Path

LOCK_NAME = "protocol.lock.json"
PROTOCOL_NAME = "protocol.md"
AMENDMENTS_DIR = "amendments"
RUNS_DIR = "runs"
OUTPUTS_INDEX = "outputs.index.json"
SCHEMA_VERSION = 1


def _utc_now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _git_identity(cwd: Path) -> dict:
    def _run(args: list[str]) -> str | None:
        try:
            result = subprocess.run(
                ["git", *args], cwd=cwd, capture_output=True, text=True, check=False
            )
        except OSError:
            return None
        if result.returncode != 0:
            return None
        return result.stdout.strip()

    commit = _run(["rev-parse", "HEAD"])
    if commit is None:
        return {"git_commit": None, "git_dirty": None}
    status = _run(["status", "--porcelain"])
    return {"git_commit": commit, "git_dirty": bool(status)}


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf8"))


def _write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf8")


def _study_paths(study_dir: str) -> tuple[Path, Path, Path]:
    study = Path(study_dir).expanduser().resolve()
    return study, study / PROTOCOL_NAME, study / LOCK_NAME


def _has_amendments(study: Path) -> bool:
    amendments = study / AMENDMENTS_DIR
    if not amendments.is_dir():
        return False
    return any(entry.is_file() and not entry.name.startswith(".") for entry in amendments.iterdir())


def cmd_freeze(args: argparse.Namespace) -> int:
    study, protocol, lock = _study_paths(args.study_dir)
    if not protocol.is_file():
        print(f"error: {protocol} not found; write the protocol before freezing", file=sys.stderr)
        return 1
    if lock.exists():
        print(
            f"error: {lock} already exists; a frozen protocol is immutable — "
            f"record changes under {AMENDMENTS_DIR}/ instead",
            file=sys.stderr,
        )
        return 1
    payload = {
        "schema": SCHEMA_VERSION,
        "protocol_path": PROTOCOL_NAME,
        "protocol_sha256": _sha256_file(protocol),
        "frozen_at": _utc_now(),
        "approver": args.approver,
        **_git_identity(study),
    }
    _write_json(lock, payload)
    print(f"frozen: {lock} (sha256 {payload['protocol_sha256'][:12]}…, approver {args.approver})")
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    study, protocol, lock = _study_paths(args.study_dir)
    if not lock.is_file():
        print(
            "error: protocol is not frozen; run `freeze` before executing study runs",
            file=sys.stderr,
        )
        return 1
    lock_data = _read_json(lock)
    current_digest = _sha256_file(protocol) if protocol.is_file() else None
    amended = current_digest != lock_data.get("protocol_sha256")
    if amended and not _has_amendments(study):
        print(
            "error: protocol.md differs from the frozen digest and no amendment is "
            f"recorded under {AMENDMENTS_DIR}/ — refusing to run",
            file=sys.stderr,
        )
        return 1

    run_id = args.id or _dt.datetime.now(_dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = study / RUNS_DIR / run_id
    if run_dir.exists():
        print(f"error: run directory already exists: {run_dir}", file=sys.stderr)
        return 1
    if not args.command:
        print("error: no command given; pass it after `--`", file=sys.stderr)
        return 1

    logs_dir = run_dir / "logs"
    logs_dir.mkdir(parents=True)
    (run_dir / "command.txt").write_text(shlex.join(args.command) + "\n", encoding="utf8")

    started_at = _utc_now()
    with (logs_dir / "stdout.log").open("wb") as out, (logs_dir / "stderr.log").open("wb") as err:
        completed = subprocess.run(args.command, stdout=out, stderr=err, check=False)
    payload = {
        "schema": SCHEMA_VERSION,
        "run_id": run_id,
        "command": args.command,
        "started_at": started_at,
        "ended_at": _utc_now(),
        "exit_code": completed.returncode,
        "protocol_sha256_at_freeze": lock_data.get("protocol_sha256"),
        "protocol_amended_at_run": amended,
        **_git_identity(study),
    }
    _write_json(run_dir / "run.json", payload)
    print(f"run {run_id}: exit {completed.returncode} (logs in {logs_dir})")
    return completed.returncode


def cmd_index(args: argparse.Namespace) -> int:
    study, _, _ = _study_paths(args.study_dir)
    run_dir = study / RUNS_DIR / args.run
    if not run_dir.is_dir():
        print(f"error: run directory not found: {run_dir}", file=sys.stderr)
        return 1
    files: list[Path] = []
    for raw in args.paths:
        path = Path(raw).expanduser().resolve()
        if path.is_dir():
            files.extend(sorted(p for p in path.rglob("*") if p.is_file()))
        elif path.is_file():
            files.append(path)
        else:
            print(f"error: output path not found: {path}", file=sys.stderr)
            return 1
    entries = [
        {
            "path": str(p.relative_to(study)) if p.is_relative_to(study) else str(p),
            "sha256": _sha256_file(p),
            "bytes": p.stat().st_size,
        }
        for p in files
    ]
    _write_json(run_dir / OUTPUTS_INDEX, {"schema": SCHEMA_VERSION, "outputs": entries})
    print(f"indexed {len(entries)} output file(s) -> {run_dir / OUTPUTS_INDEX}")
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    study, protocol, lock = _study_paths(args.study_dir)
    problems: list[str] = []
    notes: list[str] = []

    if not lock.is_file():
        problems.append(f"missing {LOCK_NAME}: protocol was never frozen")
    else:
        lock_data = _read_json(lock)
        if not protocol.is_file():
            problems.append(f"missing {PROTOCOL_NAME}: frozen protocol file was removed")
        elif _sha256_file(protocol) != lock_data.get("protocol_sha256"):
            if _has_amendments(study):
                notes.append("protocol amended after freeze (amendment trail present)")
            else:
                problems.append(
                    "frozen protocol was modified WITHOUT an amendment trail "
                    f"(no files under {AMENDMENTS_DIR}/)"
                )

    runs_root = study / RUNS_DIR
    run_dirs = sorted(p for p in runs_root.iterdir() if p.is_dir()) if runs_root.is_dir() else []
    for run_dir in run_dirs:
        label = f"{RUNS_DIR}/{run_dir.name}"
        for required in ("run.json", "command.txt"):
            if not (run_dir / required).is_file():
                problems.append(f"{label}: missing {required}")
        index_path = run_dir / OUTPUTS_INDEX
        if index_path.is_file():
            for entry in _read_json(index_path).get("outputs", []):
                target = Path(entry["path"])
                if not target.is_absolute():
                    target = study / target
                if not target.is_file():
                    problems.append(f"{label}: indexed output missing: {entry['path']}")
                elif _sha256_file(target) != entry.get("sha256"):
                    problems.append(f"{label}: indexed output changed after indexing: {entry['path']}")

    for note in notes:
        print(f"note: {note}")
    if problems:
        for problem in problems:
            print(f"FAIL: {problem}", file=sys.stderr)
        return 1
    print(f"verify OK: {len(run_dirs)} run(s), protocol digest intact")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="subcommand", required=True)

    freeze = sub.add_parser("freeze", help="freeze protocol.md into an immutable lock record")
    freeze.add_argument("study_dir")
    freeze.add_argument("--approver", required=True, help="named human approver of the protocol")
    freeze.set_defaults(func=cmd_freeze)

    run = sub.add_parser(
        "run",
        help="execute a study command under a recorded run directory",
        description="Execute a study command: provenance.py run <study-dir> [--id ID] -- <command…>",
    )
    run.add_argument("study_dir")
    run.add_argument("--id", help="run id (default: UTC timestamp)")
    run.set_defaults(func=cmd_run, command=[])

    index = sub.add_parser("index", help="checksum output files into outputs.index.json")
    index.add_argument("study_dir")
    index.add_argument("--run", required=True, help="run id to attach outputs to")
    index.add_argument("paths", nargs="+", help="output files or directories")
    index.set_defaults(func=cmd_index)

    verify = sub.add_parser("verify", help="verify protocol digest, run records, and outputs")
    verify.add_argument("study_dir")
    verify.set_defaults(func=cmd_verify)

    return parser


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    command: list[str] = []
    if "--" in argv:
        split = argv.index("--")
        command = argv[split + 1 :]
        argv = argv[:split]
    args = build_parser().parse_args(argv)
    if hasattr(args, "command"):
        args.command = command
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
