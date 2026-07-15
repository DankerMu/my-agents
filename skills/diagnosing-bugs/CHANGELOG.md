# Changelog

All notable changes to this skill will be documented in this file.
This project adheres to [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-07-14

- Initial port of `diagnosing-bugs`, adapted from `mattpocock/skills` v1.1.0. 因未知失败的六阶段诊断纪律：反馈回路优先（10 级构建阶梯 + "把回路当产品打磨"三收紧轴 + 非确定性 bug 提复现率策略）、**红命令硬闸门**（无已跑过且能红的命令禁止进入假设）、最小化复现（逐元素承重判据）、3-5 个可证伪假设排序、单变量插桩（`[DEBUG-xxx]` 标签清理纪律 + 性能回归先测量后修）、修复前回归测试的 **seam 纪律**（找不到正确的 seam 本身就是发现）、清理与归因（确诊假设写进 commit/PR）。
- 有意偏离上游：`invocation_posture: hybrid` + 窄触发描述（因未知失败），与环境侧 `/debug` 编排壳错开管辖——本 skill 是单线方法论内核，可被 `subagent-workflow` 经 Skill 工具消费（对齐 `risk-adaptive-cross-review` 的 canonical 词汇技能先例）。
- 持久层本地化：上游 `CONTEXT.md`/`docs/adr/` → 本仓库 `openspec/glossary.md` + `docs/adr/`（缺失静默跳过）。
- HITL 检查点本地化：上游"把假设清单拿给用户看"在管道（AFK）场景降级为证据记录、不阻塞；`scripts/hitl-loop.template.sh`（step/capture 原语 + KEY=VALUE 机读输出）保留用于独立场景的回路兜底。
- Handoff 本地化：架构性根因 → `improve-codebase-architecture`（修复落地后）；seam 缺失/暂缓 → 所在工作流的 deferral 路由（issue-scribe / `gh-create-issue`）。
