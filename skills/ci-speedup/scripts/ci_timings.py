#!/usr/bin/env python3
"""Measure GitHub Actions runs: where the wall-clock time goes, per job and per step.

usage:
  ci_timings.py fetch --repo OWNER/NAME --workflow ci.yml --out DIR [--limit 50] [--branch B] [--before ISO]
      Writes DIR/runs.json, DIR/jobs/<run id>.json and DIR/caches.json through `gh api`.
      Only the fields `report` reads are kept, so DIR can be committed as a fixture.
  ci_timings.py report DIR [--workflow-file PATH] [--setup-pattern REGEX] [--top 15] [--json]
      Offline. Prints the baseline: wall clock, per-job queue/setup/test medians, the slowest
      steps, the critical path through the `needs` graph, `needs` that pass no data, and the
      cache inventory with stale candidates.

Definitions (keep them fixed between the before and after measurements):
  wall clock  run created_at -> last job completed_at, latest attempt, successful runs only
  queue       job started_at - job created_at
  setup       sum of the steps whose name matches the setup pattern
  test        job duration (started_at -> completed_at) minus setup
  p90         nearest rank: the ceil(0.9 * n)-th smallest value
Standard library only, so it runs with any python3 >= 3.9.
"""

from __future__ import annotations

import argparse
import collections
import json
import math
import re
import statistics
import subprocess
import sys
from datetime import datetime
from pathlib import Path

DEFAULT_SETUP_PATTERN = (
    r"(?i)^(set up job|complete job|post )|checkout|setup|cache|\binstall\b"
    r"|\b(npm|pnpm|yarn) ci\b|\buv sync\b"
)
RUN_FIELDS = ("id", "event", "head_branch", "conclusion", "created_at", "run_started_at", "updated_at", "run_attempt")
JOB_FIELDS = ("id", "name", "run_attempt", "status", "conclusion", "created_at", "started_at", "completed_at")
STEP_FIELDS = ("name", "conclusion", "started_at", "completed_at")
CACHE_FIELDS = ("id", "key", "ref", "size_in_bytes", "created_at", "last_accessed_at")


# --- fetch -------------------------------------------------------------------------------


def gh_json(path: str) -> object:
    out = subprocess.run(["gh", "api", path], check=True, capture_output=True, text=True).stdout
    return json.loads(out)


def pick(obj: dict, fields: tuple[str, ...]) -> dict:
    return {k: obj.get(k) for k in fields}


def fetch(args: argparse.Namespace) -> int:
    out = Path(args.out)
    (out / "jobs").mkdir(parents=True, exist_ok=True)
    runs: list[dict] = []
    page = 1
    while len(runs) < args.limit:
        query = f"per_page=100&page={page}" + (f"&branch={args.branch}" if args.branch else "")
        batch = gh_json(f"repos/{args.repo}/actions/workflows/{args.workflow}/runs?{query}")["workflow_runs"]
        if not batch:
            break
        runs.extend(r for r in batch if not args.before or r["created_at"] < args.before)
        page += 1
    runs = [pick(r, RUN_FIELDS) for r in runs[: args.limit]]
    (out / "runs.json").write_text(json.dumps(runs, indent=1) + "\n", encoding="utf-8")
    for run in runs:
        jobs = gh_json(f"repos/{args.repo}/actions/runs/{run['id']}/jobs?per_page=100&filter=all")["jobs"]
        trimmed = [dict(pick(j, JOB_FIELDS), steps=[pick(s, STEP_FIELDS) for s in j.get("steps") or []]) for j in jobs]
        (out / "jobs" / f"{run['id']}.json").write_text(json.dumps(trimmed, indent=1) + "\n", encoding="utf-8")
    caches = gh_json(f"repos/{args.repo}/actions/caches?per_page=100").get("actions_caches", [])
    (out / "caches.json").write_text(json.dumps([pick(c, CACHE_FIELDS) for c in caches], indent=1) + "\n", encoding="utf-8")
    print(f"fetched {len(runs)} runs and {len(caches)} caches into {out}")
    return 0


# --- workflow needs graph ----------------------------------------------------------------


