---
date: 2026-05-24
topic: entropy-management-tooling
scope: deep
---

# Entropy Management 工具体系设计

## Problem

AI coding 会持续施加熵增压力。结构漂移、语义分裂、行为碎片化、上下文蒸发、协议不一致、控制规则失效——这些问题不是个别团队"写得不好"，而是 agent-first 开发范式的物理属性。

当前 my-agents 生态中没有专门针对仓库熵管理的工具。已有的 review、project-documentation、dependency-audit 等 skill 各自覆盖了部分维度，但缺少：

1. 一个统一的诊断框架，能系统性地评估仓库的熵状态
2. 一个专注于"变更是否引入新熵"的 review 机制
3. 一套方法论文档，指导用户如何构建 entropy-aware 的仓库控制系统

第一个真实受众项目是 heyi（heyi-co/heyi-next），一个 TypeScript 全栈 monorepo，已有重度基础设施（14 个 AGENTS.md、17 个 ADR、readonly guards、drift detection、22 个 CI workflow），但缺少系统性的熵诊断和预防机制。

## Approach

四个可交付物，分布在三个层次。

### 层次结构

```
方法论层（文档）
  └── entropy management methodology

预防层（融入 agent 工作流）
  ├── Skill: control-plane-auditor
  └── Skill: entropy-review

诊断层（独立触发）
  └── Skill: repo-entropy-audit
```

核心设计原则：

- **预防 > 纠错**：最高 ROI 的干预点在 agent 开始工作前（约束加载），不是写完代码后（事后检查）
- **每个工具独立可用**：不要求用户一次安装全部；组合后有增强效应但不强制
- **诊断先于修复，triage 先于 fix**：先说清楚问题（热力图 + 优先级），再决定是否/如何行动
- **和已有生态是补充关系**：不替代 review/project-documentation/dependency-audit，而是指向它们
- **平台无关核心 + 平台适配**：方法论和诊断框架不绑定 Claude/Codex 特定能力

## Design Overview

### 1. 方法论文档 — entropy management methodology

不是 skill，是参考文档，放在 pack 或 skill 内部。

内容：

- **六类熵的工程定义**：结构熵、语义熵、行为熵、上下文熵、协议熵、控制熵。面向实操者，从两篇文章浓缩，配工程示例。
- **七层控制栈检查清单**：Memory / Invariant / Protocol / Permission / Sensorium / Evaluation-GC / Governance 每一层应该有什么、怎么判断"站住了没有"。
- **Entropy-aware AGENTS.md 写作规范**：AGENTS.md 里应包含哪些约束信息才能有效降低 agent 引入的熵——glossary 引用、dependency rules、error model、naming conventions、doc freshness rules。标准结构模板 + 正反示例。
- **指标定义参考**：哪些指标值得跟踪、粗略计算方式、如何解读趋势。

受众：用 entropy audit 工具后想深入理解框架的人。

### 2. Skill: control-plane-auditor

审计目标仓库的"控制平面"健康度，给出针对性升级建议。

**核心工作流：**

1. 扫描：instruction files、docs/ 结构、schemas/、test infrastructure、CI、guards/validators
2. 诊断：按七层控制栈逐层检查覆盖状态
   - Memory：instruction files 完整性、docs 引用链连通性、关键模块 source of truth
   - Invariant：架构规则自动化执行率、schema/type 覆盖率、dependency direction lint
   - Protocol：计划模板、skill/runbook 存在性、non-trivial 改动 plan 覆盖率
   - Permission：readonly guards、低/高风险操作区分
   - Sensorium：测试覆盖、app 可启动性、日志/trace 结构化程度
   - GC：cleanup 机制、doc freshness 检查
   - Governance：仅提示，不自动评估
