# Changelog

All notable changes to the **implementer** agent will be documented in this file.

## [1.1.0] - 2026-07-02

### Changed

- Added a worktree-discipline constraint to both surfaces: when the orchestrator assigns a worktree and an allowed-write-set, work only inside that worktree and write only within the allowed set; never write to the parent worktree.
- Explorer usage is now scoped to standalone implementation on both surfaces; as a leaf task inside an orchestrated workflow the implementer does not spawn subagents.
- Codex definition: added an Output Behavior section (report files created/modified, tests added/updated, and verification results) to match the Claude Code surface.
- Codex definition: added the missing `.gitignore` constraint (respect `.gitignore`; don't create files in ignored directories) to match the Claude Code surface.
- Removed the unused `skills: ["clarify"]` array from `agent.json` (never projected into either prompt body).

## [1.0.4] - 2026-06-14

### Changed

- Codex definition: model `gpt-5.4` -> `gpt-5.5` and reasoning effort `high` -> `xhigh`.

## [1.0.3] - 2026-03-30

### Changed

- Updated the Codex definition to use `gpt-5.4` with `high` reasoning effort as the default.
- Updated the Claude Code definition to use `opus` as the default model.

## [1.0.2] - 2026-03-27

### Changed

- Added an explicit Codex `model_reasoning_effort = "medium"` default so implementer keeps a stable execution-oriented posture without inheriting the caller's reasoning setting.

## [1.0.1] - 2026-03-27

### Changed

- Expanded the Codex definition to mention explorer usage explicitly and align its context-gathering guidance with the declared `explorer` dependency and the Claude Code surface.

## [1.0.0] - 2026-03-26

### Added

- Initial release: code implementation agent for writing, modifying, and refactoring code.
- Claude Code definition with Read, Glob, Grep, Bash, Edit, Write tools and Agent(explorer) for context.
- Codex definition with workspace-write sandbox mode.
- Implementation process: understand → gather context → implement → test → verify.
- Working with Plans section for executing planner output.
- Code Quality Standards with do/avoid guidelines.
- Explorer agent reference for pre-change context gathering.
- Clarify skill integration for ambiguous requirements.
