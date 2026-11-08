"""Tests for scripts/ci-gate.py, and the pins that keep it in step with .github/workflows/ci.yml.

Template from the ci-speedup skill: copy next to the repository's other tests and fix ROOT.
The pins are the point. A job renamed in ci.yml but not in ci-gate.py must fail here, not in a
pull request that silently skips it.
"""

import importlib.util
import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / '.github' / 'workflows' / 'ci.yml'
_spec = importlib.util.spec_from_file_location('ci_gate', ROOT / 'scripts' / 'ci-gate.py')
gate = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gate)


def jobs(text: str) -> dict[str, str]:
    """Job id -> body for the two-space-indented jobs block."""
    block = text.split('\njobs:\n', 1)[1]
    found = re.split(r'(?m)^  ([A-Za-z0-9_-]+):\s*$', block)
    return dict(zip(found[1::2], found[2::2]))


WORKFLOW_JOBS = jobs(WORKFLOW.read_text(encoding='utf-8'))
AGGREGATOR = next(body for body in WORKFLOW_JOBS.values() if 'ci-gate.py verdict' in body)


def job_if(body: str) -> str:
    match = re.search(r'(?m)^    if:\s*(.+)$', body)
    return match.group(1) if match else ''


def test_required_jobs_are_exactly_the_aggregator_needs():
    needs = re.findall(r'(?m)^      - ([A-Za-z0-9_-]+)\s*$', AGGREGATOR.split('steps:', 1)[0])
    assert sorted(needs) == sorted(gate.REQUIRED_JOBS)


def test_code_jobs_are_exactly_the_jobs_gated_on_the_classification():
    gated = [j for j, body in WORKFLOW_JOBS.items() if 'needs.changes.outputs.code' in job_if(body)]
    assert sorted(gated) == sorted(gate.CODE_JOBS)


def test_pr_only_jobs_are_exactly_the_jobs_gated_on_pull_request():
    gated = [j for j, body in WORKFLOW_JOBS.items() if "github.event_name == 'pull_request'" in job_if(body)]
    assert sorted(gated) == sorted(gate.PR_ONLY_JOBS)


def all_pass(**overrides):
    needs = {job: {'result': 'success'} for job in gate.REQUIRED_JOBS}
    needs.update({job: {'result': result} for job, result in overrides.items()})
    return needs


def test_everything_green_passes():
    assert gate.failures(all_pass(), 'pull_request', 'true') == []


@pytest.mark.parametrize('result', ['failure', 'cancelled', 'skipped'])
def test_any_other_outcome_of_a_code_job_fails_on_a_code_pr(result):
    job = gate.CODE_JOBS[0]
    assert gate.failures(all_pass(**{job: result}), 'pull_request', 'true') == [f'{job}: {result}']


def test_code_jobs_may_skip_only_on_a_docs_only_pr():
    skipped = {job: 'skipped' for job in gate.CODE_JOBS}
    assert gate.failures(all_pass(**skipped), 'pull_request', 'false') == []
    assert gate.failures(all_pass(**skipped), 'push', 'false') != []


def test_pr_only_jobs_may_skip_only_on_push():
    skipped = {job: 'skipped' for job in gate.PR_ONLY_JOBS}
    assert gate.failures(all_pass(**skipped), 'push', 'true') == []
    assert gate.failures(all_pass(**skipped), 'pull_request', 'true') != []


def test_a_job_that_is_neither_may_never_skip():
    others = [j for j in gate.REQUIRED_JOBS if j not in gate.CODE_JOBS + gate.PR_ONLY_JOBS]
    for job in others:
        assert gate.failures(all_pass(**{job: 'skipped'}), 'pull_request', 'false') == [f'{job}: skipped']


@pytest.mark.parametrize('code', ['', 'maybe', 'True'])
def test_a_missing_or_garbled_classification_fails(code):
    assert gate.failures(all_pass(), 'pull_request', code)


def test_unknown_and_missing_jobs_fail():
    needs = all_pass()
    needs['surprise'] = {'result': 'success'}
    del needs[gate.REQUIRED_JOBS[-1]]
    bad = gate.failures(needs, 'pull_request', 'true')
    assert 'surprise: not a known required job' in bad
    assert f'{gate.REQUIRED_JOBS[-1]}: missing from needs' in bad


def rows(*paths):
    return ''.join(f'{p}\t{old}\n' for p, old in paths)


def test_docs_only_listing_skips_code():
    listing = rows(('docs/guide.md', ''), ('README.md', ''))
    assert gate.classify(listing, 2) is False


@pytest.mark.parametrize(
    'listing, count',
    [
        (rows(('docs/guide.md', ''), ('src/app.py', '')), 2),  # any code path
        (rows(('docs/moved.md', 'src/app.py')), 1),  # a rename counts its old path
        (rows(('src/README.md', '')), 1),  # Markdown under a code directory
        (rows((gate.CODE_FILES[0], '')), 1) if gate.CODE_FILES else (rows(('a.py', '')), 1),  # runtime-read Markdown
        ('', 0),  # empty listing
        (rows(('docs/guide.md', '')), 2),  # truncated listing
        (rows(('docs/guide.md', '')) * gate.FILES_API_LIMIT, gate.FILES_API_LIMIT),  # API cap
    ],
)
def test_classification_fails_closed(listing, count):
    assert gate.classify(listing, count) is True


def test_command_line_contract(monkeypatch, capsys):
    monkeypatch.setenv('NEEDS', json.dumps(all_pass()))
    monkeypatch.setenv('EVENT', 'pull_request')
    monkeypatch.setenv('CODE', 'true')
    assert gate.main(['verdict']) == 0
    monkeypatch.delenv('CODE')
    assert gate.main(['verdict']) == 2
    assert gate.main(['classify', '--expected-files', 'x']) == 2
    assert gate.main(['nonsense']) == 2
