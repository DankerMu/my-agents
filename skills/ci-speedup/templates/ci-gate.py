#!/usr/bin/env python3
"""CI gate decisions for .github/workflows/ci.yml. Standard library only: the jobs that run it have no venv.

usage:
  ci-gate.py classify --expected-files N   stdin: one '<path>\\t<previous path or empty>' row per PR file
                                            prints 'code=true' or 'code=false' for $GITHUB_OUTPUT
  ci-gate.py verdict                       env NEEDS (the needs context as JSON), EVENT, CODE
                                            exits 1 naming every required job that did not pass
Any other command line exits 2.

Template from the ci-speedup skill. Before adopting it, replace every value in the CONFIG block
with this repository's facts, and keep tests/test_ci_gate.py pinning the job sets to ci.yml.
"""

from __future__ import annotations

import json
import os
import sys

# --- CONFIG: this repository's facts --------------------------------------------------------
# Every job `All checks passed` needs. A job missing here or there fails the verdict.
REQUIRED_JOBS = (
    'changes',
    'fast-checks',
    'unit-tests',
    'browser',
    'secret-scan',
    'diff-size-guard',
)
# Skipped by design on push events (they read pull-request data).
PR_ONLY_JOBS = ('diff-size-guard',)
# Skipped by design on a documentation-only pull request. Never list a job that checks docs.
CODE_JOBS = ('unit-tests', 'browser')
# Paths that are documentation. Anything not matched here is code.
DOC_DIRECTORIES = ('docs/',)
DOC_TOP_LEVEL_SUFFIXES = ('.md',)
# Documentation-looking files that something reads at runtime or ships: they are code.
# Find them before adopting: grep the code for every Markdown file name it opens or packages.
CODE_FILES = ('CHANGELOG.md',)
# The pull request files API stops at 3000 entries.
FILES_API_LIMIT = 3000
# --- end CONFIG -------------------------------------------------------------------------------


def is_docs(path: str) -> bool:
    if path in CODE_FILES:
        return False
    if path.startswith(DOC_DIRECTORIES):
        return True
    # Only top-level files: a .md under a code directory may be read by that code.
    return '/' not in path and path.endswith(DOC_TOP_LEVEL_SUFFIXES)


def classify(listing: str, expected_files: int) -> bool:
    """True when the code jobs must run. Fails closed: any doubt runs everything."""
    rows = [line.split('\t') for line in listing.splitlines() if line]
    # Empty, truncated or mismatched listings are never docs-only.
    if not rows or len(rows) != expected_files or expected_files >= FILES_API_LIMIT:
        return True
    # A rename counts its old path too: moving code into docs/ is still a code change.
    paths = [path for row in rows for path in row if path]
    return not all(is_docs(path) for path in paths)


def failures(needs: dict, event: str, code: str) -> list[str]:
    """Every required job that did not pass. GitHub counts a skipped required check as passing,
    so a skip passes only by design: a PR-only job on push, a code job on a docs-only PR."""
    bad = []
    if code not in ('true', 'false'):
        bad.append(f'changes: classification output is {code!r}, expected true or false')
    bad.extend(f'{job}: not a known required job' for job in needs if job not in REQUIRED_JOBS)
    for job in REQUIRED_JOBS:
        if job not in needs:
            bad.append(f'{job}: missing from needs')
            continue
        result = needs[job].get('result')
        if result == 'success':
            continue
        if result == 'skipped':
            if job in PR_ONLY_JOBS and event != 'pull_request':
                continue
            if job in CODE_JOBS and event == 'pull_request' and code == 'false':
                continue
        bad.append(f'{job}: {result}')
    return bad


def usage(message: str) -> int:
    sys.stderr.write(f'ci-gate: {message}\n')
    return 2


def main(argv: list[str]) -> int:
    if len(argv) == 3 and argv[0] == 'classify' and argv[1] == '--expected-files':
        if not argv[2].isdigit():
            return usage(f'--expected-files must be a non-negative integer, got {argv[2]!r}')
        code = classify(sys.stdin.read(), int(argv[2]))
        sys.stdout.write(f'code={"true" if code else "false"}\n')
        return 0
    if argv == ['verdict']:
        try:
            needs = json.loads(os.environ['NEEDS'])
            event, code = os.environ['EVENT'], os.environ['CODE']
        except (KeyError, json.JSONDecodeError) as error:
            return usage(f'verdict needs NEEDS (JSON), EVENT and CODE: {error!r}')
        bad = failures(needs, event, code)
        for line in bad:
            sys.stdout.write(f'::error::{line}\n')
        return 1 if bad else 0
    return usage(f'unknown command line {argv!r}')


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