3. 输出：结构化报告
   - 每一层覆盖状态（covered / partial / missing）
   - 高优先级改进建议（按对"未来 agent 正确变更成本"的影响排序）
   - 缺失 AGENTS.md 约束维度的补充建议
   - 推荐使用的已有 skill（review、project-documentation、dependency-audit 等）

**触发方式**：手动触发。全科体检，不是每天做的事。

**和 agent-architect 的边界**：agent-architect 推荐"用什么 AI 工具"（agents、skills、MCP servers）；control-plane-auditor 审计"仓库控制系统本身够不够健壮"。一个看工具配置，一个看基础设施健康度。

### 3. Skill: entropy-review

基于 review skill 的思路，但专注于"变更是否引入新熵"。

**检查维度：**

- **命名一致性**：新标识符是否和项目 glossary / 已有命名模式一致
- **错误处理一致性**：新 error handling 是否遵循项目标准 envelope
- **依赖方向**：新 import/dependency 是否违反已知分层规则
- **文档同步**：改动是否影响 AGENTS.md 引用的行为或接口，docs 是否同步更新
- **状态模型**：是否引入新状态枚举/常量，且和现有定义不兼容
- **模式复制**：新代码是否在复制已被标记为"应回收"的旧模式

**前提**：目标仓库 AGENTS.md 里有 glossary、dependency rules、error model 等信息。如果没有，entropy-review 能力受限——这是 control-plane-auditor 的价值所在。

**触发方式**：手动触发（如 `/entropy-review`），面向 PR / diff / staged changes。

**和 review skill 的边界**：review 做通用代码审查（正确性、安全、性能、可维护性）；entropy-review 专注熵维度（一致性、漂移、碎片化）。两者可以在同一次 review 流程中先后调用，但不耦合。

### 4. Skill: repo-entropy-audit

全仓库级别的熵状态扫描和趋势报告。

**核心工作流：**

1. 深入代码层面扫描：
   - 结构熵：依赖图分析、SCC 检测、util/common 膨胀度、分层违规
   - 语义熵：命名多样性分析、状态定义分散度、概念簇识别
   - 行为熵：错误处理模式多样性、返回格式变体、边界行为不一致
   - 上下文熵：doc freshness、AGENTS.md 覆盖率、ADR 与代码一致性
   - 协议熵：instruction files 间一致性
   - 控制熵：规则执行覆盖率、GC backlog
2. 输出：
   - 按模块/目录的熵热力图（文本格式，标出高熵区域）
   - 趋势比较（和历史基线比较：哪些指标在上升/下降）
   - 高扩散风险坏模式列表（被多处复制的模式优先标出）
   - cleanup 优先级排序
3. 基线管理：
   - 首次运行生成基线 snapshot
   - 后续运行自动和基线比较

**触发方式**：手动触发（`/repo-entropy-audit`）或定期调度。建议频率：月度或大版本发布前。

**和 control-plane-auditor 的边界**：control-plane-auditor 检查"消防设施够不够"（控制系统本身），repo-entropy-audit 检查"有没有着火"（代码本身的熵状态）。

### 工具间协作关系

```
control-plane-auditor              repo-entropy-audit
  │                                  │
  │ "控制系统有这些缺口"              │ "代码有这些高熵区域"
  │                                  │
  ├──→ 建议补充 AGENTS.md            ├──→ 标出高优先级 cleanup 目标
  ├──→ 建议安装 review/              ├──→ 生成/更新 entropy 基线
  │    project-documentation/        │
  │    dependency-audit 等           │
  │                                  │
  └──→ entropy-review                │
       │                             │
       └── 基于 AGENTS.md 约束       │
           做 PR 级检查               │
                                     │
          ←── cleanup 优先级 ────────┘
               指导后续 refactor
```

闭环：control-plane-auditor 建立约束 → entropy-review 执行约束 → repo-entropy-audit 检查约束有效性 → 发现新问题回到 control-plane-auditor 更新约束。

## Decisions

