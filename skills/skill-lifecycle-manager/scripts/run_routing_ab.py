#!/usr/bin/env python3
"""Cross-skill routing A/B gate for skill description changes.

Feeds each routing-suite case (an unlabeled user message) to a judge model that
sees the full standing skill list (name: description) and must answer with one
skill name or NONE. Runs the same cases against the baseline (on-disk)
descriptions and, when --overrides is given, a candidate variant, then reports
per-case regressions. Exit code 2 means at least one case that passed on the
baseline failed on the candidate.

The judge endpoint is OpenAI-compatible (POST <base-url>/chat/completions with
a bearer key). Judge verdicts are a relative discrimination check between two
description sets, not a prediction of any specific agent's trigger behavior.
"""

from __future__ import annotations

import argparse
import concurrent.futures as cf
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path


def parse_frontmatter_description(text: str) -> tuple[str, str] | None:
    """Return (name, description) from a SKILL.md, or None when the skill is
    user-invoked (disable-model-invocation) or has no parseable frontmatter."""
    match = re.match(r"^---\n(.*?)\n---", text, re.S)
    if not match:
        return None
    frontmatter = match.group(1)
    if re.search(r"^disable-model-invocation:\s*true\s*$", frontmatter, re.M):
        return None
    name_match = re.search(r"^name:\s*(\S+)", frontmatter, re.M)
    if not name_match:
        return None
    folded = re.search(r"^description:\s*>-?\s*\n((?:[ \t]+\S.*\n?)+)", frontmatter, re.M)
    if folded:
        description = " ".join(line.strip() for line in folded.group(1).splitlines())
    else:
        single = re.search(r"^description:\s*\"?(.+?)\"?\s*$", frontmatter, re.M)
        if not single:
            return None
        description = single.group(1)
    return name_match.group(1), description.strip()


def load_skills(skills_dir: Path) -> dict[str, str]:
    skills: dict[str, str] = {}
    for doc in sorted(skills_dir.glob("*/SKILL.md")):
        parsed = parse_frontmatter_description(doc.read_text(encoding="utf-8"))
        if parsed:
            skills[parsed[0]] = parsed[1]
    return skills


def build_system_prompt(skills: dict[str, str]) -> str:
    lines = "\n".join(f"- {name}: {desc}" for name, desc in sorted(skills.items()))
    return (
        "You are the skill router inside a coding agent. The agent has these skills installed:\n\n"
        + lines
        + "\n\nGiven the user's message, decide which single skill should auto-activate. "
        "Pick a skill only when the message clearly matches that skill's stated activation conditions. "
        "When no skill clearly matches, or the request is plain execution or a plain question, answer NONE. "
        "Respond with exactly one line: the skill name, or NONE."
    )


def parse_verdict(answer: str, names: set[str]) -> str:
    """Extract the routed skill from a judge answer; scan from the end so
    reasoning-model preambles that mention several names do not win."""
    tokens = re.findall(r"[a-z0-9][a-z0-9-]*", answer.lower())
    for token in reversed(tokens):
        if token in names:
            return token
        if token == "none":
            return "none"
    return f"unparsed:{answer[:60]!r}"


def gate(cases: list[dict], base: dict[str, str], cand: dict[str, str] | None) -> tuple[list[dict], int, int]:
    """Score baseline (and candidate) verdicts against expected routes.
    Returns (rows, regressions, newly_fixed)."""
    rows: list[dict] = []
    regressions = fixed = 0
    for case in cases:
        cid, expected = case["id"], case["expected_route"]
        forbidden = set(case.get("forbidden_routes", []))
        b = base[cid]
        row = {
            "id": cid,
            "expected": expected,
            "baseline": b,
            "baseline_pass": b == expected,
            "baseline_forbidden_hit": b in forbidden,
        }
        if cand is not None:
            c = cand[cid]
            row.update({
                "candidate": c,
                "candidate_pass": c == expected,
                "candidate_forbidden_hit": c in forbidden,
            })
            if row["baseline_pass"] and not row["candidate_pass"]:
                regressions += 1
                row["regression"] = True
            elif row["candidate_pass"] and not row["baseline_pass"]:
                fixed += 1
        rows.append(row)
    return rows, regressions, fixed


