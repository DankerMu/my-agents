from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from _loader import load_script_module


validate_eval_suite = load_script_module("validate_eval_suite")


def routing_case(
    case_id: str,
    expected_route: str,
    forbidden_routes: list[str],
    prompt: str,
) -> dict:
    return {
        "id": case_id,
        "name": case_id,
        "prompt": prompt,
        "expected_route": expected_route,
        "forbidden_routes": forbidden_routes,
        "allowed_followups": [],
        "expected_depth": "light" if expected_route != "none" else "none",
        "rationale": "Exercise an adjacent routing boundary without naming the target skill.",
    }


def valid_payload() -> dict:
    return {
        "type": "cross-skill-routing",
        "suite": "demo-routing",
        "skills": ["clarify", "brainstorming"],
        "cases": [
            routing_case("clarify-1", "clarify", ["brainstorming"], "Resolve conflicting API constraints."),
            routing_case("clarify-2", "clarify", ["brainstorming"], "Resolve missing acceptance criteria."),
            routing_case("brainstorm-1", "brainstorming", ["clarify"], "Explore competing product directions."),
            routing_case("brainstorm-2", "brainstorming", ["clarify"], "Compare several possible approaches."),
            routing_case("none-1", "none", ["clarify"], "Fix one explicit null check."),
            routing_case("none-2", "none", ["brainstorming"], "Summarize this completed test output."),
        ],
    }


class ValidateEvalSuiteTests(unittest.TestCase):
    def test_cross_skill_routing_format_accepts_balanced_unlabeled_suite(self) -> None:
        errors, warnings = validate_eval_suite.validate_cross_skill_routing_format(valid_payload())

        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])

    def test_cross_skill_routing_format_rejects_labeled_prompt_and_missing_coverage(self) -> None:
        payload = valid_payload()
        payload["cases"] = [
            routing_case(
                "labeled",
                "clarify",
                ["brainstorming"],
                "Use clarify to resolve these constraints.",
            )
        ]

        errors, _ = validate_eval_suite.validate_cross_skill_routing_format(payload)

        self.assertTrue(any("prompt names target candidate" in error for error in errors))
        self.assertTrue(any("needs at least two positive routing cases" in error for error in errors))

    def test_validate_eval_suite_dispatches_cross_skill_format(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            eval_path = Path(tmp) / "routing.json"
            eval_path.write_text(json.dumps(valid_payload()), encoding="utf8")

            errors, warnings = validate_eval_suite.validate_eval_suite(eval_path)

            self.assertEqual(errors, [])
            self.assertEqual(warnings, [])

    def test_canonical_workflow_routing_suite_is_valid(self) -> None:
        repo_root = Path(__file__).resolve().parents[3]
        eval_path = repo_root / "eval" / "routing" / "workflow-stage-routing.json"

        errors, warnings = validate_eval_suite.validate_eval_suite(eval_path)

        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])


if __name__ == "__main__":
    unittest.main()
