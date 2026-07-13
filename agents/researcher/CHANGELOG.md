# Changelog

## [1.1.7] - 2026-07-12

### Changed

- Drop the pinned Claude Code `model` and Codex `model` / `model_reasoning_effort` so the agent inherits the parent session's model and reasoning effort on both platforms.

## [1.1.6] - 2026-07-10

### Changed

- Codex surface: upgrade model `gpt-5.5` -> `gpt-5.6-sol` and reasoning effort `xhigh` -> `high`.

All notable changes to the **researcher** agent will be documented in this file.

## [1.1.5] - 2026-07-10

### Changed

- Replaced duplicated platform behavior manuals with one concise canonical `AGENT.md` contract and generated Claude Code/Codex behavior projections.

### Added

- Preserved the extended workflow and output templates in an on-demand, installable `references/operating-guide.md`.

## [1.1.4] - 2026-07-02

### Changed

- Wire the declared `deep-research` skill dependency into the prompt bodies (Claude Code + Codex): Deep-scope requests now route through the skill's harness when installed, with the inline process as fallback. Previously the dependency was metadata-only.
- Remove the declared `clarify` skill dependency: the prompt's inline scope-clarification step covers it, and the skill was never referenced by the projected instructions.

## [1.1.3] - 2026-06-14

### Changed

- Codex definition: model `gpt-5.4` -> `gpt-5.5` and reasoning effort `high` -> `xhigh`.

## [1.1.2] - 2026-03-30

### Changed

- Updated the Codex definition to use `gpt-5.4` with `high` reasoning effort as the default.
- Updated the Claude Code definition to use `opus` as the default model.

## [1.1.1] - 2026-03-27

### Changed

- Added an explicit Codex `model_reasoning_effort = "high"` default so researcher keeps a stable multi-source synthesis posture across caller sessions.

## [1.1.0] - 2026-03-26

### Added

- Detailed Search Strategy section (query techniques, source prioritization, failure recovery).
- Anti-Hallucination Protocol section.
- Local Context Integration section for codebase-aware research.
- Gaps and Limitations section in output format.
- Caller-awareness as core behavior principle.
- Expanded Codex developer_instructions to match Claude Code depth.

## [1.0.0] - 2026-03-25

### Added

- Initial release: web research agent with multi-source verification.
- Claude Code definition with WebSearch, WebFetch, Read, Glob, Grep tools.
- Codex definition with read-only sandbox mode.
- Structured report format (Summary / Findings / Recommendations / Sources).
- Deep-research and clarify skill integrations.
