#!/usr/bin/env python3
"""Simulate Playwright `--shard i/n` on measured test durations and pick the shard count.

usage:
  shard_sim.py parse-log LOG [--suite-names a,b]  > suites.json
      Reads a CI log with Playwright's `list` reporter output. Every "Running N tests using
      W workers" line starts a suite; every finished test line contributes (file, seconds).
  shard_sim.py simulate suites.json --fixed-cost SECONDS [--max-shards 8] [--json]
      For n = 1..max: each shard's time is the fixed cost plus, for every suite the shard job
      runs one after another, that suite's makespan on its workers. Prints the longest shard
      per n and the n whose longest shard is shortest (ties go to the smaller n).

suites.json: {"suites": [{"name": "baseline", "workers": 2, "grouping": "file",
               "tests": [{"file": "e2e/a.e2e.ts", "seconds": 7.6}, ...]}]}
  grouping "file" (default config): one group per file, as Playwright groups tests without
  fullyParallel. grouping "test": every test is its own group (fullyParallel / parallel mode).
  order "sorted" (default): files sorted by path. Playwright 1.59 collects files depth-first,
  sorting each directory's entries with localeCompare (runner/projectUtils.js collectFiles),
  which equals a path sort for a flat, lowercase-ASCII test directory. Otherwise list the tests
  in `npx playwright test --list` order and set order "input" to keep it.

The partition is Playwright's filterForShard (playwright/lib/runner/testGroups.js, 1.59):
groups in file order, total test count split into n sizes of floor(total / n), the remainder
added one each to the first shards, and a group joins the shard in whose range its first test
falls. Groups are counted by tests, not by time; that is why a heavy file cannot be split and
why more shards can make the longest one longer. Within a shard, groups go in order to the
first free worker. Standard library only.
"""

from __future__ import annotations

import argparse
import heapq
import json
import re
import sys
from pathlib import Path

RUNNING = re.compile(r"Running (\d+) tests? using (\d+) workers?")
FINISHED = re.compile(r"[✓✘]\s+\d+\s+(?:\[[^\]]+\]\s+›\s+)?(\S+?):\d+:\d+\s+›.*\((\d+(?:\.\d+)?)(ms|s|m)\)\s*$")
UNIT = {"ms": 0.001, "s": 1.0, "m": 60.0}


def parse_log(text: str, names: list[str] | None = None) -> dict:
    suites: list[dict] = []
    for line in text.splitlines():
        running = RUNNING.search(line)
        if running:
            index = len(suites)
            name = names[index] if names and index < len(names) else f"suite{index + 1}"
            suites.append({"name": name, "workers": int(running.group(2)), "grouping": "file", "tests": []})
            continue
        finished = FINISHED.search(line)
        if finished and suites:
            seconds = float(finished.group(2)) * UNIT[finished.group(3)]
            suites[-1]["tests"].append({"file": finished.group(1), "seconds": round(seconds, 3)})
    return {"suites": suites}


def test_groups(suite: dict) -> list[tuple[int, float]]:
    """(test count, seconds) per group, in Playwright's file order."""
    keep = suite.get("order", "sorted") == "input"
    if suite.get("grouping", "file") == "test":
        ordered = suite["tests"] if keep else sorted(suite["tests"], key=lambda t: t["file"])
        return [(1, t["seconds"]) for t in ordered]
    files: dict[str, list[float]] = {}
    for test in suite["tests"]:
        files.setdefault(test["file"], []).append(test["seconds"])
    items = list(files.items()) if keep else sorted(files.items())
    return [(len(times), sum(times)) for _, times in items]


def shard_sizes(total: int, n: int) -> list[int]:
    sizes = [total // n] * n
    for i in range(total - sum(sizes)):
        sizes[i % n] += 1
    return sizes


def shard_groups(groups: list[tuple[int, float]], n: int, current: int) -> list[float]:
    """Seconds of each group in shard `current` (1-based), as filterForShard selects them."""
    sizes = shard_sizes(sum(count for count, _ in groups), n)
    start = sum(sizes[: current - 1])
    end = start + sizes[current - 1]
    picked, position = [], 0
    for count, seconds in groups:
        if start <= position < end:
            picked.append(seconds)
        position += count
    return picked


def makespan(durations: list[float], workers: int) -> float:
    free = [0.0] * max(1, workers)
    for seconds in durations:
        heapq.heappush(free, heapq.heappop(free) + seconds)
    return max(free)


def simulate(data: dict, fixed_cost: float, max_shards: int) -> dict:
    suites = [(s, test_groups(s)) for s in data["suites"]]
    rows = []
    for n in range(1, max_shards + 1):
        shards = [
            fixed_cost + sum(makespan(shard_groups(groups, n, i), s["workers"]) for s, groups in suites)
            for i in range(1, n + 1)
        ]
        rows.append({"shards": n, "per_shard": [round(x, 1) for x in shards], "longest": round(max(shards), 1)})
    best = min(rows, key=lambda r: (r["longest"], r["shards"]))
    heaviest = max(((seconds, s["name"]) for s, groups in suites for _, seconds in groups), default=(0.0, ""))
    return {
        "fixed_cost": fixed_cost,
        "rows": rows,
        "best": best["shards"],
        "floor": round(fixed_cost + heaviest[0], 1),
        "heaviest_group": {"suite": heaviest[1], "seconds": round(heaviest[0], 1)},
    }


def render(result: dict) -> str:
    out = ["| shards | longest | per shard |", "|---|---|---|"]
    for row in result["rows"]:
        mark = " <- best" if row["shards"] == result["best"] else ""
        out.append(f"| {row['shards']} | {row['longest']:.0f}s{mark} | {', '.join(f'{x:.0f}' for x in row['per_shard'])} |")
    out.append(
        f"floor: fixed cost {result['fixed_cost']:.0f}s + heaviest unsplittable group "
        f"{result['heaviest_group']['seconds']:.0f}s ({result['heaviest_group']['suite']}) = {result['floor']:.0f}s"
    )
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("parse-log")
    p.add_argument("log", type=Path)
    p.add_argument("--suite-names", help="comma-separated names, in the order the suites run")
    s = sub.add_parser("simulate")
    s.add_argument("suites", type=Path)
    s.add_argument("--fixed-cost", type=float, required=True, help="seconds each shard spends before its first test")
    s.add_argument("--max-shards", type=int, default=8)
    s.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    if args.command == "parse-log":
        names = args.suite_names.split(",") if args.suite_names else None
        print(json.dumps(parse_log(args.log.read_text(encoding="utf-8", errors="replace"), names), indent=1))
        return 0
    result = simulate(json.loads(args.suites.read_text(encoding="utf-8")), args.fixed_cost, args.max_shards)
    print(json.dumps(result, indent=1) if args.json else render(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
