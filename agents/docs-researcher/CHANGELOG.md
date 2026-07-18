# Changelog

All notable changes to the **docs-researcher** agent will be documented in this file.

## [1.1.0] - 2026-07-18

### Added

- omp platform projection (`omp.md`): task-agent definition for `.omp/agents/`, generated from `AGENT.md` with tools mapped to omp tool ids and explicit `spawns` where the Claude projection used `Agent(...)`.
- omp projection pins `model: "terra:high"` (fuzzy-matched against the local model catalog).

## [1.0.1] - 2026-07-10

### Changed

- Replaced duplicated platform behavior manuals with one concise canonical `AGENT.md` contract and generated Claude Code/Codex behavior projections.

### Added

- Preserved the extended workflow and output templates in an on-demand, installable `references/operating-guide.md`.

## [1.0.0] - 2026-03-26

### Added

- Initial release of the docs-researcher agent.
- Codex definition with read-only sandbox, live web search, and documentation MCP configuration.
- Claude Code definition focused on official-documentation-first verification.
- Metadata for documentation and research discovery in the generated catalog.