def parse_needs(value: str) -> list[str]:
    value = value.split("#", 1)[0].strip()
    if value.startswith("["):
        return [v.strip().strip("'\"") for v in value.strip("[]").split(",") if v.strip()]
    return [value.strip("'\"")] if value else []


def parse_workflow(text: str) -> dict[str, dict]:
    """Job id -> {name, needs, body}. Hand-rolled for the subset of YAML that job headers use."""
    lines = text.splitlines()
    start = next((i for i, line in enumerate(lines) if re.match(r"^jobs:\s*(#.*)?$", line)), None)
    if start is None:
        return {}
    jobs: dict[str, dict] = {}
    job_indent = None
    current = None
    for line in lines[start + 1 :]:
        if line.strip() == "" or line.lstrip().startswith("#"):
            if current:
                current["body"].append(line)
            continue
        indent = len(line) - len(line.lstrip())
        if indent == 0:
            break
        if job_indent is None:
            job_indent = indent
        header = re.match(r"^\s*([A-Za-z0-9_-]+):\s*(#.*)?$", line)
        if indent == job_indent and header:
            current = {"name": header.group(1), "needs": [], "if": "", "body": []}
            jobs[header.group(1)] = current
            continue
        if current is None:
            continue
        current["body"].append(line)
        key = re.match(r"^\s*(name|needs|if):\s*(.*)$", line)
        if key and indent == job_indent + 2:
            if key.group(1) == "if":
                current["if"] = key.group(2).strip()
            elif key.group(1) == "name" and key.group(2):
                current["name"] = key.group(2).strip().strip("'\"")
            elif key.group(1) == "needs":
                current["needs"] = parse_needs(key.group(2))
                current["_block_needs"] = not key.group(2).strip()
            continue
        if current.get("_block_needs"):
            item = re.match(r"^\s*-\s*([A-Za-z0-9_-]+)\s*(#.*)?$", line)
            if item and indent > job_indent + 2:
                current["needs"].append(item.group(1))
                continue
            if indent <= job_indent + 2:
                current["_block_needs"] = False
    for job in jobs.values():
        job.pop("_block_needs", None)
        job["body"] = "\n".join(job["body"])
    return jobs


def job_id_for(api_name: str, workflow: dict[str, dict]) -> str | None:
    """Map an API job name (matrix-expanded) back to its workflow job id."""
    for job_id, job in workflow.items():
        name = job["name"]
        prefix = name.split("${{", 1)[0]
        if api_name == name or api_name == job_id:
            return job_id
        if "${{" in name and prefix and api_name.startswith(prefix):
            return job_id
        if api_name.startswith(name + " ("):
            return job_id
    return None


def dataless_needs(workflow: dict[str, dict]) -> list[tuple[str, str]]:
    """(job, dependency) pairs where the job never reads needs.<dependency>.*.

    An always() aggregator legitimately reads only toJSON(needs); it is excluded. Only the
    job-level `if:` counts: a step-level `if: always()` (a teardown) says nothing about the job.
    """
    pairs = []
    for job_id, job in workflow.items():
        body = job["body"]
        if "always()" in job["if"] or "toJSON(needs)" in body.replace(" ", ""):
            continue
        for dep in job["needs"]:
            if f"needs.{dep}." not in body:
                pairs.append((job_id, dep))
    return pairs


# --- report ------------------------------------------------------------------------------


def ts(value: str) -> float:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()


def p90(values: list[float]) -> float:
    ordered = sorted(values)
    return ordered[max(0, math.ceil(0.9 * len(ordered)) - 1)]


def summary(values: list[float]) -> dict:
    if not values:
        return {"n": 0, "median": None, "p90": None}
    return {"n": len(values), "median": statistics.median(values), "p90": p90(values)}


def load(directory: Path) -> tuple[list[dict], dict[int, list[dict]], list[dict]]:
    runs = json.loads((directory / "runs.json").read_text(encoding="utf-8"))
    jobs = {}
    for run in runs:
        all_attempts = json.loads((directory / "jobs" / f"{run['id']}.json").read_text(encoding="utf-8"))
        jobs[run["id"]] = [j for j in all_attempts if j.get("run_attempt", 1) == run.get("run_attempt", 1)]
    cache_file = directory / "caches.json"
    caches = json.loads(cache_file.read_text(encoding="utf-8")) if cache_file.exists() else []
    return runs, jobs, caches


