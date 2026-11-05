#!/usr/bin/env python3
"""Validate an eng-init readiness repair handoff JSON file."""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gate_output import report  # noqa: E402

TERMINAL_DECISIONS = {
    "repaired",
    "no_op_already_passing",
    "blocked_missing_prerequisite",
    "pending_external",
    "not_locally_fixable",
}


def parse_registry(path: Path) -> dict[str, dict[str, str]]:
    registry: dict[str, dict[str, str]] = {}
    current: dict[str, str] | None = None
    for raw in path.read_text().splitlines():
        if raw.startswith("  - id: "):
            if current is not None:
                registry[current["id"]] = current
            current = {"id": raw.split(":", 1)[1].strip()}
            continue
        if current is None:
            continue
        match = re.match(r"^    ([a-z_]+):\s*(.*)$", raw.rstrip())
        if match:
            current[match.group(1)] = match.group(2).strip().strip('"').strip("'")
    if current is not None:
        registry[current["id"]] = current
    return registry


def fail_if(condition: bool, message: str, errors: list[str]) -> None:
    if condition:
        errors.append(message)


def validate_schema(payload: object) -> list[str]:
    """Check the declared wire schema, on CLI and direct calls alike; not execution proof.

    A missing validation dependency fails closed: a gate that could not run has
    not passed.
    """
    try:
        from jsonschema import Draft202012Validator
        from jsonschema.exceptions import SchemaError
    except ImportError:
        return ["schema validation unavailable: run through `uv run --with jsonschema` (see SKILL.md reference index)"]
    try:
        schema_path = Path(__file__).resolve().parents[1] / "references/readiness-repair-schema.json"
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        return [f"schema {'.'.join(map(str, e.absolute_path)) or '$'}: {e.message}"
                for e in sorted(Draft202012Validator(schema).iter_errors(payload),
                                key=lambda e: str(list(e.absolute_path)))]
    except (OSError, ValueError, SchemaError) as exc:
        return [f"schema validation unavailable: {exc}"]


def _check_state(state: dict, label: str, errors: list[str]) -> None:
    """The normalized score must agree with the status it is reported under."""
    score = state.get("score")
    status = state.get("status")
    numeric = type(score) in (int, float) and math.isfinite(score) and 0 <= score <= 1
    if score is not None and not numeric:
        errors.append(f"{label}.score must be null or a finite number in 0..1")
    if status == "passing" and (not numeric or score != 1):
        errors.append(f"{label}: passing requires score=1")
    elif status in {"failing", "missing"} and (not numeric or score != 0):
        errors.append(f"{label}: failing/missing requires score=0")
    elif status == "partial" and (not numeric or not 0 < score < 1):
        errors.append(f"{label}: partial requires 0 < score < 1")
    elif status in {"skipped", "unknown", "pending_external"} and score is not None:
        errors.append(f"{label}: {status} requires score=null")


def _check_paths(paths: object, errors: list[str]) -> None:
    """allowed_files bounds the repair's write set, so each entry must name one
    canonical repo-relative path: no absolute path, traversal, `.git`, alias
    spelling (`./a` next to `a`), or duplicate."""
    if not isinstance(paths, list):
        return
    seen = set()
    for path in paths:
        if (not isinstance(path, str) or not path.strip() or path != path.strip()
                or "\\" in path or "\x00" in path or ":" in path
                or any(part in {"", ".", "..", ".git"} for part in path.split("/"))):
            errors.append(f"allowed_files must contain canonical repo-relative file paths: {path!r}")
            continue
        if path in seen:
            errors.append(f"duplicate allowed_files path: {path}")
        seen.add(path)


