# Changelog

## [0.1.1] - 2026-07-10

### Changed

- Replaced duplicated platform behavior manuals with one concise canonical `AGENT.md` contract and generated Claude Code/Codex behavior projections.

### Added

- Preserved the extended workflow and output templates in an on-demand, installable `references/operating-guide.md`.

## [0.1.0] - 2026-07-06

- 首个版本：harness 外部长任务（slurm / 远端 PID / CI run）的廉价看护 agent。
- 双平台：Claude Code 用 `model: haiku`，Codex 用 `gpt-5.3-codex-spark`。
- 契约固化历史教训：完成检测必须基于 JobID/PID/RunID（禁止 log 轮询判完成）、轮询循环活在单次阻塞 shell 调用内（等待不烧模型轮次）、只读、静默等待、时间只读时钟不估算。
