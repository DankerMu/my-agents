"""Dual-assertion tests for the two readiness validators.

Audit finding (docs/2026-08-10-first-principles-audit.md): `score_readiness_report.py`
and `validate_readiness_repair.py` were named in SKILL.md's reference index as the
Audit and Repair pipeline validators, had zero tests, and were not executed by
`selfcheck.sh`. A program nothing ever runs and nothing proves can reject is the
phantom enforcement this skill exists to prevent — so each rule below is pinned in
both directions: a valid payload passes first, then one mutation per rule is
rejected with its message asserted.
"""

import importlib.util
import json
import subprocess
import sys
from copy import deepcopy
from pathlib import Path

import pytest

SKILL = Path(__file__).resolve().parents[2]
REGISTRY = SKILL / "references" / "readiness-registry.yaml"


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, SKILL / "scripts" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


score_mod = _load("score_readiness_report")
repair_mod = _load("validate_readiness_repair")
REGISTRY_DATA = score_mod.parse_registry(REGISTRY)


# --------------------------------------------------------------------------
# score_readiness_report.py
# --------------------------------------------------------------------------

def valid_report() -> dict:
    """One repository-scope row and one application-scope row over two apps.

    agents_md is repository scope (denominator 1); strict_typing is application
    scope (denominator = app count) and skippable, exercising the null-numerator
    branch. Scope is read from the registry, not assumed — an earlier draft of
    this fixture used a repository-scope criterion as the application-scope row
    and the acceptance assertion caught it.
    """
    return {
        # Schema-complete since 3.7.0: the CLI executes readiness-report-schema.json
        # before scoring, and this fixture predates that (it used `name`, which the
        # schema never allowed). It gains only fields the schema already required.
        "schema_version": 1,
        "generated_at": "2026-11-05T00:00:00Z",
        "applications": [{"path": "api", "description": "api"}, {"path": "web", "description": "web"}],
        "score": {"level": "L5", "applications_identified": 2, "average": 1.0},
        "control_plane_layers": {},
        "agents_md_constraint_dimensions": {},
        "priority_actions": [],
        "criteria": [
            {
                "id": "agents_md",
                "scope": "repository",
                "fixability": "A",
                "denominator": 1,
                "numerator": 1,
                "status": "passing",
                "evidence": "AGENTS.md exists with commands",
                "validator": "file exists and is non-trivial",
                "rescore_rule": "1/1 when present",
            },
            {
                "id": "strict_typing",
                "scope": "application",
                "fixability": "B",
                "denominator": 2,
                "numerator": None,
                "status": "skipped",
                "evidence": "neither app is typed; no type checker applicable yet",
                "validator": "type checker configured and blocking",
                "rescore_rule": "null when the stack has no type system",
            },
        ],
        "configured_but_not_blocking": [],
    }


def test_score_accepts_a_valid_report():
    """Clean input passes, or every rejection below proves nothing."""
    computed, errors = score_mod.score(valid_report(), REGISTRY_DATA)
    assert errors == [], errors
    assert computed == pytest.approx(1.0)


@pytest.mark.parametrize(
    "mutate,expected",
    [
        (lambda r: r["criteria"][0].update(id="not_a_real_criterion"), "unknown id"),
        (lambda r: r["criteria"][0].update(denominator=2), "must be 1"),
        (lambda r: r["criteria"][1].update(denominator=1), "must be 2"),
        (lambda r: r["criteria"][0].update(numerator=5), "out of range"),
        (lambda r: r["criteria"][0].update(evidence=""), "evidence is required"),
        (lambda r: r["criteria"][0].update(validator=""), "validator is required"),
        (lambda r: r["criteria"][0].update(rescore_rule=""), "rescore_rule is required"),
        (lambda r: r["score"].update(average=0.42), "does not match computed"),
        (lambda r: r["score"].update(applications_identified=7), "applications_identified"),
        (lambda r: r.update(applications=[]), "non-empty list"),
    ],
    ids=[
        "unknown-criterion", "repo-scope-denominator", "app-scope-denominator",
        "numerator-out-of-range", "missing-evidence", "missing-validator",
        "missing-rescore-rule", "average-mismatch", "app-count-mismatch",
        "empty-applications",
    ],
)
def test_score_rejects_each_violation(mutate, expected):
    report = valid_report()
    mutate(report)
    _, errors = score_mod.score(report, REGISTRY_DATA)
    assert errors, f"expected rejection for {expected!r}"
    assert any(expected in e for e in errors), f"{expected!r} not in {errors}"