def ran(job: dict) -> bool:
    return bool(job.get("started_at") and job.get("completed_at")) and job.get("conclusion") != "skipped"


def step_seconds(step: dict) -> float:
    if not step.get("started_at") or not step.get("completed_at"):
        return 0.0
    return max(0.0, ts(step["completed_at"]) - ts(step["started_at"]))


def job_phases(job: dict, setup: re.Pattern) -> dict:
    total = ts(job["completed_at"]) - ts(job["started_at"])
    setup_s = sum(step_seconds(s) for s in job.get("steps", []) if setup.search(s["name"]))
    return {
        "queue": max(0.0, ts(job["started_at"]) - ts(job["created_at"])),
        "setup": setup_s,
        "test": max(0.0, total - setup_s),
        "total": total,
    }


def critical_path(jobs: list[dict], workflow: dict[str, dict]) -> list[str]:
    """Walk back from the last job to finish, always through the dependency that finished last."""
    finished: dict[str, float] = {}
    for job in jobs:
        if not ran(job):
            continue
        job_id = job_id_for(job["name"], workflow)
        if job_id:
            finished[job_id] = max(finished.get(job_id, 0.0), ts(job["completed_at"]))
    if not finished:
        return []
    # The always() aggregator finishes last by construction; it is not where the time goes.
    gating = {j for j, w in workflow.items() if "toJSON(needs)" in w["body"].replace(" ", "")}
    candidates = {j: t for j, t in finished.items() if j not in gating} or finished
    node = max(candidates, key=candidates.get)
    path = [node]
    while True:
        deps = [d for d in workflow.get(node, {}).get("needs", []) if d in finished]
        if not deps:
            return list(reversed(path))
        node = max(deps, key=finished.get)
        path.append(node)


def stale_caches(caches: list[dict]) -> list[tuple[dict, str]]:
    """Caches nobody will restore again: superseded keys on the same ref, and PR-scoped refs."""
    flagged = []
    by_family: dict[tuple[str, str], list[dict]] = collections.defaultdict(list)
    for cache in caches:
        family = re.sub(r"-[0-9a-f]{8,}$", "", cache["key"])
        by_family[(cache["ref"], family)].append(cache)
    for group in by_family.values():
        group.sort(key=lambda c: c["last_accessed_at"] or "", reverse=True)
        for old in group[1:]:
            flagged.append((old, f"superseded by {group[0]['key']} on {old['ref']}"))
    seen = {id(c) for c, _ in flagged}
    for cache in caches:
        if id(cache) not in seen and cache["ref"].startswith("refs/pull/"):
            flagged.append((cache, "PR-scoped: only that pull request can restore it"))
    return flagged


