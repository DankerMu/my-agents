# Changelog

## [1.2.3] - 2026-09-10

### Changed

- omp 投影模型改名:`sub-gpt/deepseek-v4-flash-vision-exp-guan:high` -> `sub-gpt/deepseek-flash-guan:high`。网关侧已重命名该模型,旧 id 全 key 返回 404。

## [1.2.2] - 2026-09-07

### Changed

- omp 投影主 `sub-gpt/deepseek-v4-flash-vision-exp-guan:high`,副 `sub-omp/k3-256k:max`(原单一 `openai-codex/terra:max`)。文档查证属低推理活,与 omp 内置 librarian 同档。

## [1.2.1] - 2026-08-09

### Changed

- Claude Code 投影的 `model` 改为 1M 上下文变体 `sonnet[1m]`（原 `sonnet`）。别名解析链不变（仍走 `ANTHROPIC_DEFAULT_*_MODEL`），只是显式要 1M 上下文窗口。

All notable changes to the **docs-researcher** agent will be documented in this file.

## [1.2.0] - 2026-07-30

### Changed

- omp projection: pin `model: "openai-codex/terra:max"` (was `terra:high`) so the agent resolves through the `openai-codex` provider explicitly instead of relying on fuzzy provider coalescing.

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
