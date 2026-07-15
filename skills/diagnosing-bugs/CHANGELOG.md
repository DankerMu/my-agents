# Changelog

All notable changes to this skill will be documented in this file.
This project adheres to [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2026-07-14

### Added
- **多代理模式（可选）**：吸收环境侧 UltraThink Debug Orchestrator（原全局 `/debug` 命令与 `debug` agent，两者内容同源、方法论与本 skill 冲突——其"先出 5-7 个假设再设计诊断"顺序正是红命令硬闸要防的失败）。保留其有价值的部分：多视角扇出（架构失效点/外部先例/代码路径/实验设计）用于 Phase 1 回路构建与 Phase 3 假设生成的并行化，用户确认点（已是 Phase 3 非阻塞检查点）；丢弃其假设先于回路的顺序与固定四角色输出格式。**扇出加速闸门之后的宽度，不绕过闸门。**

### Changed
- Description 移除 `/debug` 反触发（该入口已废弃、由本 skill 取代），接管 "debug" 触发词；标注多代理扇出模式。

## [0.1.0] - 2026-07-14

- Initial port of `diagnosing-bugs`, adapted from `mattpocock/skills` v1.1.0. 因未知失败的六阶段诊断纪律：反馈回路优先（10 级构建阶梯 + "把回路当产品打磨"三收紧轴 + 非确定性 bug 提复现率策略）、**红命令硬闸门**（无已跑过且能红的命令禁止进入假设）、最小化复现（逐元素承重判据）、3-5 个可证伪假设排序、单变量插桩（`[DEBUG-xxx]` 标签清理纪律 + 性能回归先测量后修）、修复前回归测试的 **seam 纪律**（找不到正确的 seam 本身就是发现）、清理与归因（确诊假设写进 commit/PR）。
- 有意偏离上游：`invocation_posture: hybrid` + 窄触发描述（因未知失败），与环境侧 `/debug` 编排壳错开管辖——本 skill 是单线方法论内核，可被 `subagent-workflow` 经 Skill 工具消费（对齐 `risk-adaptive-cross-review` 的 canonical 词汇技能先例）。
- 持久层本地化：上游 `CONTEXT.md`/`docs/adr/` → 本仓库 `openspec/glossary.md` + `docs/adr/`（缺失静默跳过）。
- HITL 检查点本地化：上游"把假设清单拿给用户看"在管道（AFK）场景降级为证据记录、不阻塞；`scripts/hitl-loop.template.sh`（step/capture 原语 + KEY=VALUE 机读输出）保留用于独立场景的回路兜底。
- Handoff 本地化：架构性根因 → `improve-codebase-architecture`（修复落地后）；seam 缺失/暂缓 → 所在工作流的 deferral 路由（issue-scribe / `gh-create-issue`）。
