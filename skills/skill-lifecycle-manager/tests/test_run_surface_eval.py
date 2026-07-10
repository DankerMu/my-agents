from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from _loader import load_script_module


run_surface_eval = load_script_module("run_surface_eval")


class RunSurfaceEvalTests(unittest.TestCase):
    def _eval_entry(self) -> dict:
        return {
            "id": "case-1",
            "label": "Case 1",
            "prompt": "Say hello",
            "successCriteria": "Returns a useful answer",
        }

    def test_baseline_stage_hides_project_projection_and_restores_it(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp) / "repo"
            workdir = repo_root / "subdir"
            projection_dir = repo_root / ".agents" / "skills" / "demo-skill"
            stage_dir = repo_root / "artifacts"
            workdir.mkdir(parents=True)
            projection_dir.mkdir(parents=True)
            (repo_root / "categories.json").write_text('{"categories": ["workflow"]}\n', encoding="utf8")
            (projection_dir / "marker.txt").write_text("present\n", encoding="utf8")

            def fake_run(command, cwd, capture_output, text, timeout):  # type: ignore[no-untyped-def]
                self.assertFalse(projection_dir.exists())
                return subprocess.CompletedProcess(command, 0, stdout="baseline output", stderr="")

            with mock.patch.object(run_surface_eval, "build_command", return_value=["dummy"]), mock.patch.object(
                run_surface_eval.subprocess,
                "run",
                side_effect=fake_run,
            ):
                exit_code = run_surface_eval.run_case(
                    surface="codex",
                    workdir=workdir,
                    skill_name="demo-skill",
                    eval_entry=self._eval_entry(),
                    stage="baseline",
                    stage_dir=stage_dir,
                    effort=None,
                    timeout_sec=5,
                )

            self.assertEqual(exit_code, 0)
            self.assertTrue(projection_dir.exists())
            self.assertTrue((projection_dir / "marker.txt").exists())

            result = json.loads((stage_dir / "result.json").read_text(encoding="utf8"))
            self.assertEqual(result["baseline"]["mode"], "project-projection-disabled")
            self.assertEqual(result["stage"], "baseline")

    def test_timeout_writes_structured_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp) / "repo"
            workdir = repo_root / "subdir"
            stage_dir = repo_root / "artifacts"
            workdir.mkdir(parents=True)
            (repo_root / "categories.json").write_text('{"categories": ["workflow"]}\n', encoding="utf8")

            timeout_error = subprocess.TimeoutExpired(
                cmd=["dummy"],
                timeout=7,
                output="partial stdout",
                stderr="partial stderr",
            )

            with mock.patch.object(run_surface_eval, "build_command", return_value=["dummy"]), mock.patch.object(
                run_surface_eval.subprocess,
                "run",
                side_effect=timeout_error,
            ):
                exit_code = run_surface_eval.run_case(
                    surface="codex",
                    workdir=workdir,
                    skill_name="demo-skill",
                    eval_entry=self._eval_entry(),
                    stage="with-skill",
                    stage_dir=stage_dir,
                    effort=None,
                    timeout_sec=7,
                )

            self.assertEqual(exit_code, run_surface_eval.TIMEOUT_EXIT_CODE)
            self.assertEqual((stage_dir / "stdout.log").read_text(encoding="utf8"), "partial stdout")
            self.assertEqual((stage_dir / "stderr.log").read_text(encoding="utf8"), "partial stderr")

            result = json.loads((stage_dir / "result.json").read_text(encoding="utf8"))
            self.assertTrue(result["timedOut"])
            self.assertEqual(result["exitCode"], run_surface_eval.TIMEOUT_EXIT_CODE)
            self.assertEqual(result["error"], "process timed out after 7 seconds")

    def test_cross_skill_baseline_hides_and_restores_every_projection(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp) / "repo"
            workdir = repo_root / "subdir"
            stage_dir = repo_root / "artifacts"
            projections = [
                repo_root / ".agents" / "skills" / "clarify",
                repo_root / ".agents" / "skills" / "brainstorming",
            ]
            workdir.mkdir(parents=True)
            (repo_root / "categories.json").write_text('{"categories": ["workflow"]}\n', encoding="utf8")
            for projection in projections:
                projection.mkdir(parents=True)
                (projection / "marker.txt").write_text("present\n", encoding="utf8")

            def fake_run(command, cwd, capture_output, text, timeout):  # type: ignore[no-untyped-def]
                self.assertTrue(all(not projection.exists() for projection in projections))
                return subprocess.CompletedProcess(
                    command,
                    0,
                    stdout="Route: none\nFollowups: none\nNo routing skills are available.",
                    stderr="",
                )

            with mock.patch.object(run_surface_eval, "build_command", return_value=["dummy"]), mock.patch.object(
                run_surface_eval.subprocess,
                "run",
                side_effect=fake_run,
            ):
                exit_code = run_surface_eval.run_case(
                    surface="codex",
                    workdir=workdir,
                    skill_name="workflow-stage-routing",
                    eval_entry={
                        **self._eval_entry(),
                        "expectedRoute": "clarify",
                        "forbiddenRoutes": ["brainstorming"],
                        "allowedFollowups": [],
                    },
                    stage="baseline",
                    stage_dir=stage_dir,
                    effort=None,
                    timeout_sec=5,
                    baseline_skill_names=["clarify", "brainstorming"],
                )

            self.assertEqual(exit_code, 0)
            self.assertTrue(all(projection.exists() for projection in projections))
            result = json.loads((stage_dir / "result.json").read_text(encoding="utf8"))
            self.assertEqual(result["baseline"]["mode"], "project-projections-disabled")
            self.assertEqual(result["baseline"]["disabledCount"], 2)
            self.assertFalse(result["routing"]["scored"])

    def test_routing_outcome_scores_route_and_followups(self) -> None:
        outcome = run_surface_eval._routing_outcome(
            {
                "expectedRoute": "clarify",
                "forbiddenRoutes": ["brainstorming"],
                "allowedFollowups": ["implementation-planning"],
                "expectedDepth": "light",
            },
            "Route: clarify\nFollowups: implementation-planning\nDepth: light\nReason: constraints conflict.",
            "with-skill",
        )

        self.assertIsNotNone(outcome)
        self.assertTrue(outcome["passed"])
        self.assertEqual(outcome["actualRoute"], "clarify")
        self.assertEqual(outcome["actualDepth"], "light")

        too_heavy = run_surface_eval._routing_outcome(
            {
                "expectedRoute": "clarify",
                "forbiddenRoutes": ["brainstorming"],
                "allowedFollowups": [],
                "expectedDepth": "light",
            },
            "Route: clarify\nFollowups: none\nDepth: heavy\nReason: over-escalated.",
            "with-skill",
        )
        self.assertFalse(too_heavy["passed"])

        missing_followups = run_surface_eval._routing_outcome(
            {
                "expectedRoute": "clarify",
                "forbiddenRoutes": ["brainstorming"],
                "allowedFollowups": [],
                "expectedDepth": "light",
            },
            "Route: clarify\nDepth: light\nReason: constraints conflict.",
            "with-skill",
        )
        self.assertFalse(missing_followups["passed"])
        self.assertFalse(missing_followups["followupsParsed"])


if __name__ == "__main__":
    unittest.main()