def validate(payload: object, registry: dict[str, dict[str, str]]) -> list[str]:
    errors = validate_schema(payload)
    if not isinstance(payload, dict):
        return errors or ["repair handoff must be an object"]
    required = ["schema_version", "requested_signal", "matched_criterion", "pre_state", "fixability", "allowed_files", "validator", "post_state", "decision"]
    for field in required:
        fail_if(field not in payload, f"missing required field: {field}", errors)
    cid = payload.get("matched_criterion")
    meta = registry.get(cid) if isinstance(cid, str) else None
    fail_if(meta is None, f"matched_criterion is not in readiness registry: {cid!r}", errors)
    decision = payload.get("decision")
    fail_if(not isinstance(decision, str) or decision not in TERMINAL_DECISIONS, f"invalid decision: {decision!r}", errors)
    # Never dereference a scalar/list where an object belongs: a gate reports,
    # it does not crash on the input it is judging.
    pre = payload.get("pre_state") if isinstance(payload.get("pre_state"), dict) else {}
    post = payload.get("post_state") if isinstance(payload.get("post_state"), dict) else {}
    validator = payload.get("validator") if isinstance(payload.get("validator"), dict) else {}
    for state, label in ((pre, "pre_state"), (post, "post_state")):
        if isinstance(state.get("status"), str):
            _check_state(state, label, errors)
    _check_paths(payload.get("allowed_files"), errors)
    fail_if(not isinstance(payload.get("requested_signal"), str) or not payload["requested_signal"].strip(),
            "requested_signal is required", errors)
    fail_if(not isinstance(payload.get("allowed_files"), list), "allowed_files must be a list", errors)
    fail_if(not validator.get("command"), "validator.command is required", errors)
    fail_if("exit_code" not in validator, "validator.exit_code is required", errors)
    fail_if(not validator.get("evidence"), "validator.evidence is required", errors)
    fail_if(not pre.get("evidence"), "pre_state.evidence is required", errors)
    fail_if(not post.get("rescore_evidence"), "post_state.rescore_evidence is required", errors)
    if meta is not None:
        fail_if(payload.get("fixability") != meta.get("fixability"), f"fixability {payload.get('fixability')!r} must match registry {meta.get('fixability')!r}", errors)
        # Class D external/governance controls cannot be faked by local files. They require pending/external disposition
        # unless authenticated external evidence is named explicitly in the validator evidence.
        if meta.get("fixability") == "D":
            evidence_text = str(validator.get("evidence", "")).lower()
            external_evidence = "authenticated" in evidence_text
            fake_local_completion = decision == "repaired" or post.get("status") == "passing"
            fail_if(fake_local_completion and not external_evidence, "Class D fake local completion rejected: use pending_external or provide authenticated external evidence", errors)
    if meta is not None and post.get("status") == "skipped":
        fail_if(meta.get("skippable") != "true", "post_state skipped requires a skippable registry criterion", errors)
    # type() is int, not isinstance(): `false` must not pass as exit code 0.
    exit_ok = type(validator.get("exit_code")) is int and validator.get("exit_code") == 0
    if decision == "repaired":
        fail_if(not exit_ok, "repaired decision requires validator.exit_code=0", errors)
        fail_if(post.get("status") not in ("passing", "partial", "skipped"), "repaired decision requires passing/partial/skipped post_state", errors)
    if decision == "no_op_already_passing":
        fail_if(not exit_ok, "no-op decision requires validator.exit_code=0", errors)
        fail_if(pre.get("status") != "passing" or post.get("status") != "passing", "no-op decision requires pre and post passing", errors)
    if decision == "pending_external":
        fail_if(post.get("status") != "pending_external", "pending_external decision requires pending_external post_state", errors)
    if decision in ("blocked_missing_prerequisite", "pending_external", "not_locally_fixable"):
        fail_if(post.get("status") == "passing", f"{decision} cannot produce a passing post_state", errors)
    gaming = payload.get("metric_gaming_rejected", [])
    # Tuples, not sets: an attacker-shaped list value is unhashable, and a set
    # membership test on it crashes the gate instead of rejecting the input.
    if cid in ("unit_tests_exist", "lint_config", "test_coverage_thresholds") and decision == "repaired":
        fail_if(not gaming, f"{cid}: repaired handoff must record metric_gaming_rejected evidence", errors)
    return errors


def _unique_object(pairs: list[tuple[str, object]]) -> dict:
    # json.loads keeps the last duplicate silently (`"decision":"x","decision":"repaired"`).
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise ValueError(f"duplicate JSON key: {key}")
        obj[key] = value
    return obj


def _nonfinite(value: str) -> None:
    raise ValueError(f"non-finite JSON constant: {value}")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Validate eng-init readiness repair handoff JSON")
    parser.add_argument("handoff")
    parser.add_argument("--registry", default=str(Path(__file__).resolve().parents[1] / "references/readiness-registry.yaml"))
    args = parser.parse_args(argv[1:])

    try:
        payload = json.loads(Path(args.handoff).read_text(encoding="utf-8"),
                             object_pairs_hook=_unique_object, parse_constant=_nonfinite)
        registry = parse_registry(Path(args.registry))
        errors = validate(payload, registry)
    except (OSError, UnicodeError, ValueError, RecursionError) as exc:
        return report("validate-readiness-repair", [f"input could not be validated: {exc}"], "")
    criterion = payload.get("matched_criterion") if isinstance(payload, dict) else None
    return report("validate-readiness-repair", errors,
                  f"repair handoff for {criterion} conforms")


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