def test_score_rejects_null_numerator_on_a_non_skippable_criterion():
    """A null numerator is only legal when the registry marks the criterion skippable.

    Without this, any failing criterion could be laundered into "not applicable".
    """
    report = valid_report()
    report["criteria"][0].update(numerator=None, status="skipped")
    _, errors = score_mod.score(report, REGISTRY_DATA)
    assert any("null numerator requires skippable" in e for e in errors), errors


def test_score_rejects_configured_but_not_blocking_row_claiming_full_pass():
    """Half credit must be recorded as partial, not passing."""
    report = valid_report()
    report["configured_but_not_blocking"] = ["agents_md"]
    _, errors = score_mod.score(report, REGISTRY_DATA)
    assert any("must be partial" in e for e in errors), errors


# --- 3.7.0: false passes closed (cherry-picked from upstream harness-init 4.3.x/4.4.x)

def test_schema_accepts_the_valid_report():
    """Clean side of the wire-schema gate the CLI now executes."""
    assert score_mod.validate_schema(valid_report()) == []


def test_score_rejects_a_level_inconsistent_with_the_average():
    """score.level is a claim about the average; it was never checked, so a
    report with every criterion failing could declare Level 5."""
    report = valid_report()
    _, errors = score_mod.score(report, REGISTRY_DATA)
    assert errors == [], errors  # control: the matching level passes
    report["score"]["level"] = "L1"
    _, errors = score_mod.score(report, REGISTRY_DATA)
    assert any("score.level" in e for e in errors), errors


@pytest.mark.parametrize("average,declared,ok", [
    (0.8, "L5", True),
    (0.8, "L4", False),   # L4 is 60–79; 80% belongs to L5
    (0.79, "L4", True),
    (0.2, "L2", True),    # a boundary belongs to the higher band
    (0.2, "L1", False),
    (0.0, "L1", True),
    (1.0, "L5", True),
    (1.0, "Level 5", True),
    (0.5, "Level X", False),
    (0.5, 3, False),
])
def test_score_level_band_boundaries(average, declared, ok):
    assert score_mod.level_matches(average, declared)[0] is ok


@pytest.mark.parametrize("value,valid", [
    ("2026-09-22T00:00:00Z", True),
    ("2026-09-22t08:30:00.123456789+08:00", True),
    ("2016-12-31T23:59:60Z", True),
    ("2017-01-01T07:59:60+08:00", True),
    ("2026-09-22T00:00:00z", True),
    ("2026-09-22T00:00:00+23:59", True),
    ("not a timestamp", False),
    ("{{ISO_TIMESTAMP}}", False),
    ("2026-09-22", False),
    ("2026-09-22T00:00:00", False),
    ("2026-02-30T00:00:00Z", False),
    ("2026-09-22T24:00:00Z", False),
    ("2026-09-22T10:00:00+25:00", False),
    ("2026-09-22T12:34:60Z", False),
    ("2026-12-31T23:59:60Z", False),
    ("2026-09-22T00:00:00+01:60", False),
    ("٢٠٢٦-09-22T00:00:00Z", False),
])
def test_schema_checks_generated_at_as_rfc3339_date_time(value, valid):
    """The schema's date-time format holds without the optional rfc3339-validator package."""
    report = valid_report()
    report["generated_at"] = value
    errors = [e for e in score_mod.validate_schema(report) if e.startswith("schema generated_at")]
    assert (errors == []) is valid, errors


def _fail_row(report):
    report["criteria"][0].update(numerator=0, status="failing",
                                 evidence_locations=["ls -a repo root: no AGENTS.md"])
    report["score"].update(average=0.0, level="L1")


def test_score_accepts_a_failing_row_with_evidence_locations():
    report = valid_report()
    _fail_row(report)
    _, errors = score_mod.score(report, REGISTRY_DATA)
    assert errors == [], errors
    assert score_mod.validate_schema(report) == []


def test_score_accepts_half_credit_listed_as_configured_but_not_blocking():
    """Clean side of the status/credit rule: the documented half-credit path."""
    report = valid_report()
    report["criteria"][0].update(numerator=0.5, status="partial",
                                 evidence_locations=["CI runs lint without --max-warnings 0"])
    report["configured_but_not_blocking"] = ["agents_md"]
    report["score"].update(average=0.5, level="L3")
    _, errors = score_mod.score(report, REGISTRY_DATA)
    assert errors == [], errors
    assert score_mod.validate_schema(report) == []


