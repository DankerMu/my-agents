"""shard_sim.py: Playwright's real partition, and the open-webui#758 result that 3 shards beat 4."""

import json

import pytest
from conftest import FIXTURES, SKILL, load

ss = load("shard_sim", SKILL / "scripts" / "shard_sim.py")
SUITES = json.loads((FIXTURES / "open-webui" / "playwright-suites.json").read_text(encoding="utf-8"))
FIXED_COST = 210  # ~3.5 min per shard before the first test: setup, dev server, OCU stack


def test_fixture_is_the_measured_browser_run():
    assert [(s["name"], s["workers"], len(s["tests"])) for s in SUITES["suites"]] == [("baseline", 2, 44), ("ocu", 1, 51)]


def test_three_shards_beat_four_on_open_webui():
    result = ss.simulate(SUITES, FIXED_COST, 6)
    longest = {row["shards"]: row["longest"] for row in result["rows"]}
    assert result["best"] == 3
    assert longest[3] < longest[4]
    assert longest[3] < longest[2] < longest[1]


def test_every_test_lands_in_exactly_one_shard():
    for suite in SUITES["suites"]:
        groups = ss.test_groups(suite)
        for n in range(1, 7):
            picked = [seconds for i in range(1, n + 1) for seconds in ss.shard_groups(groups, n, i)]
            assert sorted(picked) == sorted(seconds for _, seconds in groups)


@pytest.mark.parametrize("total, n, sizes", [(10, 3, [4, 3, 3]), (95, 4, [24, 24, 24, 23]), (2, 3, [1, 1, 0])])
def test_shard_sizes_follow_filter_for_shard(total, n, sizes):
    assert ss.shard_sizes(total, n) == sizes


def test_a_group_joins_the_shard_where_its_first_test_falls():
    # Three files of 3, 1 and 2 tests: total 6, two shards of 3. File 2 starts at index 3 -> shard 2.
    groups = [(3, 30.0), (1, 10.0), (2, 20.0)]
    assert ss.shard_groups(groups, 2, 1) == [30.0]
    assert ss.shard_groups(groups, 2, 2) == [10.0, 20.0]


def test_one_heavy_file_bounds_the_longest_shard():
    data = {"suites": [{"name": "s", "workers": 1, "tests": [{"file": "a", "seconds": 100}] + [
        {"file": f"b{i}", "seconds": 1} for i in range(9)]}]}
    result = ss.simulate(data, 0, 5)
    assert all(row["longest"] >= 100 for row in result["rows"])
    assert result["floor"] == 100


def test_test_grouping_splits_files():
    suite = {"name": "s", "workers": 1, "grouping": "test", "tests": [{"file": "a", "seconds": 5}] * 4}
    assert ss.test_groups(suite) == [(1, 5)] * 4


def test_parse_log_reads_seconds_minutes_and_milliseconds():
    log = "\n".join([
        "2026-11-06T17:37:44Z Running 3 tests using 2 workers",
        "2026-11-06T17:38:07Z   ✓   1 e2e/a.e2e.ts:90:2 › first (7.6s)",
        "2026-11-06T17:38:07Z   ✘   2 [chromium] › e2e/b.e2e.ts:10:1 › slow (1.5m)",
        "2026-11-06T17:38:07Z   ✓   3 e2e/a.e2e.ts:99:2 › quick (450ms)",
        "2026-11-06T17:38:08Z Running 1 test using 1 worker",
        "2026-11-06T17:38:09Z   ✓   1 e2e/c.e2e.ts:1:1 › only (2.0s)",
    ])
    suites = ss.parse_log(log, ["base", "ocu"])["suites"]
    assert [(s["name"], s["workers"]) for s in suites] == [("base", 2), ("ocu", 1)]
    assert suites[0]["tests"] == [
        {"file": "e2e/a.e2e.ts", "seconds": 7.6},
        {"file": "e2e/b.e2e.ts", "seconds": 90.0},
        {"file": "e2e/a.e2e.ts", "seconds": 0.45},
    ]
    assert suites[1]["tests"] == [{"file": "e2e/c.e2e.ts", "seconds": 2.0}]
