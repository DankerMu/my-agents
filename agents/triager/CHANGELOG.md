# Changelog

## [0.2.0] - 2026-07-18

### Added

- omp platform projection (`omp.md`): task-agent definition for `.omp/agents/`, generated from `AGENT.md` with tools mapped to omp tool ids and explicit `spawns` where the Claude projection used `Agent(...)`.

## [0.1.5] - 2026-07-12

### Changed

- Drop the pinned Claude Code `model` and Codex `model` / `model_reasoning_effort` so the agent inherits the parent session's model and reasoning effort on both platforms.

## [0.1.4] - 2026-07-10

### Changed

- Codex surface: upgrade model `gpt-5.5` -> `gpt-5.6-sol` and reasoning effort `xhigh` -> `high`.

## [0.1.3] - 2026-07-10

### Changed

- Replaced duplicated platform behavior manuals with one concise canonical `AGENT.md` contract and generated Claude Code/Codex behavior projections.

### Added

- Preserved the extended workflow and output templates in an on-demand, installable `references/operating-guide.md`.

## [0.1.2] - 2026-06-14

### Changed

- Codex definition: model `gpt-5.4` -> `gpt-5.5` and reasoning effort `high` -> `xhigh`.

## [0.1.1] - 2026-03-30

### Changed

- Updated the Codex definition to use `gpt-5.4` with `high` reasoning effort as the default.
- Updated the Claude Code definition to use `opus` as the default model.

## [0.1.0]

- Initial triager agent for Issue Agent OS.
- Reads issues, assesses actionability, decides routing, writes execution briefs.
- Seven routing decisions: execute, split, plan_then_execute, investigate, defer, reject, escalate.
- Claude Code and Codex platform definitions.