def test_score_accepts_zero_credit_pending_external():
    """Clean side: zero credit may be pending_external, not only failing."""
    report = valid_report()
    report["criteria"][0].update(numerator=0, status="pending_external",
                                 evidence_locations=["gh api: not permitted in this run"])
    report["score"].update(average=0.0, level="L1")
    _, errors = score_mod.score(report, REGISTRY_DATA)
    assert errors == [], errors
    assert score_mod.validate_schema(report) == []


@pytest.mark.parametrize(
    "mutate,expected",
    [
        (lambda r: r["criteria"][0].update(status="THIS_IS_NOT_A_STATUS"), "unknown status"),
        (lambda r: r["criteria"][0].update(status=["passing"]), "unknown status"),
        (lambda r: r["criteria"][0].update(numerator=True), "numerator must be number or null"),
        (lambda r: r["criteria"][0].update(numerator=float("nan")), "numerator must be number or null"),
        (lambda r: r["criteria"][0].update(scope="application"), "scope must match registry"),
        (lambda r: r["criteria"][0].update(id=["agents_md"]), "unknown id"),
        (lambda r: (r["criteria"][0].update(numerator=0), r["score"].update(average=0.0, level="L1")),
         "zero credit requires failing"),
        (lambda r: r["criteria"][0].update(status="failing", evidence_locations=["x"]),
         "full credit requires passing"),
        (lambda r: (r["criteria"][1].update(numerator=1, status="passing"),
                    r["score"].update(average=0.75, level="L4")),
         "partial credit must have partial status"),
        (lambda r: (_fail_row(r), r["criteria"][0].pop("evidence_locations")),
         "evidence_locations is required on failing rows"),
        (lambda r: (_fail_row(r), r["criteria"][0].update(evidence_locations=[""])),
         "non-empty strings"),
        (lambda r: r["score"].update(average=True), "score.average must be numeric"),
        (lambda r: r.update(configured_but_not_blocking="agents_md"), "must be a list of criterion ids"),
        (lambda r: r.update(configured_but_not_blocking=["agents_md", "agents_md"]), "must be unique"),
    ],
    ids=[
        "unknown-status", "status-array", "bool-numerator", "nan-numerator", "scope-mismatch",
        "unhashable-id", "zero-credit-passing", "full-credit-failing", "partial-credit-passing",
        "failing-without-locations", "empty-location-entry", "bool-average",
        "cbnb-not-list", "cbnb-duplicate",
    ],
)
def test_score_rejects_each_contradiction(mutate, expected):
    report = valid_report()
    mutate(report)
    try:
        _, errors = score_mod.score(report, REGISTRY_DATA)
    except Exception as exc:  # a gate reports; it does not crash
        pytest.fail(f"scorer crashed instead of rejecting: {type(exc).__name__}: {exc}")
    assert any(expected in e for e in errors), f"{expected!r} not in {errors}"


@pytest.mark.parametrize("report,expected", [
    ([1, 2, 3], "report must be an object"),
    ({"applications": [{"path": "."}], "score": [], "criteria": []}, "score must be an object"),
])
def test_score_rejects_non_object_shapes_without_crashing(report, expected):
    _, errors = score_mod.score(report, REGISTRY_DATA)
    assert any(expected in e for e in errors), errors


def _run_cli(script: str, payload: Path):
    return subprocess.run(
        [sys.executable, str(SKILL / "scripts" / script), str(payload), "--registry", str(REGISTRY)],
        capture_output=True, text=True, timeout=30)


def _dup_app(r):
    r["applications"] = [{"path": ".", "description": "first"}, {"path": "./", "description": "same app"}]


