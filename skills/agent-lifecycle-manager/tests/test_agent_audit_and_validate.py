from __future__ import annotations

import tempfile
import textwrap
import unittest
import json
from pathlib import Path

from _loader import load_script_module


audit_agent_inventory = load_script_module("audit_agent_inventory")
quick_validate_agent = load_script_module("quick_validate_agent")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf8")


def agent_json(
    *,
    name: str,
    description: str,
    skills: list[str] | None = None,
    agents: list[str] | None = None,
) -> str:
    skills = skills or []
    agents = agents or []
    return textwrap.dedent(
        f"""\
        {{
          "name": "{name}",
          "description": "{description}",
          "version": "1.0.0",
          "archetype": "explorer",
          "categories": ["workflow"],
          "skills": {json.dumps(skills)},
          "agents": {json.dumps(agents)},
          "entrypoints": {{"contract": "AGENT.md"}},
          "capabilities": {{
            "filesystemWrite": false,
            "network": false
          }}
        }}
        """
    )


def agent_contract(name: str) -> str:
    return textwrap.dedent(
        f"""\
        # {name} Contract

        - Handle only the assigned read-only evidence-gathering role.
        - Inspect repository facts before drawing conclusions.
        - Cite concrete files and distinguish facts from hypotheses.
        - Return a concise evidence map, risks, and open questions.
        - Never edit files or claim evidence that was not inspected.
        - For exact templates, read {{{{agent_references}}}}/operating-guide.md.
        """
    )


def operating_guide() -> str:
    return textwrap.dedent(
        """\
        # Demo Operating Guide

        This guide contains extended workflow detail for the test agent. It is
        deliberately loaded only when the concise core contract is insufficient.

        ## Workflow

        Inspect the assigned files, trace relevant relationships, cite concrete
        evidence, and return a bounded report without modifying the repository.
        """
    ) + ("Extra guide detail to clear the minimum length. " * 5)


def claude_code_markdown(*, name: str, description: str) -> str:
    frontmatter = textwrap.dedent(
        f"""\
        ---
        name: {name}
        description: >
          {description}
        tools: Bash
        ---
        """
    )
    return f"{frontmatter}\n{agent_contract(name)}"


def codex_toml(*, name: str, description: str) -> str:
    return (
        f'name = "{name}"\n'
        f'description = "{description}"\n'
        'developer_instructions = """\n'
        f"{agent_contract(name).strip()}\n"
        '"""\n'
        'sandbox_mode = "read-only"\n'
        'model_reasoning_effort = "medium"\n'
        'web_search = "off"\n'
    )


class AgentAuditAndValidateTests(unittest.TestCase):
    def test_validate_agent_accepts_well_formed_agent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp) / "repo"
            agent_dir = repo_root / "agents" / "demo-agent"

            write_text(repo_root / "categories.json", '{"categories": ["workflow"]}\n')
            write_text(
                agent_dir / "agent.json",
                agent_json(
                    name="demo-agent",
                    description="Use this agent when you need read-only evidence gathering for an agent request.",
                ),
            )
            write_text(agent_dir / "AGENT.md", agent_contract("demo-agent"))
            write_text(agent_dir / "references" / "operating-guide.md", operating_guide())
            write_text(
                agent_dir / "claude-code.md",
                claude_code_markdown(
                    name="demo-agent",
                    description="Use this agent when you need read-only evidence gathering for an agent request.",
                ),
            )
            write_text(
                agent_dir / "codex.toml",
                codex_toml(
                    name="demo-agent",
                    description="Use this agent when you need read-only evidence gathering for an agent request.",
                ),
            )
            write_text(
                agent_dir / "CHANGELOG.md",
                textwrap.dedent(
                    """\
                    # Changelog

                    ## [1.0.0] - 2026-03-28

                    ### Added
                    - Initial release.
                    """
                ),
            )

            errors, warnings = quick_validate_agent.validate_agent(agent_dir)

            self.assertEqual(errors, [])
            self.assertEqual(warnings, [])

    def test_audit_inventory_reports_missing_skill_dependency(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp) / "repo"
            agents_root = repo_root / "agents"
            agent_dir = agents_root / "demo-agent"

            write_text(repo_root / "categories.json", '{"categories": ["workflow"]}\n')
            write_text(
                agent_dir / "agent.json",
                agent_json(
                    name="demo-agent",
                    description="Use this agent when you need read-only evidence gathering for an agent request.",
                    skills=["missing-skill"],
                ),
            )
            write_text(agent_dir / "AGENT.md", agent_contract("demo-agent"))
            write_text(agent_dir / "references" / "operating-guide.md", operating_guide())
            write_text(
                agent_dir / "claude-code.md",
                claude_code_markdown(
                    name="demo-agent",
                    description="Use this agent when you need read-only evidence gathering for an agent request.",
                ),
            )
            write_text(
                agent_dir / "codex.toml",
                codex_toml(
                    name="demo-agent",
                    description="Use this agent when you need read-only evidence gathering for an agent request.",
                ),
            )
            write_text(
                agent_dir / "CHANGELOG.md",
                textwrap.dedent(
                    """\
                    # Changelog

                    ## [1.0.0] - 2026-03-28

                    ### Added
                    - Initial release.
                    """
                ),
            )
            write_text(
                repo_root / "skills" / "present-skill" / "skill.json",
                textwrap.dedent(
                    """\
                    {
                      "name": "present-skill",
                      "description": "Use this skill when you need a real local skill reference.",
                      "version": "1.0.0",
                      "categories": ["workflow"]
                    }
                    """
                ),
            )

            report = audit_agent_inventory.audit_inventory(agents_root)

            self.assertEqual(report["summary"]["total"], 1)
            self.assertGreaterEqual(report["summary"]["highCount"], 1)
            messages = [
                finding["message"]
                for entry in report["agents"]
                for finding in entry["findings"]
            ]
            self.assertTrue(
                any("references skill 'missing-skill'" in message for message in messages),
                messages,
            )


if __name__ == "__main__":
    unittest.main()