| #   | Decision                                              | Alternatives Considered                     | Rationale                                                                                                                              |
| --- | ----------------------------------------------------- | ------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | 做独立 skill 而非 meta pack                           | Meta pack（含 meta skill 自动适配目标仓库） | Meta skill 的"生成定制配置"可能是伪需求——成熟项目维护者比工具更了解自己的项目，新手项目看不懂生成结果。独立 skill 更轻量、更容易验证。 |
| 2   | entropy-review 新建而非增强现有 review                | 在 review skill 中增加 entropy lens         | 保持现有 review 的稳定性。entropy-review 的前提条件（需要 AGENTS.md 中有 glossary 等约束）和 review 不同，耦合在一起会增加复杂度。     |
| 3   | 预防层（约束加载 + review）优先于诊断层（全仓库审计） | 先做全仓库审计、事后检查优先                | 预防 ROI 高于纠错一个数量级。agent 在写代码前就知道约束，比写完再告诉它"你错了"要高效得多。                                            |
| 4   | 方法论文档独立于 skill 逻辑                           | 方法论硬编码进 skill 执行逻辑               | 方法论仍在演化（从第一篇到第二篇已有大量修正），硬编码会导致每次演化所有 skill 都要改。文档独立、skill 引用文档。                      |
| 5   | 不做独立 agent（如 entropy-sweeper）                  | 后台 GC agent 自动生成 cleanup PR           | 当前优先级是诊断和预防，不是自动修复。自动修复的前提是诊断体系已经成熟稳定。先 crawl → walk → run。                                    |

## Assumptions

- heyi 项目的 AGENTS.md 体系可以作为 control-plane-auditor 的第一个测试用例
- entropy-review 的效果高度依赖目标仓库 AGENTS.md 中约束信息的质量
- 全仓库 entropy audit 的计算成本在 agent token budget 可接受范围内
- 方法论在未来 6-12 个月内仍会继续演化，工具设计需要容忍这种不稳定性

## Risks

| Risk                                              | Likelihood | Impact | Mitigation                                         |
| ------------------------------------------------- | ---------- | ------ | -------------------------------------------------- |
| entropy-review 因 AGENTS.md 约束不足而效果差      | High       | High   | control-plane-auditor 先行，帮用户补齐约束         |
| 全仓库 audit 结果太多太杂，用户不知道怎么行动     | Medium     | Medium | cleanup 优先级排序 + 和已有 skill 的 handoff       |
| 方法论大幅修改导致 skill 逻辑需要重写             | Medium     | Medium | 方法论和执行逻辑解耦，skill 引用文档而非硬编码框架 |
| 和 agent-architect / review 等已有 skill 边界模糊 | Low        | Medium | DDR 中已明确边界定义，安装文档中说明               |
| 指标定义在不同项目间不可比                        | High       | Low    | 不追求跨项目比较，只看单项目趋势                   |

## Non-Goals

- 不做自动修复 / cleanup PR 生成（留给未来的 entropy-sweeper agent）
- 不做跨仓库 / 跨项目的熵比较
- 不做实时监控 / dashboard（先做批量诊断）
- 不替代已有的 review、project-documentation、dependency-audit 等 skill
- 不把方法论硬编码为不可配置的固定规则

## Open Questions

- entropy-review 的检查维度应该多细？太粗则没价值，太细则 false positive 多
- repo-entropy-audit 的基线 snapshot 格式怎么定？需要在实际使用中迭代
- 全仓库 audit 的合理频率是什么？需要在 heyi 上实验
- 未来是否需要一个 Pack 把这几个 skill 打包？等验证后再决定
- control-plane-auditor 和 agent-architect 未来是否应该合并或建立更紧密的协作？

## Next Steps

1. 确认此设计方案
2. 按优先级实现：control-plane-auditor → entropy-review → repo-entropy-audit
3. 方法论文档和 skill 同步推进
4. 在 heyi 上验证效果
5. 根据验证结果迭代