@pytest.mark.parametrize("case", [
    "duplicate_key", "nonfinite", "invalid_json", "top_level_array", "bad_date",
    "missing_required", "duplicate_app_path", "failing_without_locations",
])
def test_score_cli_rejects_malformed_wire_input_without_a_traceback(tmp_path, case):
    report = valid_report()
    if case == "bad_date":
        report["generated_at"] = "not a timestamp"
    elif case == "missing_required":
        del report["schema_version"]
    elif case == "duplicate_app_path":
        _dup_app(report)
    elif case == "failing_without_locations":
        _fail_row(report)
        del report["criteria"][0]["evidence_locations"]
    text = json.dumps(report)
    if case == "duplicate_key":
        text = text.replace('"schema_version": 1', '"schema_version": 9, "schema_version": 1')
    elif case == "nonfinite":
        text = text.replace('"average": 1.0', '"average": NaN')
    elif case == "invalid_json":
        text = "{"
    elif case == "top_level_array":
        text = "[1, 2, 3]"
    path = tmp_path / "report.json"
    path.write_text(text, encoding="utf-8")
    proc = _run_cli("score_readiness_report.py", path)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert "violation(s) found" in proc.stderr, proc.stderr
    assert "Traceback" not in proc.stderr, proc.stderr


def test_score_cli_exits_zero_then_nonzero(tmp_path, monkeypatch, capsys):
    """The CLI wrapper, not just the scoring function, must carry the exit code."""
    good = tmp_path / "good.json"
    good.write_text(json.dumps(valid_report()), encoding="utf-8")
    monkeypatch.setattr(sys, "argv", ["x", str(good), "--registry", str(REGISTRY)])
    assert score_mod.main(sys.argv) == 0
    assert "score:" in capsys.readouterr().out

    bad_report = valid_report()
    bad_report["score"]["average"] = 0.1
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps(bad_report), encoding="utf-8")
    monkeypatch.setattr(sys, "argv", ["x", str(bad), "--registry", str(REGISTRY)])
    assert score_mod.main(sys.argv) == 1
    err = capsys.readouterr().err
    assert "score-readiness-report:" in err and "violation(s) found" in err, err


# --------------------------------------------------------------------------
# validate_readiness_repair.py
# --------------------------------------------------------------------------

def valid_handoff() -> dict:
    """A class-A (skill-owned) repair reported as repaired with a green validator."""
    return {
        "schema_version": 1,
        "requested_signal": "fix the guardrail self-test",
        "matched_criterion": "guardrail_self_test",
        "fixability": "A",
        "pre_state": {"status": "failing", "score": 0, "evidence": "scripts/test-guardrails.sh absent"},
        "allowed_files": ["scripts/test-guardrails.sh", ".github/workflows/agents-md-liveness.yml"],
        "validator": {
            "command": "bash scripts/test-guardrails.sh",
            "exit_code": 0,
            "evidence": "3 passed, 0 failed",
        },
        # `score` was always required by readiness-repair-schema.json; the fixture
        # gains it now that validate() executes the schema (3.7.0).
        "post_state": {
            "status": "passing",
            "score": 1,
            "rescore_evidence": "guardrail_self_test=1/1",
        },
        "decision": "repaired",
    }


def test_repair_accepts_a_valid_handoff():
    """Clean input passes first."""
    assert repair_mod.validate(valid_handoff(), REGISTRY_DATA) == []


@pytest.mark.parametrize(
    "mutate,expected",
    [
        (lambda h: h.pop("requested_signal"), "missing required field"),
        (lambda h: h.update(matched_criterion="invented_criterion"), "not in readiness registry"),
        (lambda h: h.update(decision="looks_fine_to_me"), "invalid decision"),
        (lambda h: h.update(fixability="D"), "must match registry"),
        (lambda h: h["validator"].update(command=""), "validator.command is required"),
        (lambda h: h["validator"].pop("exit_code"), "validator.exit_code is required"),
        (lambda h: h["validator"].update(evidence=""), "validator.evidence is required"),
        (lambda h: h["pre_state"].update(evidence=""), "pre_state.evidence is required"),
        (lambda h: h["post_state"].update(rescore_evidence=""), "rescore_evidence is required"),
        (lambda h: h.update(allowed_files="scripts/x.sh"), "allowed_files must be a list"),
        (lambda h: h["validator"].update(exit_code=1), "requires validator.exit_code=0"),
    ],
    ids=[
        "missing-field", "unknown-criterion", "invalid-decision", "fixability-mismatch",
        "no-validator-command", "no-exit-code", "no-validator-evidence",
        "no-pre-evidence", "no-rescore-evidence", "allowed-files-not-list",
        "repaired-with-red-validator",
    ],
)
def test_repair_rejects_each_violation(mutate, expected):
    handoff = valid_handoff()
    mutate(handoff)
    errors = repair_mod.validate(handoff, REGISTRY_DATA)
    assert errors, f"expected rejection for {expected!r}"
    assert any(expected in e for e in errors), f"{expected!r} not in {errors}"


