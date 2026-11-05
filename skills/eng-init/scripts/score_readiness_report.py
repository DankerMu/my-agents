#!/usr/bin/env python3
"""Validate and rescore an eng-init readiness report JSON file."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import math
import posixpath
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gate_output import report as gate_report  # noqa: E402  (aliased: local `report` holds the parsed JSON)


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


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


STATUSES = {"passing", "failing", "partial", "skipped", "pending_external"}

# Scoring-model bands from agent-readiness-criteria.md § Scoring model: L1 0–20,
# L2 20–40, L3 40–60, L4 60–79, L5 80–100. The ranges touch at their lower end,
# so a value on a boundary belongs to the higher band (80% is Level 5, not 4);
# the top of the scale is inclusive.
LEVEL_RE = re.compile(r"^(?:Level[ _]?|L)([1-5])$", re.IGNORECASE)
LEVEL_BANDS = {1: (0.0, 0.2), 2: (0.2, 0.4), 3: (0.4, 0.6), 4: (0.6, 0.8), 5: (0.8, 1.0)}


def level_matches(average: float, declared: object) -> tuple[bool, str]:
    """(ok, message) for a declared `score.level` against the computed average."""
    match = LEVEL_RE.match(declared) if isinstance(declared, str) else None
    if match is None:
        return False, "score.level must be L1..L5 or Level 1..Level 5"
    number = int(match.group(1))
    low, high = LEVEL_BANDS[number]
    last = number == 5
    if low - 1e-9 <= average and (average < high - 1e-9 or (last and average <= high + 1e-9)):
        return True, ""
    return False, (f"score.level {declared!r} does not match average {average:.6f}; "
                   "the scoring bands place it in a different level")


def _finite_number(value: object) -> bool:
    # type(), not isinstance(): bool is an int subclass, and `true` must not
    # count as a numerator of 1.
    return type(value) in (int, float) and math.isfinite(value)


def score(report: dict, registry: dict[str, dict[str, str]]) -> tuple[float, list[str]]:
    errors: list[str] = []
    if not isinstance(report, dict):
        return 0.0, ["report must be an object"]
    if not registry:
        return 0.0, ["registry must contain at least one criterion"]
    configured = report.get("configured_but_not_blocking", [])
    if not isinstance(configured, list) or not all(isinstance(cid, str) for cid in configured):
        errors.append("configured_but_not_blocking must be a list of criterion ids")
        configured = []
    require(len(configured) == len(set(configured)), "configured_but_not_blocking ids must be unique", errors)
    apps = report.get("applications")
    require(isinstance(apps, list) and len(apps) >= 1, "applications must be a non-empty list", errors)
    app_count = len(apps) if isinstance(apps, list) else 0
    score_block = report.get("score", {})
    if not isinstance(score_block, dict):
        return 0.0, errors + ["score must be an object"]
    require(score_block.get("applications_identified") == app_count, "score.applications_identified must equal len(applications)", errors)
    criteria = report.get("criteria")
    require(isinstance(criteria, list), "criteria must be a list", errors)
    values: list[float] = []
    # Stop after recording the shape error rather than iterating a non-list: a
    # dict yields its keys and the row loop dies on `row.get`, turning a reported
    # violation into a traceback that loses every other finding. A gate reports;
    # it does not crash.
    if not isinstance(criteria, list):
        return 0.0, errors
    for index, row in enumerate(criteria, start=1):
        if not isinstance(row, dict):
            require(False, f"criteria[{index}] must be an object, got {type(row).__name__}", errors)
            continue
        cid = row.get("id")
        meta = registry.get(cid) if isinstance(cid, str) else None
        require(meta is not None, f"criteria[{index}] unknown id {cid!r}", errors)
        denominator = row.get("denominator")
        numerator = row.get("numerator")
        status = row.get("status")
        if not isinstance(status, str) or status not in STATUSES:
            errors.append(f"{cid}: unknown status {status!r}")
            status = "invalid"
        if meta is not None:
            if "scope" in row:
                require(row["scope"] == meta.get("scope"), f"{cid}: scope must match registry", errors)
            expected_denominator = 1 if meta.get("scope") == "repository" else app_count
            require(denominator == expected_denominator, f"{cid}: denominator {denominator!r} must be {expected_denominator}", errors)
            if numerator is None:
                require(meta.get("skippable") == "true" and status == "skipped", f"{cid}: null numerator requires skippable=true and skipped status", errors)
            else:
                require(_finite_number(numerator), f"{cid}: numerator must be number or null", errors)
                require(type(denominator) is int and denominator >= 1, f"{cid}: denominator must be positive integer", errors)
                if _finite_number(numerator) and type(denominator) is int and denominator >= 1:
                    require(0 <= numerator <= denominator, f"{cid}: numerator out of range", errors)
                    frac = float(numerator) / float(denominator)
                    values.append(frac)
                    # The status is a claim about the credit; a row cannot say
                    # "passing" with zero credit or "failing" with full credit.
                    if frac == 0:
                        require(status in {"failing", "pending_external"},
                                f"{cid}: zero credit requires failing or pending_external status", errors)
                    elif frac == 1:
                        require(status == "passing", f"{cid}: full credit requires passing status", errors)
                    elif 0 < frac < 1:
                        require(status == "partial",
                                f"{cid}: partial credit must have partial status, not {status}", errors)
        require(row.get("evidence"), f"{cid}: evidence is required", errors)
        require(row.get("validator"), f"{cid}: validator is required", errors)
        require(row.get("rescore_rule"), f"{cid}: rescore_rule is required", errors)
        if status in {"failing", "partial", "pending_external"}:
            # agent-readiness-criteria.md honesty rules: every non-passing row
            # names what was checked. The schema field is the machine form.
            locs = row.get("evidence_locations")
            require(isinstance(locs, list) and len(locs) >= 1, f"{cid}: evidence_locations is required on {status} rows", errors)
            if isinstance(locs, list):
                require(all(isinstance(loc, str) and loc for loc in locs), f"{cid}: evidence_locations entries must be non-empty strings", errors)
    computed = sum(values) / len(values) if values else 0.0
    reported = score_block.get("average")
    require(_finite_number(reported), "score.average must be numeric", errors)
    if _finite_number(reported):
        require(math.isclose(computed, float(reported), rel_tol=0.0, abs_tol=0.0001), f"score.average {reported!r} does not match computed {computed:.6f}", errors)
    if "level" in score_block:
        # Presence and type are the wire schema's job; this checks the claim
        # against the computed average so a 0.0 report cannot advertise Level 5.
        level_ok, level_error = level_matches(computed, score_block.get("level"))
        require(level_ok, level_error, errors)
    for cid in configured:
        rows = [row for row in criteria if isinstance(row, dict) and row.get("id") == cid]
        require(bool(rows), f"configured_but_not_blocking id {cid!r} missing from criteria", errors)
        for row in rows:
            require(row.get("status") == "partial", f"{cid}: configured-but-not-blocking rows must be partial", errors)
    return computed, errors


_RFC3339_DATE_TIME = re.compile(
    r"([0-9]{4}-[0-9]{2}-[0-9]{2})[Tt ]([0-9]{2}:[0-9]{2}):([0-9]{2})"
    r"(?:\.([0-9]+))?([Zz]|[+-][0-9]{2}:[0-9]{2})")

# IERS positive leap seconds: https://hpiers.obspm.fr/iers/bul/bulc/Leap_Second.dat
# Each increase after the initial 1972-01-01 entry applies at the end of the
# preceding UTC day; 2016-12-31 is the last one announced.
_UTC_LEAP_SECOND_DATES = frozenset({
    "1972-06-30", "1972-12-31", "1973-12-31", "1974-12-31", "1975-12-31",
    "1976-12-31", "1977-12-31", "1978-12-31", "1979-12-31", "1981-06-30",
    "1982-06-30", "1983-06-30", "1985-06-30", "1987-12-31", "1989-12-31",
    "1990-12-31", "1992-06-30", "1993-06-30", "1994-06-30", "1995-12-31",
    "1997-06-30", "1998-12-31", "2005-12-31", "2008-12-31", "2012-06-30",
    "2015-06-30", "2016-12-31",
})


def is_rfc3339_date_time(value: object) -> bool:
    """RFC 3339 date-time check for the schema's `format: date-time`.

    jsonschema's FormatChecker checks date-time only when the optional
    rfc3339-validator package is installed and otherwise accepts any string,
    so the scorer carries the check itself. Non-strings are left to `type`.
    """
    if not isinstance(value, str):
        return True
    match = _RFC3339_DATE_TIME.fullmatch(value)
    if not match:
        return False
    date, hour_minute, second, fraction, offset = match.groups()
    if int(hour_minute[:2]) > 23:  # datetime reads 24:00 as the next midnight.
        return False
    if offset not in ("Z", "z") and (int(offset[1:3]) > 23 or int(offset[4:6]) > 59):
        return False
    leap_second = second == "60"
    if leap_second:  # datetime cannot represent second 60.
        second = "59"
    fraction = ((fraction or "") + "000000")[:6]
    offset = "+00:00" if offset in ("Z", "z") else offset
    try:
        parsed = datetime.fromisoformat(f"{date}T{hour_minute}:{second}.{fraction}{offset}")
        if leap_second:
            utc = parsed.astimezone(timezone.utc)
            return (utc.hour == 23 and utc.minute == 59
                    and utc.date().isoformat() in _UTC_LEAP_SECOND_DATES)
    except (ValueError, OverflowError):
        return False
    return True


def validate_schema(report: object) -> list[str]:
    """Validate the versioned wire contract before any semantic computation.

    score() is the lower-level semantic calculator; CLI callers cannot bypass
    this schema boundary. A missing validation dependency fails closed: a gate
    that could not run has not passed.
    """
    try:
        from jsonschema import Draft202012Validator, FormatChecker
    except ImportError:
        return ["schema validation unavailable: run through `uv run --with jsonschema` (see SKILL.md reference index)"]
    schema_path = Path(__file__).resolve().parents[1] / "references/readiness-report-schema.json"
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        format_checker = FormatChecker()
        format_checker.checks("date-time")(is_rfc3339_date_time)
        validator = Draft202012Validator(schema, format_checker=format_checker)
        return [f"schema {'.'.join(map(str, error.absolute_path)) or '$'}: {error.message}"
                for error in sorted(validator.iter_errors(report),
                                    key=lambda e: str(list(e.absolute_path)))]
    except (OSError, ValueError) as exc:
        return [f"schema validation unavailable: {exc}"]


def _unique_object(pairs: list[tuple[str, object]]) -> dict:
    # json.loads keeps the last duplicate silently; a report that says a thing
    # twice says nothing reliable, so a duplicate key is rejected outright.
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise ValueError(f"non-finite JSON number is forbidden: {value}")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Validate and rescore eng-init readiness report JSON")
    parser.add_argument("report")
    parser.add_argument("--registry", default=str(Path(__file__).resolve().parents[1] / "references/readiness-registry.yaml"))
    args = parser.parse_args(argv[1:])

    try:
        report = json.loads(Path(args.report).read_text(encoding="utf-8"),
                            parse_constant=_reject_constant, object_pairs_hook=_unique_object)
        registry = parse_registry(Path(args.registry))
    except (OSError, UnicodeError, ValueError, RecursionError) as exc:
        return gate_report("score-readiness-report", [f"input could not be validated: {exc}"], "")
    errors = validate_schema(report)
    if errors:
        return gate_report("score-readiness-report", errors, "")
    app_paths = [posixpath.normpath(app["path"]) for app in report["applications"]]
    if len(set(app_paths)) != len(app_paths):
        return gate_report("score-readiness-report", ["duplicate application paths after normalization"], "")
    computed, errors = score(report, registry)
    if errors:
        return gate_report("score-readiness-report", errors, "")
    print(f"score: {computed:.6f}")
    print(f"criteria: {len(report.get('criteria', []))}")
    print(f"applications_identified: {len(report.get('applications', []))}")
    return gate_report("score-readiness-report", [],
                       f"{len(report.get('criteria', []))} criteria scored, all conform")


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
