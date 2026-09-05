# Changelog

All notable changes to this skill will be documented in this file.
This project adheres to [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2026-09-05

### Changed

- **定位收窄为可携带性**（同步 `mattpocock/skills` v1.2.x `PHASE-BOUNDARIES.md`）：description 与开篇不再把"上下文将满"列为触发条件——那是原生压缩的领地；只在有东西要随身带走时用：换 harness、换目录/仓库、交给同事、中途分叉 side task，以及本仓库特有的 issue 工作流跨会话续跑（工作流计数器只在会话记忆里，会话结束后新会话必须靠它恢复）。Non-goals 同步；完整决策树指向 `ask-danker` 跨会话节。模板与硬规则不变。

## [0.1.0] - 2026-07-16

### Added

- 首版，adapted from `mattpocock/skills` `productivity/handoff`（把会话压缩成交接文档、suggested skills 节、引用不复制、脱敏、按参数裁剪）。
- 针对本仓库跨会话续跑场景的适配：
  - **写入位置分流**：处于 issue/PR 工作流时写 `.workplans/<issue-or-pr>/handoff.md`（与证据束同地、覆盖旧份），否则沿用上游的 OS 临时目录约定。
  - **工作流状态节**：round counter、gate 状态、`Last clean reviewed SHA`、证据束路径随文档携带——`subagent-workflow` 三轮硬 gate 的计数器不归零语义跨会话不丢。
  - **已排除路径节**：tried-and-failed 方案及否决理由，防止新会话重走死路。
  - **接续协议**：输出绝对路径 + 新会话第一条消息模板；新会话先恢复计数器再执行"下一步"。
  - 脱敏落为可执行动作（按常见 secret 形状 grep 自查）；新增交付前"新 agent 视角"自检。
- User-invoked（`disable-model-invocation: true`），已登记进 `ask-danker` 路由表"跨会话"节与 user-invoked 清单。
