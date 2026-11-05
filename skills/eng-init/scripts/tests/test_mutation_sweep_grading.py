"""Grading of mutation_sweep.py suite outcomes.

pytest reports more than "passed" and "failed": 2 = interrupted/collection
error, 3 = internal error, 4 = usage error, 5 = no tests collected. The sweep
read every non-zero code as "a test detected the mutant", so a mutation that
stopped collection was counted as killed and the sweep exited 0 claiming proof
it did not have. Cherry-picked from upstream harness-init 4.4.2.
"""

import importlib.util
import sys
from pathlib import Path

import pytest

SKILL = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("mutation_sweep", SKILL / "scripts" / "mutation_sweep.py")
sweep = importlib.util.module_from_spec(_spec)
sys.modules["mutation_sweep"] = sweep
_spec.loader.exec_module(sweep)


@pytest.mark.parametrize("code,expected", [
    (0, "green"),
    (1, "caught"),
    (2, "unmeasured"),
    (3, "unmeasured"),
    (4, "unmeasured"),
    (5, "unmeasured"),
])
def test_suite_outcome_classification(code, expected):
    assert sweep.classify_suite(code) == expected
