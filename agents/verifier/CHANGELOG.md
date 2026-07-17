# Changelog

## [0.2.0] - 2026-07-17

### Changed

- **合同对齐 Phase 4.5 批处理语义**：subagent-workflow 的验证门早已按 failure-class 分批派发（每批至多 5 个 candidate、同类共享证据基座、单例类即一批），但本合同仍写"每次只裁决一个 candidate"——同一执行方看到互相矛盾的两条规则，就是给跳过或敷衍留的口子。合同、operating guide、描述全面改为：裁决所属批次内每个 candidate、逐个独立、每个自带证据，批级一票无逐条证据即无效、编排器必须重跑该批；verifier 不得是产出本批任一 candidate 的 reviewer。输出模板改为批头 + 逐 candidate 块。

## [0.1.5] - 2026-07-12

### Changed

- Drop the pinned Claude Code `model` and Codex `model` / `model_reasoning_effort` so the agent inherits the parent session's model and reasoning effort on both platforms.

## [0.1.4] - 2026-07-10

### Changed

- Codex surface: upgrade model `gpt-5.5` -> `gpt-5.6-sol` and reasoning effort `xhigh` -> `high`.

All notable changes to the **verifier** agent will be documented in this file.

## [0.1.3] - 2026-07-10

### Changed

- Replaced duplicated platform behavior manuals with one concise canonical `AGENT.md` contract and generated Claude Code/Codex behavior projections.

### Added

- Preserved the extended workflow and output templates in an on-demand, installable `references/operating-guide.md`.

## [0.1.2] - 2026-07-02

### Changed

- Codex definition: added the two constraint bullets present on the Claude Code surface but missing from Codex ("Do not fabricate scenarios or guards" and "One candidate, one verdict — keep the output to the structured block").
- Claude Code tools: `Bash` -> `Bash(readonly)` to match the read-only role.

## [0.1.1] - 2026-06-14

### Changed

- Codex definition: model `gpt-5.4` -> `gpt-5.5` and reasoning effort `high` -> `xhigh`.

## [0.1.0] - 2026-06-14

### Added

- Initial release: independent finding-verification gate that adjudicates a single candidate review finding as CONFIRMED, PLAUSIBLE, or REFUTED.
- Read-only posture on both surfaces: Claude Code definition with Read, Glob, Grep, Bash; Codex definition with `read-only` sandbox and `gpt-5.4` at `high` reasoning effort.
- Encodes the find/verify separation: a verifier must not be the reviewer that produced the candidate, must not search for new findings, and must default ambiguous-but-realistic runtime states to PLAUSIBLE.
- Pairs with the `subagent-workflow` skill's Phase 4.5 verification gate.
