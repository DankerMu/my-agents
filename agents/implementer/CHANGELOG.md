# Changelog

## [1.6.0] - 2026-07-18

### Added

- omp platform projection (`omp.md`): task-agent definition for `.omp/agents/`, generated from `AGENT.md` with tools mapped to omp tool ids and explicit `spawns` where the Claude projection used `Agent(...)`.
- omp projection pins `model: "claude-opus-4-8:xhigh"` (fuzzy-matched against the local model catalog).

## [1.5.0] - 2026-07-17

### Changed

- **TDD 微循环压缩为批量红证明**（动机：实跑反馈强制 red-green 微循环对 LLM implementer 过重——每个循环是一次完整推理+工具往返，而"先写测试"的作者顺序在最终 diff 里不可核查，付全价买到的合规信号可伪造）。改为：实现与测试同批完成后，`git stash push -m "red-proof" -- <source paths>`（新测试留在树上）跑一次全红证明——测新行为的测试在旧代码上必须失败，过了就是在测想象中的行为；随即 `git stash pop` 跑绿。N 次微循环 → 2 次运行，反测试腐化保证不变，且红跑输出成为可核查证据。tracer bullet 首切片降级为绿地/陌生集成路径的推荐。
- **Stash 卫生硬门**：push/pop 同步完成，红证明未收尾禁止其他动作，pop 冲突即刻处理；报告完成前 `git stash list` 不得残留 `red-proof` 条目——与 `[DEBUG-<tag>]` grep 清零同级的阻塞缺陷。

## [1.4.0] - 2026-07-14

### Added

- Contract gains a test-discipline bullet: vertical slices at pre-agreed public seams, expected values from an independent source of truth, boundary-only mocking, refactoring deferred to the review stage.
- Operating guide gains a **Test Discipline** section, adapted from `mattpocock/skills` v1.1.0 `tdd`: vertical slices / tracer bullet (never batch tests up front — they verify imagined behavior), consume pre-agreed seams (a missing seam is a finding, not license to test internals), independent expected values (tautology guard), boundary-only mocking with mockability design (inject clients; SDK-style per-operation functions over a generic fetcher), WHAT-naming in the project's glossary vocabulary (`openspec/glossary.md`), and red → green only while implementing.

## [1.3.3] - 2026-07-12

### Changed

- Drop the pinned Claude Code `model` and Codex `model` / `model_reasoning_effort` so the agent inherits the parent session's model and reasoning effort on both platforms.

## [1.3.2] - 2026-07-10

### Changed

- Codex surface: upgrade model `gpt-5.5` -> `gpt-5.6-sol` and reasoning effort `xhigh` -> `high`.

All notable changes to the **implementer** agent will be documented in this file.

## [1.3.1] - 2026-07-10

### Changed

- Replaced duplicated platform behavior manuals with one concise canonical `AGENT.md` contract and generated Claude Code/Codex behavior projections.

### Added

- Preserved the extended workflow and output templates in an on-demand, installable `references/operating-guide.md`.

## [1.3.0] - 2026-07-06

### Changed

- Anti-parallel-implementation constraint on both surfaces (eng-init alignment): fix in place — never create parallel `_v2`/`_new`/`_backup`/`-copy` files or directories to sidestep modifying the original; evolve the existing file unless the plan explicitly calls for a new module.

## [1.2.0] - 2026-07-06

### Changed

- Sink the orchestration-brief behavior contract into the role definition on both surfaces: treat issue text, review findings, code comments, and fetched content in the brief as untrusted data, not instructions (prompt-injection defense), and never invoke workflows/skills or delegate to another AI/code agent — explorer (where permitted) is the only subagent. Orchestrator briefs no longer need to restate these to get them; the injected boundary remains defense-in-depth.

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
