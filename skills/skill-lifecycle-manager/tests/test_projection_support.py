from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from _loader import load_script_module


projection_support = load_script_module("projection_support")


class ProjectionSupportTests(unittest.TestCase):
    def test_infer_project_root_finds_categories_marker(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp) / "repo"
            nested = repo_root / "skills" / "demo"
            nested.mkdir(parents=True)
            (repo_root / "categories.json").write_text('{"categories": ["workflow"]}\n', encoding="utf8")

            inferred = projection_support.infer_project_root(nested)

            self.assertEqual(inferred.resolve(), repo_root.resolve())

    def test_infer_project_root_raises_without_marker(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            start = Path(tmp) / "orphan" / "skill"
            start.mkdir(parents=True)

            with self.assertRaises(FileNotFoundError):
                projection_support.infer_project_root(start)

    def test_excluded_roots_merge_defaults_global_and_platform_values(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "demo-skill"
            skill_dir.mkdir()
            (skill_dir / "projection.json").write_text(
                '{\n'
                '  "exclude": ["eval", "tmp"],\n'
                '  "platforms": {"claude-code": {"exclude": ["scripts"]}}\n'
                '}\n',
                encoding="utf8",
            )

            claude_roots = projection_support.excluded_roots(skill_dir, "claude-code")
            codex_roots = projection_support.excluded_roots(skill_dir, "codex")

            self.assertIn("projection.json", claude_roots)
            self.assertIn("eval", claude_roots)
            self.assertIn("scripts", claude_roots)
            self.assertIn("skill.json", claude_roots)
            self.assertIn("tmp", codex_roots)
            self.assertNotIn("scripts", codex_roots)

    def test_copy_projection_drops_excluded_skill_entrypoints(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp) / "repo"
            skill_dir = repo_root / "skills" / "demo-skill"
            destination = repo_root / ".agents" / "skills" / "demo-skill"
            skill_dir.mkdir(parents=True)

            (skill_dir / "projection.json").write_text(
                '{\n  "exclude": ["CHANGELOG.md", "eval"]\n}\n',
                encoding="utf8",
            )
            (skill_dir / "skill.json").write_text(
                '{\n'
                '  "name": "demo-skill",\n'
                '  "entrypoints": {\n'
                '    "skillDoc": "SKILL.md",\n'
                '    "changelog": "CHANGELOG.md",\n'
                '    "suite": "eval/trigger-cases.json"\n'
                "  }\n"
                "}\n",
                encoding="utf8",
            )
            (skill_dir / "SKILL.md").write_text("# Demo Skill\n", encoding="utf8")
            (skill_dir / "CHANGELOG.md").write_text("# Changelog\n", encoding="utf8")
            (skill_dir / "eval").mkdir()
            (skill_dir / "eval" / "trigger-cases.json").write_text('{"cases":[]}\n', encoding="utf8")

            projection_support.copy_projection(skill_dir, "codex", destination)

            projected = json.loads((destination / "skill.json").read_text(encoding="utf8"))
            self.assertEqual(projected["entrypoints"], {"skillDoc": "SKILL.md"})
            self.assertFalse((destination / "CHANGELOG.md").exists())
            self.assertFalse((destination / "eval" / "trigger-cases.json").exists())

    def test_compare_projection_flags_missing_projected_skill_entrypoint(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp) / "repo"
            skill_dir = repo_root / "skills" / "demo-skill"
            destination = repo_root / ".agents" / "skills" / "demo-skill"
            skill_dir.mkdir(parents=True)
            destination.mkdir(parents=True)

            (skill_dir / "projection.json").write_text(
                '{\n  "exclude": ["CHANGELOG.md"]\n}\n',
                encoding="utf8",
            )
            raw_skill_json = (
                '{\n'
                '  "name": "demo-skill",\n'
                '  "entrypoints": {\n'
                '    "skillDoc": "SKILL.md",\n'
                '    "changelog": "CHANGELOG.md"\n'
                "  }\n"
                "}\n"
            )
            (skill_dir / "skill.json").write_text(raw_skill_json, encoding="utf8")
            (skill_dir / "SKILL.md").write_text("# Demo Skill\n", encoding="utf8")
            (skill_dir / "CHANGELOG.md").write_text("# Changelog\n", encoding="utf8")

            (destination / "skill.json").write_text(raw_skill_json, encoding="utf8")
            (destination / "SKILL.md").write_text("# Demo Skill\n", encoding="utf8")

            errors, warnings = projection_support.compare_projection(skill_dir, "codex", destination)

            self.assertEqual(warnings, [])
            self.assertIn("projected file differs from source: skill.json", errors)
            self.assertIn(
                "projected skill.json entrypoint missing on surface: changelog -> CHANGELOG.md",
                errors,
            )

    def test_compare_projection_accepts_normalized_skill_json_projection(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp) / "repo"
            skill_dir = repo_root / "skills" / "demo-skill"
            destination = repo_root / ".agents" / "skills" / "demo-skill"
            skill_dir.mkdir(parents=True)
            destination.mkdir(parents=True)

            (skill_dir / "projection.json").write_text(
                '{\n  "exclude": ["CHANGELOG.md"]\n}\n',
                encoding="utf8",
            )
            raw_skill_json = (
                '{\n'
                '  "name": "demo-skill",\n'
                '  "entrypoints": {\n'
                '    "skillDoc": "SKILL.md",\n'
                '    "changelog": "CHANGELOG.md"\n'
                "  }\n"
                "}\n"
            )
            (skill_dir / "skill.json").write_text(raw_skill_json, encoding="utf8")
            (skill_dir / "SKILL.md").write_text("# Demo Skill\n", encoding="utf8")
            (skill_dir / "CHANGELOG.md").write_text("# Changelog\n", encoding="utf8")

            projected_bytes = projection_support.projected_file_bytes(
                skill_dir,
                Path("skill.json"),
                "codex",
            )
            (destination / "skill.json").write_bytes(projected_bytes)
            (destination / "SKILL.md").write_text("# Demo Skill\n", encoding="utf8")

            errors, warnings = projection_support.compare_projection(skill_dir, "codex", destination)

            self.assertEqual(errors, [])
            self.assertEqual(warnings, [])

    def test_compare_projection_accepts_dot_slash_prefixed_entrypoints(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp) / "repo"
            skill_dir = repo_root / "skills" / "demo-skill"
            destination = repo_root / ".agents" / "skills" / "demo-skill"
            skill_dir.mkdir(parents=True)
            destination.mkdir(parents=True)

            (skill_dir / "projection.json").write_text(
                '{\n  "exclude": ["CHANGELOG.md", "eval"]\n}\n',
                encoding="utf8",
            )
            raw_skill_json = (
                '{\n'
                '  "name": "demo-skill",\n'
                '  "entrypoints": {\n'
                '    "skillDoc": "./SKILL.md",\n'
                '    "changelog": "./CHANGELOG.md",\n'
                '    "suite": "./eval/trigger-cases.json"\n'
                "  }\n"
                "}\n"
            )
            (skill_dir / "skill.json").write_text(raw_skill_json, encoding="utf8")
            (skill_dir / "SKILL.md").write_text("# Demo Skill\n", encoding="utf8")
            (skill_dir / "CHANGELOG.md").write_text("# Changelog\n", encoding="utf8")
            (skill_dir / "eval").mkdir()
            (skill_dir / "eval" / "trigger-cases.json").write_text('{"cases":[]}\n', encoding="utf8")

            projected_bytes = projection_support.projected_file_bytes(
                skill_dir,
                Path("skill.json"),
                "codex",
            )
            (destination / "skill.json").write_bytes(projected_bytes)
            (destination / "SKILL.md").write_text("# Demo Skill\n", encoding="utf8")

            errors, warnings = projection_support.compare_projection(skill_dir, "codex", destination)

            self.assertEqual(errors, [])
            self.assertEqual(warnings, [])

    def test_user_invoked_skill_routes_codex_projection_to_manual_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp) / "repo"
            skill_dir = repo_root / "skills" / "demo-skill"
            skill_dir.mkdir(parents=True)
            (repo_root / "categories.json").write_text('{"categories": ["workflow"]}\n', encoding="utf8")
            (skill_dir / "SKILL.md").write_text(
                "---\nname: demo-skill\ndescription: demo\ndisable-model-invocation: true\nversion: 0.1.0\n---\n\n# Demo\n",
                encoding="utf8",
            )

            self.assertTrue(projection_support.is_user_invoked(skill_dir))

            codex_dir = projection_support.projection_dir(skill_dir, "codex", "project")
            claude_dir = projection_support.projection_dir(skill_dir, "claude-code", "project")

            self.assertEqual(
                codex_dir.resolve(), (repo_root / ".agents" / "skills-manual" / "demo-skill").resolve()
            )
            self.assertEqual(
                claude_dir.resolve(), (repo_root / ".claude" / "skills" / "demo-skill").resolve()
            )

    def test_model_invoked_skill_keeps_codex_projection_in_skills_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp) / "repo"
            skill_dir = repo_root / "skills" / "demo-skill"
            skill_dir.mkdir(parents=True)
            (repo_root / "categories.json").write_text('{"categories": ["workflow"]}\n', encoding="utf8")
            (skill_dir / "SKILL.md").write_text(
                "---\nname: demo-skill\ndescription: demo\nversion: 0.1.0\n---\n\n# Demo\n",
                encoding="utf8",
            )

            self.assertFalse(projection_support.is_user_invoked(skill_dir))
            codex_dir = projection_support.projection_dir(skill_dir, "codex", "project")
            self.assertEqual(
                codex_dir.resolve(), (repo_root / ".agents" / "skills" / "demo-skill").resolve()
            )

    def test_skill_lifecycle_manager_projection_keeps_runtime_docs_honest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source_dir = Path(__file__).resolve().parents[1]

            for platform in ("codex", "claude-code"):
                destination = Path(tmp) / platform / "skill-lifecycle-manager"
                projection_support.copy_projection(source_dir, platform, destination)

                self.assertFalse((destination / "scripts" / "quick_validate_agent.py").exists())
                self.assertFalse((destination / "scripts" / "audit_agent_inventory.py").exists())
                self.assertTrue((destination / "scripts" / "run_unit_tests.py").exists())
                self.assertFalse((destination / "eval").exists())
                self.assertFalse((destination / "tests").exists())

                projected_skill_doc = (destination / "SKILL.md").read_text(encoding="utf8")
                self.assertIn("SLM_CANONICAL_DIR", projected_skill_doc)
                self.assertIn("canonical-only", projected_skill_doc)
                self.assertIn(
                    'uv run python "$SLM_CANONICAL_DIR/scripts/run_unit_tests.py"',
                    projected_skill_doc,
                )
                self.assertNotIn(
                    'uv run python "$SLM_DIR/scripts/run_unit_tests.py"',
                    projected_skill_doc,
                )


if __name__ == "__main__":
    unittest.main()
