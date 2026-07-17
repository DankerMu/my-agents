# Changelog

All notable changes to this hook will be documented in this file.
This project adheres to [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-07-17

### Added

- 首版：PreToolUse hook，`subagent-workflow` 三轮硬门锁定期间机械拒绝 `implementer`/`reviewer` 子代理派发（matcher `Task`，按 `subagent_type` 匹配，默认阻断集可由状态文件 `blockedSubagents` 覆盖）。拦截发生在派发瞬间，不是 pre-merge 末端。
- 零逻辑重复的职责切分：gate 判定全部在 skill 分发的 `review_gate.py` CLI（记轮、算锁、验 converging 资格、管 post-gate 预算、写 ledger），本 hook 只读 `.review-gate.json` 预计算的 `locked`/`lockReason` 字段。状态文件缺失时 no-op，可安全装到所有项目。
- 仅 Claude Code fragment：Codex 侧无稳定的子代理派发工具名可 match，机械层由 CLI 的当场拒绝（exit 2 + 违规 ledger 行）+ pre-merge 确定性兜底承担。
