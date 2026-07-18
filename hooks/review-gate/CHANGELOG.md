# Changelog

All notable changes to this hook will be documented in this file.
This project adheres to [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2026-07-18

- 新增 omp 平台支持：`omp.ts` 扩展工厂安装到 `.omp/hooks/pre/review-gate.ts`，匹配 `task` 工具并从 payload 的 `agent` 字段提取子代理名，调用同一份 shell 脚本；退出码 2 翻译为 `{ block, reason }`，其余退出码放行。

## [Unreleased]

## [0.2.0] - 2026-07-17

### Added

- **Codex fragment**：matcher `(collaboration\.)?(spawn_agent|followup_task)`，锁定期间拦截 Codex 的子代理创建与后续任务派发。agent 名从 payload 常见字段（`agent`/`agent_type`/`agent_name`/`name`/`role`/`target_agent`，Claude 的 `subagent_type` 仍优先）提取；未命中候选字段时 fail-open，退回 CLI 当场拒绝 + pre-merge 兜底。确认真实 payload 字段后应收紧候选集。

## [0.1.0] - 2026-07-17

### Added

- 首版：PreToolUse hook，`subagent-workflow` 三轮硬门锁定期间机械拒绝 `implementer`/`reviewer` 子代理派发（matcher `Task`，按 `subagent_type` 匹配，默认阻断集可由状态文件 `blockedSubagents` 覆盖）。拦截发生在派发瞬间，不是 pre-merge 末端。
- 零逻辑重复的职责切分：gate 判定全部在 skill 分发的 `review_gate.py` CLI（记轮、算锁、验 converging 资格、管 post-gate 预算、写 ledger），本 hook 只读 `.review-gate.json` 预计算的 `locked`/`lockReason` 字段。状态文件缺失时 no-op，可安全装到所有项目。
- 仅 Claude Code fragment：Codex 侧无稳定的子代理派发工具名可 match，机械层由 CLI 的当场拒绝（exit 2 + 违规 ledger 行）+ pre-merge 确定性兜底承担。
