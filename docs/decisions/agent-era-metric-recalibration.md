---
date: 2026-05-24
topic: agent-era-metric-recalibration
scope: deep
---

# Agent 时代的工程指标重新校准

## Problem

Entropy management 工具体系的检查维度大量继承自人类时代的工程度量（文件行数、函数长度、注释密度、嵌套深度等）。这些度量中的许多实际上是对人类认知瓶颈的 proxy，在 agent-first 开发中已经失效或需要重新校准。如果不更新，工具会产出大量 false positive，用户会失去信任。

## Approach

基于人类 vs agent 的认知差异分析，将传统指标分为四类，并为每类确定替代方案。

核心原则：**衡量真实问题，而不是人类时代的 proxy。**

## Decisions

| #   | Decision                                                           | Alternatives Considered | Rationale                                                                                          |
| --- | ------------------------------------------------------------------ | ----------------------- | -------------------------------------------------------------------------------------------------- |
| 1   | 文件行数从独立指标降级为辅助信号，替换为"单文件 import 来源多样性" | 保持行数作为主指标      | Agent 读取速度与文件大小无关；真正的问题是职责混杂，而职责混杂通过 import 多样性比行数更准确地衡量 |
| 2   | 函数长度替换为"隐式依赖数量"                                       | 保持行数阈值            | Agent 可以处理长函数；真正让 agent 出错的是全局状态、副作用和闭包捕获，不是行数                    |
| 3   | 注释密度不再作为检查维度                                           | 保留注释密度检查        | Agent 从类型签名和 instruction files 获取约束信息，不依赖注释；过期注释反而是误导                  |
| 4   | 新增"模式传染风险"指标                                             | 不做                    | Agent 会机械复制仓库已有模式，坏模式的扩散速度比人类时代快得多；这是全新的 agent-era 风险          |
| 5   | 类型覆盖率提升权重                                                 | 保持原权重              | 类型签名是 agent 理解函数契约的主要通道；any/unknown 对 agent 的伤害比对人类更大                   |
| 6   | 全局状态/副作用升级为独立检查项，agents-md-spec 增加第七个约束维度 | 保持作为结构熵子项      | Agent 跨会话无记忆，无法口头传递"注意这个全局变量"；必须显式声明                                   |
| 7   | 区分 instruction file freshness vs 普通 doc freshness 权重         | 统一权重                | Instruction file 对 agent 行为的影响力远大于普通文档                                               |

## Assumptions

- Agent 的 context window 足够大，读取大文件不是瓶颈（token 成本是经济问题，不是认知问题）
- 人类仍然参与 review 和高层决策，不是纯 agent 系统
- 类型系统是 agent 理解代码意图的首要通道

## Risks

| Risk                               | Likelihood | Impact | Mitigation                                                      |
| ---------------------------------- | ---------- | ------ | --------------------------------------------------------------- |
| 放弃行数阈值后，极端大文件缺少预警 | Low        | Low    | 保留 1000+ 行文件作为辅助信号（informational，不作为 red flag） |
| "隐式依赖数量"难以自动化计算       | Medium     | Medium | 先用 global/mutable 关键字 grep 近似，后续迭代改进              |
| 模式传染风险指标的准确性未验证     | High       | Medium | 首版作为实验性指标，在 heyi 上验证后再调整                      |

## Non-Goals

- 不重新定义所有软件工程最佳实践
- 不取消对人类 review 友好性的考虑（人仍然需要读代码）
- 不追求所有指标的完美自动化

## Next Steps

1. 更新 scan-dimensions.md
2. 更新 agents-md-spec.md（增加第七个约束维度）
3. 更新 entropy-checklist.md
4. 更新 six-entropy-axes.md（增加 agent-era 说明）
