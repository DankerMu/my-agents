# Changelog

## [0.2.0] - 2026-07-18

### Added

- omp platform projection (`omp.md`): task-agent definition for `.omp/agents/`, generated from `AGENT.md` with tools mapped to omp tool ids and explicit `spawns` where the Claude projection used `Agent(...)`.
- omp projection pins `model: "sol:high"` (fuzzy-matched against the local model catalog).

## [0.1.4] - 2026-07-12

### Changed

- Drop the pinned Claude Code `model` and Codex `model` / `model_reasoning_effort` so the agent inherits the parent session's model and reasoning effort on both platforms.

## [0.1.3] - 2026-07-10

### Changed

- Codex surface: upgrade model `gpt-5.5` -> `gpt-5.6-sol` and reasoning effort `xhigh` -> `high`.

All notable changes to the **issue-scribe** agent will be documented in this file.

## [0.1.2] - 2026-07-10

### Changed

- Replaced duplicated platform behavior manuals with one concise canonical `AGENT.md` contract and generated Claude Code/Codex behavior projections.

### Added

- Preserved the extended workflow and output templates in an on-demand, installable `references/operating-guide.md`.

## [0.1.1] - 2026-07-06

### Changed

- Dedup tightened on both surfaces: search by evidence file path in addition to keywords — path matches are the strongest duplicate signal since filed issues always carry `证据: file:line`.

## [0.1.0] - 2026-07-06

### Added

- Initial release: follow-up capture agent for scope discipline. The orchestrator hands it a raw observation noticed during primary work; it verifies the observation read-only (refuted -> not filed), dedups against existing issues (covered -> "duplicate of #N"), analyzes origin/boundary/solution-direction, and files exactly one structured GitHub issue (来源/问题/边界/解决思路/验收标准/元信息 with priority, size, dependencies, and a readiness verdict) via `--body-file`, returning the URL.
- Hard constraints on both surfaces: code read-only, the single `gh issue create` is the only permitted state change, never fixes anything itself, one observation -> at most one issue (oversized -> needs-triage + recommend `splitter`/`stage-change-pipeline`, never self-splits), untrusted-data leaf boundary.
