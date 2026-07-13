# Changelog

## [1.0.7] - 2026-07-12

### Changed

- Drop the pinned Claude Code `model` and Codex `model` / `model_reasoning_effort` so the agent inherits the parent session's model and reasoning effort on both platforms.

## [1.0.6] - 2026-07-10

### Changed

- Codex surface: upgrade model `gpt-5.5` -> `gpt-5.6-sol` and reasoning effort `xhigh` -> `high`.

All notable changes to the **debugger** agent will be documented in this file.

## [1.0.5] - 2026-07-10

### Changed

- Replaced duplicated platform behavior manuals with one concise canonical `AGENT.md` contract and generated Claude Code/Codex behavior projections.

### Added

- Preserved the extended workflow and output templates in an on-demand, installable `references/operating-guide.md`.

## [1.0.4] - 2026-06-14

### Changed

- Codex definition: model `gpt-5.4` -> `gpt-5.5` and reasoning effort `high` -> `xhigh`.

## [1.0.3] - 2026-03-30

### Changed

- Updated the Codex definition to use `gpt-5.4` with `high` reasoning effort as the default.
- Updated the Claude Code definition to use `opus` as the default model.

## [1.0.2] - 2026-03-27

### Changed

- Added an explicit Codex `model_reasoning_effort = "high"` default so debugger runs with a stable deep-investigation posture instead of inheriting the caller's reasoning setting.

## [1.0.1] - 2026-03-27

### Changed

- Expanded the Codex definition to mention explorer usage explicitly and align its investigation guidance with the declared `explorer` dependency and the Claude Code surface.

## [1.0.0] - 2026-03-26

### Added

- Initial release: systematic debugging agent with hypothesis-driven investigation.
- Claude Code definition with Read, Glob, Grep, Bash, Edit, Write tools and Agent(explorer) for context.
- Codex definition with workspace-write sandbox mode.
- Six-phase debugging process: reproduce → hypothesize → investigate → isolate → fix → confirm.
- Common debugging patterns: test failures, runtime errors, CI-only failures, performance issues.
- Investigation log template for structured debugging records.
- Explorer agent reference for code path tracing during investigation.
- Clarify skill integration for ambiguous bug reports.