def test_repair_rejects_fake_local_completion_of_an_external_criterion():
    """The anti-gaming rule this validator exists for.

    A class-D external/governance control (branch protection is set server-side)
    cannot be completed by editing local files. Claiming `repaired` without
    authenticated external evidence must be rejected, or the loop can mark
    governance work done by writing a file.
    """
    external = [cid for cid, m in REGISTRY_DATA.items() if m.get("fixability") == "D"]
    assert external, "registry must contain at least one class-D criterion for this test to mean anything"
    handoff = valid_handoff()
    handoff.update(matched_criterion=external[0], fixability="D")
    errors = repair_mod.validate(handoff, REGISTRY_DATA)
    assert any("fake local completion" in e for e in errors), errors

    # The escape hatch must work: authenticated external evidence is accepted.
    ok = deepcopy(handoff)
    ok["validator"]["evidence"] = "authenticated gh api call shows the ruleset enabled"
    assert not [e for e in repair_mod.validate(ok, REGISTRY_DATA) if "fake local completion" in e]


def test_repair_rejects_metric_gaming_prone_repair_without_evidence():
    """unit_tests_exist / lint_config / test_coverage_thresholds are the criteria a
    loop can satisfy with empty tests or a disabled config, so a repaired handoff
    must record what gaming it rejected."""
    handoff = valid_handoff()
    handoff.update(matched_criterion="unit_tests_exist",
                   fixability=REGISTRY_DATA["unit_tests_exist"]["fixability"])
    errors = repair_mod.validate(handoff, REGISTRY_DATA)
    assert any("metric_gaming_rejected" in e for e in errors), errors

    handoff["metric_gaming_rejected"] = ["no assertion-free placeholder tests were added"]
    assert not [e for e in repair_mod.validate(handoff, REGISTRY_DATA) if "metric_gaming_rejected" in e]


def test_repair_rejects_blocked_decision_claiming_a_passing_post_state():
    handoff = valid_handoff()
    handoff.update(decision="pending_external")
    errors = repair_mod.validate(handoff, REGISTRY_DATA)
    assert any("cannot produce a passing post_state" in e for e in errors), errors


# --- 3.7.0: wire and state contract (cherry-picked from upstream harness-init 4.3.1)

@pytest.mark.parametrize("mutator", [
    lambda d: [],
    lambda d: {**d, "schema_version": 99},
    lambda d: {**d, "validator": []},
    lambda d: {**d, "matched_criterion": []},
    lambda d: {**d, "pre_state": {"status": "failing", "evidence": "x"}},
    lambda d: {**d, "validator": {**d["validator"], "exit_code": False}},
    lambda d: {**d, "requested_signal": "   "},
    lambda d: {**d, "allowed_files": ["../outside"]},
    lambda d: {**d, "allowed_files": ["a", "./a"]},
    lambda d: {**d, "allowed_files": ["a", "a"]},
    lambda d: {**d, "allowed_files": ["/tmp/outside"]},
    lambda d: {**d, "allowed_files": ["x\\y"]},
    lambda d: {**d, "allowed_files": [".git/hooks/pre-commit"]},
    lambda d: {**d, "surprise_authorization": True},
], ids=[
    "top-level-array", "schema-version", "validator-array", "criterion-array",
    "state-without-score", "bool-exit-code", "blank-signal", "traversal", "alias-path",
    "duplicate-path", "absolute-path", "backslash-path", "dot-git-path", "unknown-field",
])
def test_repair_rejects_malformed_wire_types_without_crashing(mutator):
    data = mutator(valid_handoff())
    try:
        errors = repair_mod.validate(data, REGISTRY_DATA)
    except Exception as exc:
        pytest.fail(f"validator crashed instead of rejecting: {type(exc).__name__}: {exc}")
    assert errors, f"accepted malformed repair handoff: {data!r}"


