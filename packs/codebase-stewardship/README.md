# Codebase Stewardship Pack

## Purpose

把代码健康治理的几条轴打成一个可安装单元，用于**周期性或按需的代码健康审查与改进**——区别于 `agentic-issue-delivery` 的"issue → PR 一次性交付流水线"。三条轴共用同一套对抗式对话（grill）与领域沉淀（`openspec/glossary.md` + `docs/adr/`）：

- **深化模块**：`improve-codebase-architecture` 基于"深模块"哲学找出 shallow modules，产出可视化 HTML 评审并 grill 落地。
- **治乱删冗**：`repo-entropy-audit`（全仓库六轴扫描）、`entropy-review`（每次变更）、`control-plane-auditor`（控制面/自动化熵）。
- **定方向**：`future-aware-architecture` 形成可逆性与长期演进的架构决策输入。

## Included Skills

- `improve-codebase-architecture` — 深模块架构评审：explorer 扫描 → deletion test → HTML 报告 → grilling loop。
- `repo-entropy-audit` — 全仓库熵治理：六轴扫描、模块热力图、基线趋势、优先级清理。
- `entropy-review` — 每次变更的熵评审。
- `control-plane-auditor` — 控制面 / 配置 / 自动化的熵审计。
- `future-aware-architecture` — 架构方向、技术选型、可逆性与长期演进决策。
- `grill-with-docs` — 领域压测 + 术语/决策沉淀到 `openspec/glossary.md`、`docs/adr/`。
- `grill-me` — 轻量对抗式计划/设计压测。
- `blind-spot-pass` — 动手前的盲区侦察：对陌生模块做代码库考古（历史/范式/隐形约定/危险区/邻接面），挖 unknown unknowns 并产出更好的任务 prompt；grill-me 的反向箭头。
- `clarify` — 需求/范围澄清；各审计 skill 的 when-not-to-use 分流目标，grill 之前先把模糊需求收敛。
- `gh-create-issue` — 审计发现的落地出口：`improve-codebase-architecture` 与 `repo-entropy-audit` 在结论确认后经它把高优先级目标变成可追踪 issue。

## Included Agents

- `explorer` — 只读 codebase 侦查，`improve-codebase-architecture` 的 Explore 步骤执行者。

## Included Hooks

- `large-file-guard` — 提交时的大文件机械闸：`git commit` 触碰到超过 1000 行（可配）的文本文件即拒绝并把清单喂回模型。增量棘轮：只检查本次提交触碰的文件，存量大文件由 `repo-entropy-audit` 治理，本 hook 保证新债务不再进入历史。`.large-file-guard.json` 可调阈值/排除/关闭。

## Install

```bash
npx my-agents install pack codebase-stewardship
npx my-agents install pack codebase-stewardship --platform codex --scope project
```

## Notes

- 与 `agentic-issue-delivery` **刻意重叠**：`entropy-review`、`repo-entropy-audit`、`future-aware-architecture`、`grill-with-docs`、`grill-me` 同时服务交付流水线（作支撑）与本包（作核心）。skill 在 my-agents 里是引用而非拷贝，重叠维护成本≈0。
- 沉淀落点统一为本仓库约定：领域术语 → `openspec/glossary.md`，长期决策 → `docs/adr/`（格式见 `grill-with-docs` 的 `GLOSSARY-FORMAT.md` / `ADR-FORMAT.md`）。`grill-with-docs`、`improve-codebase-architecture` 直接读写两处；`future-aware-architecture` 的 ADR seed 默认落 `docs/adr/`；熵套件认 `openspec/glossary.md` 为术语权威，量化基线另落 `.entropy-baseline/`（只读快照，不属领域沉淀）。
- 审计发现不止步于报告：`improve-codebase-architecture` 与 `repo-entropy-audit` 在用户确认后主动提议 `gh-create-issue`（本包内）或 `stage-change-pipeline`（随 `agentic-issue-delivery` 安装）把目标变成交付工作项。
- `improve-codebase-architecture` 会把 HTML 报告写到系统临时目录，不落进 repo；其 grilling loop 需要一个支持原生 subagent 的编排器（Claude Code Task subagents 或 Codex subagents）。

## 搭配 `research-engineering`

[`research-engineering`](../research-engineering/README.md) 决定科学对象、过程表示、研究协议、证据边界与人工科学结论；本包治理这些结论落入代码后产生的结构与语义熵。对于积雪模块、陆气耦合、数值方法或数据产品等研究驱动变更，`research-engineering-handoff` 里的科学不变量、单位/状态语义、证据 oracle 和未完成的验证义务是本包不可擅自改写的上游合同。

治理可以改变模块边界、依赖方向、代码组织和测试性，但若重构会改变科学状态、方程、过程顺序、单位、守恒或有效域，必须回到新的 research decision，而不能以“代码更整洁”为由直接修改。`research/project-profile.md` 保存科学权威，`openspec/project-profile.md` 保存软件风险/验证面；熵治理主要读后者，但涉及科学语义时必须引用前者与 handoff。

完整关系见 [Research Engineering flow](../../docs/architecture/research-engineering-flow.md)。

## 搭配 `agentic-issue-delivery`

本包决定"改什么"并守住健康基线，[`agentic-issue-delivery`](../agentic-issue-delivery/README.md) 把改进落成 reviewed PR，两者构成闭环：交付产生的新代码再回到本包的下一轮体检。共用 `openspec/glossary.md` + `docs/adr/` 单一事实源、grill 决策底座，以及作为交付内守门的 `entropy-review`。

完整工作流见 [交付 + 治理 搭配指南](../../docs/architecture/delivery-and-stewardship.md)。
