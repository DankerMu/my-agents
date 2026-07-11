from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from _loader import load_script_module


run_routing_ab = load_script_module("run_routing_ab")


class ParseVerdictTests(unittest.TestCase):
    NAMES = {"review", "clarify", "brainstorming"}

    def test_plain_name(self) -> None:
        self.assertEqual(run_routing_ab.parse_verdict("review", self.NAMES), "review")

    def test_none_answer(self) -> None:
        self.assertEqual(run_routing_ab.parse_verdict("NONE", self.NAMES), "none")

    def test_reasoning_preamble_last_token_wins(self) -> None:
        answer = "This could be clarify or brainstorming, but the final answer is: review"
        self.assertEqual(run_routing_ab.parse_verdict(answer, self.NAMES), "review")

    def test_unparsed_answer(self) -> None:
        verdict = run_routing_ab.parse_verdict("no idea at all", self.NAMES)
        self.assertTrue(verdict.startswith("unparsed:"))


class FrontmatterParsingTests(unittest.TestCase):
    def test_folded_description(self) -> None:
        text = "---\nname: demo\ndescription: >\n  First line\n  second line.\nversion: 0.1.0\n---\n\n# Demo\n"
        self.assertEqual(
            run_routing_ab.parse_frontmatter_description(text),
            ("demo", "First line second line."),
        )

    def test_single_line_description(self) -> None:
        text = '---\nname: demo\ndescription: "One line only."\nversion: 0.1.0\n---\n'
        self.assertEqual(
            run_routing_ab.parse_frontmatter_description(text),
            ("demo", "One line only."),
        )

    def test_user_invoked_skill_is_excluded(self) -> None:
        text = "---\nname: demo\ndescription: >\n  Hidden.\ndisable-model-invocation: true\nversion: 0.1.0\n---\n"
        self.assertIsNone(run_routing_ab.parse_frontmatter_description(text))

    def test_load_skills_scans_packages(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "alpha").mkdir()
            (root / "alpha" / "SKILL.md").write_text(
                "---\nname: alpha\ndescription: >\n  Alpha skill.\nversion: 0.1.0\n---\n", encoding="utf-8"
            )
            (root / "hidden").mkdir()
            (root / "hidden" / "SKILL.md").write_text(
                "---\nname: hidden\ndescription: >\n  Hidden.\ndisable-model-invocation: true\nversion: 0.1.0\n---\n",
                encoding="utf-8",
            )
            self.assertEqual(run_routing_ab.load_skills(root), {"alpha": "Alpha skill."})


class GateTests(unittest.TestCase):
    CASES = [
        {"id": "a", "expected_route": "review", "forbidden_routes": ["clarify"]},
        {"id": "b", "expected_route": "none", "forbidden_routes": ["review"]},
    ]

    def test_regression_detected(self) -> None:
        rows, regressions, fixed = run_routing_ab.gate(
            self.CASES,
            {"a": "review", "b": "none"},
            {"a": "clarify", "b": "none"},
        )
        self.assertEqual(regressions, 1)
        self.assertEqual(fixed, 0)
        self.assertTrue(rows[0]["regression"])
        self.assertTrue(rows[0]["candidate_forbidden_hit"])

    def test_newly_fixed_counted(self) -> None:
        rows, regressions, fixed = run_routing_ab.gate(
            self.CASES,
            {"a": "review", "b": "review"},
            {"a": "review", "b": "none"},
        )
        self.assertEqual(regressions, 0)
        self.assertEqual(fixed, 1)
        self.assertTrue(rows[1]["baseline_forbidden_hit"])

    def test_baseline_only_run(self) -> None:
        rows, regressions, fixed = run_routing_ab.gate(self.CASES, {"a": "review", "b": "none"}, None)
        self.assertEqual((regressions, fixed), (0, 0))
        self.assertNotIn("candidate", rows[0])


if __name__ == "__main__":
    unittest.main()
