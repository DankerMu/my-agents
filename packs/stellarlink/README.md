# Stellarlink Pack

## Purpose

从 stellarlink-skills 整体吸收的一组工程方法论 skill，打成一个可安装单元。核心是一条**证据驱动的交付链**（spec → 实现 → 验证 → 验收），外加三个独立的重型工作流（迁移、仓库就绪、进化循环）和一个逆向工程路由器。

调用姿势：**除 `tdd` 与 `vdd` 外全部 `disable-model-invocation: true`（手动 `/name` 调用）**。`tdd`/`vdd` 被 `implement` 与 `code-migration` 在运行中调用，按本仓 `instructions/root/reference/skill-flags.md` 的规则（被其他 skill 中途调用的 skill 不得打 manual 标）保持模型可调。

## Included Skills

### 交付链

- `architecture-design` — 新项目架构设计 / 存量架构审计：模块分解、seam、目录结构，用 `/grill-me` 的访谈协议逐轮推进，落定的决策记为 ADR。产出交给 `/to-spec`。
- `to-spec` — 把会话上下文 / 仓库事实 / 想法压成紧凑 PRD + 执行 spec，可按需切成可独立认领的 issue 分片或问卷。
- `implement` — 按 spec / tickets 实现，过程中在预定 seam 上使用 `/tdd` 与 `/vdd`，完成后走 `review` skill 评审。
- `tdd` — 红-绿-重构循环 + 深模块 / 接口设计 / mocking / 重构参考。（模型可调）
- `vdd` — 验证驱动开发：以可执行证据为控制面，四种治理模式（Characterization / Construction / Equivalence / Calibration）、oracle 资格审查、独立验收与证据 attestation。（模型可调）

### 重型工作流

- `code-migration` — 代码库级迁移：语言移植、同栈升级、strangler 重写的分类、领域工件、阶段闸门与交接；验收委托给 `vdd`（Equivalence / `large_equivalence`），局部实现与修复委托给 `tdd` / `diagnosing-bugs`。执行运行时假定外部 Missions 系统，无 Missions 时按 SKILL.md 的降级路径征询用户。
- `eng-init` — Agent Engineering Readiness Control Plane：bootstrap / audit / repair 仓库级 agent 控制面（AGENTS.md、CONTEXT.md、统一命令入口、验证分层、决策记录生命周期、机械 guardrails）。控制面审计（七层 / AGENTS.md 约束维度）也归它。与本仓 `project-instruction-bootstrap` 分工固定：项目用后者的生成模式（有 `instructions/agents/` 源）时 eng-init 把段落写进源再重生成；否则 eng-init 直接写 `AGENTS.md`，后者只增量补段并为 Claude Code 桥接 `CLAUDE.md`（一行 `@AGENTS.md`）。
- `self-evolution` — 可度量工件（prompt、skill、代码、配置、实验）的变异-评估-门控自主进化循环，支持 GT 用例集、标量指标循环与成对偏好循环。eval 工作区放 `workspaces/self-evolution/`。

### 独立工具

- `visual-design` — 视觉设计工程：先定页面形态（转化 / 任务 / 判断 / 叙事 / agentic）与任务级设计契约，再填领域内容与语义组件、补全 loading/empty/error/permission 等非 happy-path 状态，**最后**才做排版配色；交付前跑四层证据（标记有效性 → 主路径行为 → 截图观感 → 契约语义），缺陷按 spec/domain/shape/components/system/craft/implementation 归因并回到对应阶段修。六种模式：create / explore / tweak / review / system-bound / agentic。
  - 上游名为 `design`，导入时改名以避开 Claude Code 内置的 `design`（画布 Artifact）以及各类软件架构 `design` skill——三者同名但不同轴。本 skill 只管视觉产物，软件架构走 `architecture-design`。
  - 其输出契约默认写"cwd 里一个可运行的 HTML 文件"。若要改走 Claude Code 的画布 Artifact（`.dc.html` 多画板），需要自行调整该节。
- `reverse-skill` — 逆向工程路由器：APK / JS 签名 / 二进制 / 固件 / CTF / API 安全 / 渗透测试任务路由到包内子 skill 与工具工作流。仅用于授权的安全测试与研究场景。

## Dependencies On Repo Skills (not bundled)

- `grill-me` — `architecture-design` 的访谈协议来源（模型可调，已满足）。
- `review` — `implement` 的完成后评审出口。
- `diagnosing-bugs` — `code-migration` 有界工作单元内的修复方法。
- `stage-change-pipeline` / `improve-codebase-architecture` — `architecture-design` 的下游分流目标（上游 `/wayfinder` 槽位本仓库暂无对应，改走 `stage-change-pipeline` 的 fog 两节）。
- `project-instruction-bootstrap` — `eng-init` 在生成型项目里的根指令写入机制（可选，同一项目两者按上述分工并存）。

## Install

```bash
node scripts/install.js pack stellarlink --target <project> --platform claude-code
```
