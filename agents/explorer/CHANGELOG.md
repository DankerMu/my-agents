# Changelog

All notable changes to the **explorer** agent will be documented in this file.

## [1.2.2] - 2026-07-02

### Changed

- Remove the declared `clarify` skill dependency. It was never projected into the Claude Code or Codex prompt bodies, and an interactive requirements-clarification skill does not fit a read-only recon subagent. Declared skill dependencies must be visible in the projected instructions.

## [1.2.1] - 2026-06-14

### Changed

- Codex definition: reasoning effort `high` -> `xhigh` (model `gpt-5.3-codex-spark` unchanged).

## [1.2.0] - 2026-03-26

### Added

- Change scoping guidance for blast-radius analysis and risky touch points.
- Reporting guidance for separating observed facts from inference.
- Preferred output shape with impact radius and next recommended check sections.

### Changed

- Updated the Codex configuration to use `gpt-5.3-codex-spark` with `high` reasoning effort.
- Aligned the Claude Code definition with the newer Codex prompt wording and reporting structure.
- Refined the one-line agent description to include impact analysis.

## [1.1.0] - 2026-03-26

### Added

- Common Exploration Tasks section (architecture mapping, dependency tracing, pattern discovery, test coverage).
- Reporting to Callers section with guidelines for structured output to planner/reviewer.
- Unexpected Discoveries section in output format.
- Expanded Codex developer_instructions to match Claude Code depth.

### Changed

- Expanded Search Strategy with parallelization guidance.
- Added caller-awareness as core behavior principle.
- Enhanced constraints with guidance on handling large result sets.

## [1.0.0] - 2026-03-25

### Added

- Initial release: read-only codebase exploration agent.
- Claude Code definition with Glob, Grep, Read, Bash(readonly) tools.
- Codex definition with read-only sandbox mode.
- Structured output format (Finding / Evidence / Context).
- Clarify skill integration for ambiguous requests.
