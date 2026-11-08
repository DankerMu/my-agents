"""ci_timings.py against the frozen DankerMu/open-webui runs from issue #23 (before and after #758)."""

import json

import pytest
from conftest import FIXTURES, SKILL, load

ct = load("ci_timings", SKILL / "scripts" / "ci_timings.py")
OWUI = FIXTURES / "open-webui"


@pytest.fixture(scope="module")
def before():
    return ct.build_report(OWUI / "before", OWUI / "ci-before.yml", ct.DEFAULT_SETUP_PATTERN, 15)


@pytest.fixture(scope="module")
def after():
    return ct.build_report(OWUI / "after", OWUI / "ci-after.yml", ct.DEFAULT_SETUP_PATTERN, 15)


def job(report, prefix):
    return next(j for j in report["jobs"] if j["job"].startswith(prefix))


def step(report, name):
    return next(s for s in report["steps"] if s["step"] == name)


def test_baseline_wall_clock_matches_the_issue(before):
    assert before["runs"]["total"] == 50
    assert before["runs"]["successful"] == 35
    assert before["wall_clock_s"]["median"] / 60 == pytest.approx(24.9, abs=0.1)


def test_baseline_job_and_step_medians_match_the_issue(before):
    # Issue #23 baseline: fast checks 455 s, anti-drift 147 s, unit tests 971 s.
    assert job(before, "Fast checks")["total"] == pytest.approx(455, abs=5)
    assert job(before, "Anti-drift")["total"] == pytest.approx(147, abs=5)
    assert job(before, "Unit tests")["total"] == pytest.approx(971, abs=5)
    # The slowest steps: serial browser run 709 s, coverage gate 427 s, serial lint 242 s.
    assert step(before, "Baseline and isolated workspace browser verification")["median"] == pytest.approx(709, abs=5)
    assert step(before, "Run make coverage-gate")["median"] == pytest.approx(427, abs=5)
    assert step(before, "Run make lint-scoped")["median"] == pytest.approx(242, abs=5)


def test_setup_is_two_minutes_per_job_and_queueing_is_negligible(before):
    for prefix in ("Fast checks", "Unit tests", "Runtime verification", "Anti-drift"):
        row = job(before, prefix)
        assert 110 <= row["setup"] <= 170, row
        assert row["queue"] < 10, row


def test_critical_path_and_dataless_needs(before):
    paths = dict(before["critical_path"]["paths"])
    assert set(paths) == {"layer1-fast-checks -> layer2-unit-tests", "layer1-fast-checks -> layer3-integration-tests"}
    assert sum(paths.values()) == 35
    assert sorted(before["dataless_needs"]) == [
        ("layer2-unit-tests", "layer1-fast-checks"),
        ("layer3-integration-tests", "layer1-fast-checks"),
        ("layer4-anti-drift", "layer1-fast-checks"),
    ]


def test_after_is_under_ten_minutes_and_the_critical_path_moved(after, before):
    assert after["wall_clock_s"]["median"] < 10 * 60
    assert after["wall_clock_s"]["median"] < before["wall_clock_s"]["median"] / 2
    roots = {path.split(" -> ")[-1] for path, _ in after["critical_path"]["paths"]}
    assert roots <= {"layer3-browser", "layer2-backend-tests"}
    assert after["dataless_needs"] == []


def test_matrix_job_names_map_back_to_their_workflow_job():
    workflow = ct.parse_workflow((OWUI / "ci-after.yml").read_text(encoding="utf-8"))
    assert ct.job_id_for("Browser verification (shard 2)", workflow) == "layer3-browser"
    assert ct.job_id_for("Change classification", workflow) == "changes"
    assert ct.job_id_for("no such job", workflow) is None


def test_step_level_always_does_not_hide_a_dataless_need():
    workflow = ct.parse_workflow(
        "jobs:\n"
        "  a:\n    runs-on: x\n    steps:\n      - run: true\n"
        "  b:\n    needs: a\n    steps:\n      - run: make test\n      - run: make stop\n        if: always()\n"
        "  gate:\n    if: always()\n    needs: [a, b]\n    steps:\n      - run: echo '${{ toJSON(needs) }}'\n"
    )
    assert workflow["gate"]["needs"] == ["a", "b"]
    assert ct.dataless_needs(workflow) == [("b", "a")]


def test_needs_read_through_outputs_is_not_dataless():
    workflow = ct.parse_workflow(
        "jobs:\n  a:\n    outputs:\n      v: x\n  b:\n    needs:\n      - a\n    steps:\n      - run: echo ${{ needs.a.outputs.v }}\n"
    )
    assert ct.dataless_needs(workflow) == []


def test_without_a_workflow_the_critical_path_is_reported_unknown():
    report = ct.build_report(OWUI / "before", None, ct.DEFAULT_SETUP_PATTERN, 5)
    assert report["critical_path"]["known"] is False
    assert "needs graph unknown" in ct.render(report)


def test_stale_caches_flag_superseded_keys_and_pr_scoped_refs(tmp_path):
    caches = [
        {"id": 1, "key": "uv-linux-3.11.9-aaaaaaaaaa", "ref": "refs/heads/main", "size_in_bytes": 2_900_000_000,
         "created_at": "2026-11-01T00:00:00Z", "last_accessed_at": "2026-11-01T00:00:00Z"},
        {"id": 2, "key": "uv-linux-3.11.9-bbbbbbbbbb", "ref": "refs/heads/main", "size_in_bytes": 2_900_000_000,
         "created_at": "2026-11-06T00:00:00Z", "last_accessed_at": "2026-11-07T00:00:00Z"},
        {"id": 3, "key": "node-modules-linux-cccccccccc", "ref": "refs/pull/700/merge", "size_in_bytes": 400_000_000,
         "created_at": "2026-11-05T00:00:00Z", "last_accessed_at": "2026-11-05T00:00:00Z"},
    ]
    flagged = {c["id"]: why for c, why in ct.stale_caches(caches)}
    assert set(flagged) == {1, 3}
    assert "superseded by uv-linux-3.11.9-bbbbbbbbbb" in flagged[1]
    assert flagged[3].startswith("PR-scoped")


def test_only_the_latest_attempt_counts(tmp_path):
    run = {"id": 9, "event": "push", "head_branch": "main", "conclusion": "success", "run_attempt": 2,
           "created_at": "2026-11-07T00:00:00Z", "run_started_at": "2026-11-07T00:30:00Z", "updated_at": "2026-11-07T00:40:00Z"}
    def j(attempt, start, end):
        return {"id": attempt, "name": "test", "run_attempt": attempt, "status": "completed", "conclusion": "success",
                "created_at": start, "started_at": start, "completed_at": end, "steps": []}
    (tmp_path / "jobs").mkdir()
    (tmp_path / "runs.json").write_text(json.dumps([run]))
    (tmp_path / "jobs" / "9.json").write_text(json.dumps([
        j(1, "2026-11-07T00:00:00Z", "2026-11-07T00:20:00Z"),
        j(2, "2026-11-07T00:30:00Z", "2026-11-07T00:40:00Z"),
    ]))
    report = ct.build_report(tmp_path, None, ct.DEFAULT_SETUP_PATTERN, 5)
    assert report["jobs"][0]["total"] == 600