def call_judge(base_url: str, key: str, model: str, system: str, user: str,
               max_tokens: int = 4096, timeout: int = 180, attempts: int = 4) -> str:
    request = urllib.request.Request(
        base_url.rstrip("/") + "/chat/completions",
        data=json.dumps({
            "model": model,
            "temperature": 0,
            "max_tokens": max_tokens,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        }).encode("utf-8"),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
    )
    last: Exception = RuntimeError("no attempt made")
    for _ in range(attempts):
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                data = json.loads(response.read())
            message = data["choices"][0]["message"]
            answer = (message.get("content") or "").strip()
            if not answer:
                # reasoning models sometimes burn the budget on reasoning_content
                answer = (message.get("reasoning_content") or "").strip()
            if answer:
                return answer
            last = RuntimeError("empty content and reasoning_content")
        except (urllib.error.URLError, TimeoutError, KeyError) as error:
            last = error
    raise last


def run_variant(label: str, skills: dict[str, str], cases: list[dict],
                base_url: str, key: str, model: str, workers: int) -> dict[str, str]:
    system = build_system_prompt(skills)
    names = set(skills)

    def one(case: dict) -> tuple[str, str]:
        answer = call_judge(base_url, key, model, system, case["prompt"])
        return case["id"], parse_verdict(answer, names)

    results: dict[str, str] = {}
    with cf.ThreadPoolExecutor(max_workers=workers) as pool:
        for cid, verdict in pool.map(one, cases):
            results[cid] = verdict
    print(f"[{label}] done: {len(results)} cases", file=sys.stderr)
    return results


def main(argv: list[str] | None = None) -> int:
    package_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description="Cross-skill routing A/B gate")
    parser.add_argument("--suite", default=str(package_root / "eval" / "cross-skill-routing-cases.json"),
                        help="Routing suite JSON (default: %(default)s)")
    parser.add_argument("--skills-dir", default=str(package_root.parent),
                        help="Directory containing skill packages (default: %(default)s)")
    parser.add_argument("--overrides", default=None,
                        help="JSON file mapping skill name -> candidate description")
    parser.add_argument("--model", default=os.environ.get("ROUTING_AB_MODEL"),
                        help="Judge model id (default: env ROUTING_AB_MODEL)")
    parser.add_argument("--base-url", default=os.environ.get("ROUTING_AB_BASE_URL", "https://www.dmxapi.cn/v1"),
                        help="OpenAI-compatible endpoint base (default: env ROUTING_AB_BASE_URL or %(default)s)")
    parser.add_argument("--key-env", default="DMXAPI_KEY",
                        help="Environment variable holding the bearer key (default: %(default)s)")
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--out", default=None, help="Optional path for the per-case results JSON")
    args = parser.parse_args(argv)

    if not args.model:
        parser.error("--model is required (or set ROUTING_AB_MODEL)")
    key = os.environ.get(args.key_env, "").strip()
    if not key:
        parser.error(f"environment variable {args.key_env} is empty; export the judge endpoint key first")

    suite = json.loads(Path(args.suite).read_text(encoding="utf-8"))
    cases = suite["cases"]
    baseline = load_skills(Path(args.skills_dir))

    candidate = None
    if args.overrides:
        overrides = json.loads(Path(args.overrides).read_text(encoding="utf-8"))
        unknown = [name for name in overrides if name not in baseline]
        if unknown:
            parser.error(f"overrides for unknown or user-invoked skills: {unknown}")
        candidate = {**baseline, **overrides}

    base_results = run_variant("baseline", baseline, cases, args.base_url, key, args.model, args.workers)
    cand_results = (run_variant("candidate", candidate, cases, args.base_url, key, args.model, args.workers)
                    if candidate else None)

    rows, regressions, fixed = gate(cases, base_results, cand_results)
    base_total = sum(row["baseline_pass"] for row in rows)
    print(f"\nbaseline: {base_total}/{len(rows)} pass")
    if candidate:
        cand_total = sum(row["candidate_pass"] for row in rows)
        print(f"candidate: {cand_total}/{len(rows)} pass | regressions={regressions} newly-fixed={fixed}")
    for row in rows:
        mark = " <-- REGRESSION" if row.get("regression") else ""
        cand_part = f" | cand={row.get('candidate', '-'):<28}" if candidate else ""
        print(f"{row['id']:<28} exp={row['expected']:<26} base={row['baseline']:<28}{cand_part}{mark}")

    if args.out:
        Path(args.out).write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"results -> {args.out}")
    return 2 if (candidate and regressions) else 0


if __name__ == "__main__":
    sys.exit(main())
