# Delivery + Stewardship：两个 pack 如何搭配

`agentic-issue-delivery`（交付）与 `codebase-stewardship`（治理）不是并列的两套工具，而是一个**闭环**：治理决定"改什么"并守住健康基线，交付把改动落成 reviewed PR，交付产生的新熵再回到治理。两者靠**共享底座**咬合，而不是各跑各的。

## 主线：治理 → 交付 → 治理

```
codebase-stewardship（决定做什么 / 守健康基线）
  repo-entropy-audit ─────┐  全仓库体检：熵清单 + 基线趋势
  improve-codebase-arch ──┤  深模块评审：HTML 报告 + deepening 决策
  future-aware-architecture┘  定方向：可逆性 / 选型
        │  产出：改进 backlog + 沉淀 glossary/ADR
        ▼
agentic-issue-delivery（把改进落成 reviewed PR）
  stage-change-pipeline   Stage 1-2：吃上面的结论 → OpenSpec change → 细粒度 issue
  subagent-workflow       issue → 实现 → cross-review → verified PR
        │  交付产生的新代码 = 新的熵
        ▼
   回到 codebase-stewardship 的下一轮体检
```

## 三个咬合点

1. **`openspec/glossary.md` + `docs/adr/` = 单一事实源。**
   治理阶段（`improve-codebase-architecture` / `grill-with-docs`）沉淀的术语与决策，交付阶段 `stage-change-pipeline` 写 design/specs 时直接遵守；交付阶段 `grill-with-docs` 新增的术语再回流。两 pack 读写同一份，不分叉。

2. **grill 系列 + `future-aware-architecture` = 共用决策底座。**
   `improve-codebase-architecture` 的 grilling loop 与 `stage-change-pipeline` 的 Stage 1 压测门禁 / Stage 2 领域建模是同一套 grill 机制。治理阶段 grill 出的 deepening 决策，可以无缝变成交付阶段的 design 输入。

3. **熵守门分内外两层。**
   - `entropy-review`（per-change）内嵌在 `subagent-workflow` 里，交付每次变更时实时守门。
   - `repo-entropy-audit`（全仓库）在交付之外周期性跑，产出下一轮治理 backlog。

## 什么时候用哪个

- **有明确任务**（实现某 feature / fix）→ 直接走 `agentic-issue-delivery`，治理只在内部（`entropy-review`）守门。
- **没有具体任务**（技术债盘点 / 发布前体检 /"这块架构该改了"）→ 先用 `codebase-stewardship` 产出改进 backlog + 沉淀 glossary/ADR，再转 `agentic-issue-delivery` 落地。

## 端到端示例：一处架构债的闭环

1. **体检**：`repo-entropy-audit` 周期扫描，热力图标出某模块为熵热点。
2. **诊断 + 定方案**：`improve-codebase-architecture` Step 1 用 `explorer` 扫描，`deletion test` 确认它是 shallow module；产出 HTML 评审，进入 grilling loop 定下 deepening 决策；新模块命名写入 `openspec/glossary.md`，被否决的替代方案（够三门槛）落 `docs/adr/`。
3. **转交付**：把 deepening 决策作为设计输入进 `stage-change-pipeline` Stage 1-2 → 生成遵守 glossary/ADR 的 OpenSpec change → 拆成细粒度、小 PR 边界的 issue。
4. **执行**：`subagent-workflow` 跑每个 issue —— `implementer` 实现 → Phase 4 cross-review（`reviewer` spawn `explorer` 深挖调用链）→ Phase 4.5 `verifier` 裁定 → `entropy-review` 守门 → verified PR。
5. **回流**：合并后的代码变化进入下一轮 `repo-entropy-audit`，闭环继续。

## 成员重叠说明

`entropy-review`、`repo-entropy-audit`、`future-aware-architecture`、`grill-with-docs`、`grill-me`、`clarify` 同时出现在两个 pack：在 `agentic-issue-delivery` 里作交付支撑，在 `codebase-stewardship` 里作治理核心。skill 在 my-agents 里是**引用而非拷贝**，重叠维护成本≈0，且保证两条线共用同一套定义。

一句话：**stewardship 出"该改什么"和"健康基线"，delivery 出"reviewed PR"，`openspec/glossary.md` + `docs/adr/` 是它们之间的合同。**
