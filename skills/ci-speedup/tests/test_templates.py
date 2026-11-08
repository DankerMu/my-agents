"""The templates run together: ci-gate.py, its pinning tests, and the workflow it pins."""

import shutil
import subprocess
import sys

from conftest import SKILL, load

TEMPLATES = SKILL / "templates"


def adopt(tmp_path, workflow_text=None):
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    (repo / "tests").mkdir()
    (repo / ".github" / "workflows").mkdir(parents=True)
    shutil.copy(TEMPLATES / "ci-gate.py", repo / "scripts" / "ci-gate.py")
    shutil.copy(TEMPLATES / "test_ci_gate.py", repo / "tests" / "test_ci_gate.py")
    text = workflow_text if workflow_text is not None else (TEMPLATES / "ci-docs-only.yml").read_text(encoding="utf-8")
    (repo / ".github" / "workflows" / "ci.yml").write_text(text, encoding="utf-8")
    return repo


def pytest_in(repo):
    return subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", str(repo / "tests")],
                          capture_output=True, text=True, cwd=repo)


def test_adopted_templates_pass_their_own_tests(tmp_path):
    result = pytest_in(adopt(tmp_path))
    assert result.returncode == 0, result.stdout + result.stderr


def test_renaming_a_job_in_the_workflow_fails_the_pins(tmp_path):
    text = (TEMPLATES / "ci-docs-only.yml").read_text(encoding="utf-8").replace("  unit-tests:\n", "  unit-test:\n").replace(
        "      - unit-tests\n", "      - unit-test\n")
    result = pytest_in(adopt(tmp_path, text))
    assert result.returncode != 0
    assert "test_required_jobs_are_exactly_the_aggregator_needs" in result.stdout


def test_workflow_template_satisfies_the_eng_init_aggregator_shape():
    text = (TEMPLATES / "ci-docs-only.yml").read_text(encoding="utf-8")
    assert "if: always()" in text and "toJSON(needs)" in text and "scripts/ci-gate.py verdict" in text
    assert "cancel-in-progress: ${{ github.ref != 'refs/heads/main' }}" in text
    assert "paths:" not in text and "paths-ignore:" not in text


def test_gate_template_mentions_skipped_for_the_render_check():
    # eng-init's check_rendered_harness.py accepts a delegated verdict only if the script names `skipped`.
    assert "skipped" in (TEMPLATES / "ci-gate.py").read_text(encoding="utf-8")
    gate = load("ci_gate_template", TEMPLATES / "ci-gate.py")
    assert set(gate.CODE_JOBS) <= set(gate.REQUIRED_JOBS) and set(gate.PR_ONLY_JOBS) <= set(gate.REQUIRED_JOBS)