@pytest.mark.parametrize("kind,expected", [
    ("noop_failed_validator", "no-op decision requires validator.exit_code=0"),
    ("passing_zero", "passing requires score=1"),
    ("non_skippable_skip", "requires a skippable registry criterion"),
    ("partial_full", "partial requires 0 < score < 1"),
    ("nonfinite", "must be null or a finite number"),
    ("pending_mismatch", "pending_external decision requires pending_external post_state"),
])
def test_repair_rejects_inconsistent_terminal_state(kind, expected):
    d = valid_handoff()
    if kind == "noop_failed_validator":
        d["decision"] = "no_op_already_passing"
        d["pre_state"].update(status="passing", score=1)
        d["validator"]["exit_code"] = 9
    elif kind == "passing_zero":
        d["post_state"]["score"] = 0
    elif kind == "non_skippable_skip":
        d["matched_criterion"] = "agents_md"  # registry marks this criterion non-skippable
        d["post_state"].update(status="skipped", score=None)
    elif kind == "partial_full":
        d["post_state"].update(status="partial", score=1)
    elif kind == "nonfinite":
        d["post_state"]["score"] = float("inf")
    else:
        d["decision"] = "pending_external"
        d["post_state"].update(status="failing", score=0)
    errors = repair_mod.validate(d, REGISTRY_DATA)
    assert any(expected in e for e in errors), errors


def test_repair_accepts_a_skipped_post_state_on_a_skippable_criterion():
    """Clean side: the skippable rule must not over-reject a legitimate skip."""
    d = valid_handoff()
    d["post_state"].update(status="skipped", score=None,
                           rescore_evidence="Not applicable: no guardrails selected; scope reviewed.")
    assert repair_mod.validate(d, REGISTRY_DATA) == []


def _valid_json_with(prefix: str) -> str:
    """A valid handoff with `prefix` injected first: with last-key-wins parsing
    the payload would be accepted, so only duplicate-key rejection fails it."""
    return "{" + prefix + ", " + json.dumps(valid_handoff())[1:]


@pytest.mark.parametrize("raw", [
    _valid_json_with('"schema_version": 99'),
    _valid_json_with('"decision": "nonsense"'),
    json.dumps(valid_handoff()).replace('"score": 1', '"score": NaN'),
    "[1,2,3]",
    "{",
], ids=["duplicate-key", "duplicate-decision", "nonfinite", "array", "truncated"])
def test_repair_cli_rejects_malformed_wire_input_without_a_traceback(tmp_path, raw):
    path = tmp_path / "payload.json"
    path.write_text(raw, encoding="utf-8")
    proc = _run_cli("validate_readiness_repair.py", path)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert "violation(s) found" in proc.stderr, proc.stderr
    assert "Traceback" not in proc.stderr, proc.stderr


def test_repair_cli_accepts_the_valid_payload_the_duplicate_cases_build_on(tmp_path):
    path = tmp_path / "payload.json"
    path.write_text(json.dumps(valid_handoff()), encoding="utf-8")
    proc = _run_cli("validate_readiness_repair.py", path)
    assert proc.returncode == 0, proc.stdout + proc.stderr


def test_repair_cli_exits_zero_then_nonzero(tmp_path, monkeypatch, capsys):
    good = tmp_path / "good.json"
    good.write_text(json.dumps(valid_handoff()), encoding="utf-8")
    monkeypatch.setattr(sys, "argv", ["x", str(good), "--registry", str(REGISTRY)])
    assert repair_mod.main(sys.argv) == 0
    assert "conforms" in capsys.readouterr().out

    bad_handoff = valid_handoff()
    bad_handoff["decision"] = "nonsense"
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps(bad_handoff), encoding="utf-8")
    monkeypatch.setattr(sys, "argv", ["x", str(bad), "--registry", str(REGISTRY)])
    assert repair_mod.main(sys.argv) == 1
    err = capsys.readouterr().err
    assert "validate-readiness-repair:" in err and "violation(s) found" in err, err


def test_documented_json_companion_example_is_a_valid_report():
    """The JSON companion example in agent-readiness-criteria.md is what agents copy.

    It drifted from the schema once (it used `level`/`failing_criteria` keys the
    schema never allowed) and nothing noticed; pin it through the same schema and
    scorer the CLI runs.
    """
    doc = (SKILL / "references" / "agent-readiness-criteria.md").read_text(encoding="utf-8")
    marker = "JSON companion shape"
    assert marker in doc
    block = doc[doc.index(marker):]
    start = block.index("```json\n") + len("```json\n")
    example = json.loads(block[start:block.index("```", start)])
    assert score_mod.validate_schema(example) == []
    computed, errors = score_mod.score(example, REGISTRY_DATA)
    assert errors == [], errors
    assert computed == pytest.approx(example["score"]["average"])
