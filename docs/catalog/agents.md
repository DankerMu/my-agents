# Agents Catalog

> This file is generated. Run `npm run build`.

| Name | Version | Maturity | Archetype | Platforms | Categories | Description |
| --- | --- | --- | --- | --- | --- | --- |
| [debugger](../../agents/debugger/AGENT.md) | 1.0.5 | experimental | debugger | claude-code, codex | debugging, coding | Systematic debugging agent that diagnoses bugs, test failures, and unexpected behavior through hypothesis-driven investigation. |
| [docs-researcher](../../agents/docs-researcher/AGENT.md) | 1.0.1 | experimental | explorer | claude-code, codex | documentation, research | Documentation-backed research agent for verifying APIs, SDKs, frameworks, and libraries against official sources. |
| [explorer](../../agents/explorer/AGENT.md) | 1.3.1 | experimental | explorer | claude-code, codex | coding, productivity | Use when a task needs fast read-only codebase mapping, evidence gathering, impact analysis, or file and symbol discovery before implementation or review. |
| [implementer](../../agents/implementer/AGENT.md) | 1.3.1 | experimental | implementer | claude-code, codex | coding, refactoring | Code implementation agent that writes, modifies, and refactors code based on plans, specs, or direct instructions. |
| [issue-scribe](../../agents/issue-scribe/AGENT.md) | 0.1.2 | experimental | custom | claude-code, codex | workflow, productivity | Follow-up capture agent: takes a raw observation noticed during primary work, verifies it read-only, determines origin, boundary, and solution direction, dedups against existing issues, and files one structured GitHub issue for later delivery. Never fixes anything itself. |
| [monitor](../../agents/monitor/AGENT.md) | 0.1.1 | experimental | custom | claude-code, codex | devops, workflow | Cheap-model watchdog for harness-external long-running jobs (slurm, remote PID over ssh, CI runs). ID-based completion detection, one blocking poll loop per check, quiet waits, final-state report with evidence. Read-only; never does side work. |
| [planner](../../agents/planner/AGENT.md) | 1.2.4 | experimental | planner | claude-code, codex | design, coding, productivity | Architecture and implementation planning agent that designs step-by-step plans with trade-off analysis and escalates to implementation-planning for complex technical execution plans. |
| [researcher](../../agents/researcher/AGENT.md) | 1.1.5 | experimental | explorer | claude-code, codex | research, productivity | Web research agent for deep investigation, multi-source verification, and structured report generation. |
| [reviewer](../../agents/reviewer/AGENT.md) | 2.1.1 | experimental | reviewer | claude-code, codex | review, coding | Code review agent that performs structured, severity-graded reviews on PRs, diffs, and code changes. |
| [verifier](../../agents/verifier/AGENT.md) | 0.1.3 | experimental | custom | claude-code, codex | review, coding | Independent finding-verification agent. Adjudicates a single candidate review finding as CONFIRMED, PLAUSIBLE, or REFUTED using only diff/spec/code/test evidence. Read-only; never the reviewer that produced the candidate. |