def build_report(directory: Path, workflow_file: Path | None, setup_pattern: str, top: int) -> dict:
    runs, jobs_by_run, caches = load(directory)
    setup = re.compile(setup_pattern)
    workflow = parse_workflow(workflow_file.read_text(encoding="utf-8")) if workflow_file else {}
    ok = [r for r in runs if r["conclusion"] == "success"]
    walls, phases, steps, paths = [], collections.defaultdict(lambda: collections.defaultdict(list)), collections.defaultdict(list), []
    for run in ok:
        jobs = [j for j in jobs_by_run[run["id"]] if ran(j)]
        if not jobs:
            continue
        walls.append(max(ts(j["completed_at"]) for j in jobs) - ts(run["created_at"]))
        for job in jobs:
            for key, value in job_phases(job, setup).items():
                phases[job["name"]][key].append(value)
            for step in job.get("steps", []):
                steps[(job["name"], step["name"])].append(step_seconds(step))
        if workflow:
            paths.append(" -> ".join(critical_path(jobs_by_run[run["id"]], workflow)))
    job_rows = []
    for name, values in phases.items():
        job_rows.append({"job": name, "n": len(values["total"]), **{k: statistics.median(v) for k, v in values.items()}, "total_p90": p90(values["total"])})
    job_rows.sort(key=lambda r: r["total"], reverse=True)
    step_rows = sorted(
        ({"job": j, "step": s, "n": len(v), "median": statistics.median(v)} for (j, s), v in steps.items()),
        key=lambda r: r["median"],
        reverse=True,
    )[:top]
    path_counts = collections.Counter(paths)
    stale = stale_caches(caches)
    return {
        "runs": {"total": len(runs), "successful": len(ok), "conclusions": dict(collections.Counter(r["conclusion"] for r in runs))},
        "wall_clock_s": summary(walls),
        "jobs": job_rows,
        "steps": step_rows,
        "critical_path": {"known": bool(workflow), "paths": path_counts.most_common()},
        "dataless_needs": dataless_needs(workflow) if workflow else None,
        "caches": {
            "count": len(caches),
            "total_bytes": sum(c["size_in_bytes"] for c in caches),
            "stale": [{"key": c["key"], "ref": c["ref"], "bytes": c["size_in_bytes"], "reason": why} for c, why in stale],
            "stale_bytes": sum(c["size_in_bytes"] for c, _ in stale),
        },
    }


def fmt_s(value: float | None) -> str:
    return "-" if value is None else f"{value:.0f}s" if value < 120 else f"{value / 60:.1f}m"


def render(report: dict) -> str:
    out = []
    r = report["runs"]
    w = report["wall_clock_s"]
    out.append(f"runs: {r['total']} ({r['successful']} successful) {r['conclusions']}")
    out.append(f"wall clock (successful): median {fmt_s(w['median'])}, p90 {fmt_s(w['p90'])}, n={w['n']}")
    out.append("\n| job | n | queue | setup | test | total | total p90 |\n|---|---|---|---|---|---|---|")
    for j in report["jobs"]:
        out.append(f"| {j['job']} | {j['n']} | {fmt_s(j['queue'])} | {fmt_s(j['setup'])} | {fmt_s(j['test'])} | {fmt_s(j['total'])} | {fmt_s(j['total_p90'])} |")
    out.append("\n| slowest steps (median) | job | n |\n|---|---|---|")
    for s in report["steps"]:
        out.append(f"| {fmt_s(s['median'])} {s['step']} | {s['job']} | {s['n']} |")
    cp = report["critical_path"]
    if not cp["known"]:
        out.append("\ncritical path: needs graph unknown (pass --workflow-file)")
    else:
        out.append("\ncritical path (runs):")
        out.extend(f"  {count}x {path}" for path, count in cp["paths"])
        dataless = report["dataless_needs"] or []
        out.append("needs that pass no data: " + (", ".join(f"{a} <- {b}" for a, b in dataless) or "none"))
    c = report["caches"]
    out.append(f"\ncaches: {c['count']}, {c['total_bytes'] / 1e9:.2f} GB; stale candidates {len(c['stale'])}, {c['stale_bytes'] / 1e9:.2f} GB")
    out.extend(f"  {s['bytes'] / 1e9:.2f} GB {s['key']} ({s['reason']})" for s in c["stale"])
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    f = sub.add_parser("fetch")
    f.add_argument("--repo", required=True)
    f.add_argument("--workflow", required=True, help="workflow file name or id, e.g. ci.yml")
    f.add_argument("--out", required=True)
    f.add_argument("--limit", type=int, default=50)
    f.add_argument("--branch")
    f.add_argument("--before", help="only runs created before this ISO timestamp (freeze a baseline)")
    r = sub.add_parser("report")
    r.add_argument("directory")
    r.add_argument("--workflow-file", type=Path)
    r.add_argument("--setup-pattern", default=DEFAULT_SETUP_PATTERN)
    r.add_argument("--top", type=int, default=15)
    r.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    if args.command == "fetch":
        return fetch(args)
    report = build_report(Path(args.directory), args.workflow_file, args.setup_pattern, args.top)
    print(json.dumps(report, indent=1) if args.json else render(report))
    return 0


if __name__ == "__main__":
    sys.exit(main())
