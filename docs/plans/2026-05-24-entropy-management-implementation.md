# Entropy Management 工具体系实现计划

## Goal

在 my-agents 仓库中实现三个 skill 和一套方法论文档，构成一个完整的仓库熵管理工具体系。第一个验证目标是 heyi 项目。

## Scope

- 三个 skill 包：`control-plane-auditor`、`entropy-review`、`repo-entropy-audit`
- 一套共享方法论文档（放在 `control-plane-auditor/references/` 下，其他 skill 引用）
- 在 heyi 项目上完成首次验证

## Not In Scope

- 不修改已有 skill（review、agent-architect、project-documentation 等）
- 不建 Pack（验证后再决定）
- 不做 entropy-sweeper agent
- 不对 heyi 做任何代码修改
- 不做 CI 集成、dashboard 或定期调度

## What Already Exists

### my-agents 仓库

- 成熟的 skill 包规范：skill.json schema、SKILL.md + CHANGELOG.md 约定、scaffolding 脚本、pre-commit hook、CI 验证
- 相关 skill：`review`（代码审查，四阶段工作流）、`agent-architect`（项目 AI 环境设计）、`project-documentation`（docs 目录治理）、`dependency-audit`（依赖审计）
- 成熟模式可复用：review 的分阶段工作流、severity grading、verdict decision table；agent-architect 的 routing table + multi-mode 设计

### heyi 项目（验证目标）

- 14 个 AGENTS.md（根 + 模块级，遵循统一 7 段模板：Owns / Do Not Edit / First Read / Common Tasks / Required Verification / Known Failure Modes / Escalate To HQ When）
- 17 个 ADR、readonly guards、drift detection、22 个 CI workflow、242 个测试文件
- 已有的控制基础设施：tools/doctor、tools/sync、tools/guards、tools/specs、eslint-plugin-heyi-design
- **缺失**：glossary（术语散落在 blueprint 中未在根 AGENTS.md 定义）、inter-package dependency rules、error model 定义、naming conventions、state machine overview、breaking-change criteria

## Constraints

- skill.json `name` = 目录名 = SKILL.md frontmatter `name`（三者必须一致）
- categories 必须来自 categories.json（可用：`review`, `coding`, `workflow`, `design`, `documentation`, `security`, `devops`, `productivity` 等 21 个）
- 每个 version 必须在 CHANGELOG.md 中有对应条目
- 必须通过 `npm test`（eslint + prettier + sync-instructions check + validate.js + unit tests）
- SKILL.md frontmatter `description` 是触发逻辑，不是营销文案

## Success Criteria

1. 三个 skill 通过 `npm test`，出现在 `dist/catalog.json` 中
2. `control-plane-auditor` 在 heyi 上产出可操作的七层控制栈健康报告
3. `entropy-review` 在 heyi 的一个真实 diff 上正确识别至少一个熵问题
4. `repo-entropy-audit` 在 heyi 上产出按模块的熵热力图和趋势基线

## Assumptions

- skill 通过标准 shell 工具（grep、find、wc、git 等）+ 文件读取即可完成大部分分析
- heyi 的 AGENTS.md 体系足够结构化，可以被程序化审计
- 方法论文档的迭代不会阻塞 skill 的首版交付

## Open Decisions

| # | Decision | Status | Notes |
|---|----------|--------|-------|
| 1 | 方法论文档放在哪个 skill 的 references/ 下 | 倾向 control-plane-auditor | 它是入口 skill，方法论文档被其他 skill 引用 |
| 2 | entropy-review 是否需要 `invocation_posture` | 倾向 manual-first | 不自动触发，手动调用 |
| 3 | repo-entropy-audit 的基线 snapshot 格式 | 需要实现时定义 | JSON？Markdown？取决于可读性 vs 可比较性 |

---

## Phases

### Phase 0: 共享方法论文档

**目标**：建立三个 skill 共用的知识基础

**交付物**：放在 `skills/control-plane-auditor/references/` 下的方法论文档

```
skills/control-plane-auditor/references/
  methodology/
    six-entropy-axes.md          # 六类熵的工程定义
    seven-layer-checklist.md     # 七层控制栈检查清单
    agents-md-spec.md            # Entropy-aware AGENTS.md 写作规范
    metric-definitions.md        # 指标定义参考
```

#### 文件 1: `six-entropy-axes.md`

从两篇文章浓缩，面向工具使用者（不是文章读者）。每类熵包括：

- 一句话定义
- 3-5 个具体工程信号（可观测的症状）
- 对应的检查手段（哪些 shell 命令/文件模式可以检测）
- 和其他熵轴的关联

六类：结构熵、语义熵、行为熵、上下文熵、协议熵、控制熵。

#### 文件 2: `seven-layer-checklist.md`

每一层包括：

- 这一层解决什么问题（一句话）
- "站住了"的标志（3-5 个可检查的条件）
- "没站住"的信号（对应的缺失/退化表现）
- 常见工具/实践（不绑定特定平台）

七层：Memory / Invariant / Protocol / Permission / Sensorium / Evaluation-GC / Governance。

#### 文件 3: `agents-md-spec.md`

最关键的新产出。定义 entropy-aware 的 AGENTS.md 应该包含哪些约束维度：

- **Glossary 引用**：关键业务术语的官方命名 + 禁用别名
- **Dependency rules**：模块间允许/禁止的依赖方向
- **Error model**：标准错误 envelope、错误码范围、边界行为约定
- **Naming conventions**：标识符命名规则（函数、类型、事件、API 操作）
- **Doc freshness rules**：哪些文档在代码修改时必须同步更新
- **State model references**：关键实体的状态机定义位置

对每个维度给出：为什么需要、怎么写、好示例/坏示例。

#### 文件 4: `metric-definitions.md`

不追求精确算法，给出每个指标的：

- 名称和含义
- 粗略计算方式（基于 shell 工具可实现）
- 怎么解读趋势（升/降/稳定各意味着什么）
- 使用哪些工具的输出作为输入

**验证**：文档内容自洽、引用关系正确、示例可理解。

**依赖**：无。这是其他所有 phase 的基础。

---

### Phase 1: Skill — control-plane-auditor

**目标**：审计目标仓库的控制平面健康度

#### 1.1 包结构

```
skills/control-plane-auditor/
  skill.json
  SKILL.md
  CHANGELOG.md
  references/
    methodology/           # Phase 0 的方法论文档
      six-entropy-axes.md
      seven-layer-checklist.md
      agents-md-spec.md
      metric-definitions.md
    audit-report-template.md    # 报告输出模板
```

#### 1.2 skill.json

```json
{
  "schemaVersion": 1,
  "name": "control-plane-auditor",
  "displayName": "Control Plane Auditor",
  "description": "Audit a repository's control plane health across seven layers (memory, invariant, protocol, permission, sensorium, evaluation, governance) and produce an actionable improvement report. Covers instruction-file completeness, rule enforcement coverage, doc freshness, test infrastructure, and agent readiness.",
  "version": "0.1.0",
  "maturity": "experimental",
  "categories": ["workflow", "documentation", "review"],
  "tags": [
    "entropy", "control-plane", "audit", "agents-md",
    "repo-health", "invariant", "governance"
  ],
  "authors": [{ "name": "Qiongyu Li" }],
  "entrypoints": {
    "skillDoc": "SKILL.md",
    "changelog": "CHANGELOG.md"
  },
  "requirements": {
    "tools": ["git"]
  },
  "capabilities": {
    "shell": true,
    "filesystemRead": true,
    "filesystemWrite": false
  }
}
```

注意：`filesystemWrite: false` — 这个 skill 只读，不修改目标仓库。

#### 1.3 SKILL.md 结构设计

**Frontmatter**：

```yaml
---
name: control-plane-auditor
description: >-
  Audit a repository's control-plane health and produce an actionable
  improvement report. Use when the user asks to "audit the repo",
  "check repo health", "assess control plane", "entropy audit for
  the control system", or wants to know what's missing in their
  instruction files, rules, and verification infrastructure.
  Do NOT use for code review, dependency audit, general documentation
  work, or when the user wants to review a specific PR or diff.
invocation_posture: manual-first
---
```

**Body 结构**（参考 agent-architect 的 multi-mode routing + review 的 phased execution）：

```
# Control Plane Auditor

## When To Use / When Not To Use
## Process Overview

## Phase 1 — Scan
  扫描目标仓库，收集：
  - 所有 AGENTS.md / CLAUDE.md / instruction files 的位置和结构
  - docs/ 目录结构和内容
  - schemas/、test infrastructure、CI 配置
  - 已有的 guards、validators、lint rules、hooks
  - package/module 结构

## Phase 2 — Diagnose
  按七层控制栈逐层评估：

  ### Memory Layer
  - instruction files 是否存在于所有关键目录
  - 引用链是否连通（AGENTS.md → docs/ → 源文件）
  - 是否有关键模块缺少 source of truth
  - doc freshness（最后修改时间 vs 代码最后修改时间）

  ### Invariant Layer
  - 架构规则是否被自动化执行（lint rules、structural tests、schema validation）
  - 依赖方向是否有 lint 或 guard
  - type coverage
  - readonly/generated 路径是否有 guard

  ### Protocol Layer
  - 是否有计划模板（docs/plans/ 或类似结构）
  - non-trivial 改动是否有 plan 痕迹
  - 是否有 skill/runbook（docs/runbooks/ 或类似结构）

  ### Permission Layer
  - readonly guards 是否存在
  - 高风险操作（DB migration、secret access、production deploy）是否有明确的审批/门控

  ### Sensorium Layer
  - 测试类型覆盖（unit / integration / e2e / contract）
  - app 可启动性（是否有 dev server / smoke test）
  - 日志/trace 结构化程度

  ### Evaluation / GC Layer
  - 是否有 cleanup 机制（doctor script、drift detection、stale doc check）
  - tech debt / cleanup backlog 是否可见

  ### Governance Layer
  - （仅提示，不自动评估）
  - 提示用户考虑：执行自治等级和需求自治等级的当前状态

## Phase 3 — Report
  输出结构化报告：

  ### 报告格式
  每一层：
  - 覆盖状态标签：✅ covered / ⚠️ partial / ❌ missing
  - 关键发现（具体文件和路径）
  - 改进建议（按影响排序）

  ### AGENTS.md 约束维度审计
  对比 agents-md-spec.md 中定义的六个维度：
  - 哪些维度在目标仓库的 AGENTS.md 中已覆盖
  - 哪些维度缺失
  - 缺失维度的补充建议（含模板/示例）

  ### Handoff 建议
  - 哪些已有 skill 可以帮助解决发现的问题
  - 建议的下一步操作优先级

## References
  - [Six Entropy Axes](references/methodology/six-entropy-axes.md)
  - [Seven Layer Checklist](references/methodology/seven-layer-checklist.md)
  - [AGENTS.md Spec](references/methodology/agents-md-spec.md)
  - [Report Template](references/audit-report-template.md)

## Caveats
```

#### 1.4 验证

- `npm test` 通过
- 在 heyi 上手动运行，确认：
  - Memory Layer 能正确识别 14 个 AGENTS.md
  - Invariant Layer 能发现 readonly guards 和 drift detection
  - 能正确报告缺失的 glossary、dependency rules、error model
  - 报告格式清晰可操作

**依赖**：Phase 0（方法论文档）。

---

### Phase 2: Skill — entropy-review

**目标**：PR/diff 级别的熵检查

#### 2.1 包结构

```
skills/entropy-review/
  skill.json
  SKILL.md
  CHANGELOG.md
  references/
    entropy-checklist.md        # 熵检查维度清单
```

#### 2.2 skill.json

```json
{
  "schemaVersion": 1,
  "name": "entropy-review",
  "displayName": "Entropy Review",
  "description": "Review code changes for entropy introduction: naming drift, error-model fragmentation, dependency-direction violations, doc staleness, state-model splits, and pattern duplication. Produces severity-graded findings focused on consistency and drift rather than correctness.",
  "version": "0.1.0",
  "maturity": "experimental",
  "categories": ["review", "coding", "workflow"],
  "tags": [
    "entropy", "review", "naming", "consistency",
    "drift", "error-model", "dependency"
  ],
  "authors": [{ "name": "Qiongyu Li" }],
  "entrypoints": {
    "skillDoc": "SKILL.md",
    "changelog": "CHANGELOG.md"
  },
  "requirements": {
    "tools": ["git"]
  },
  "capabilities": {
    "shell": true,
    "filesystemRead": true,
    "filesystemWrite": false
  }
}
```

#### 2.3 SKILL.md 结构设计

**Frontmatter**：

```yaml
---
name: entropy-review
description: >-
  Review code changes for entropy introduction: naming drift,
  error-model splits, dependency violations, doc staleness, and
  pattern duplication. Activate when the user asks for "entropy review",
  "consistency check", "drift check on this PR", "check if this change
  introduces new patterns", or wants a review focused on naming,
  error handling, or structural consistency rather than correctness.
  Do NOT activate for general code review (use review), full repo audit
  (use repo-entropy-audit), brainstorming, or implementation tasks.
invocation_posture: manual-first
---
```

**Body 结构**（参考 review 的四阶段工作流 + severity grading）：

```
# Entropy Review

## When To Use / When Not To Use
  - 和 review skill 的明确边界：review = 正确性/安全/性能/可维护性，
    entropy-review = 一致性/漂移/碎片化
  - 两者可以在同一流程中先后调用，但不耦合

## Prerequisites
  - 说明：效果取决于目标仓库 AGENTS.md 中的约束信息质量
  - 如果缺少 glossary / dependency rules / error model，明确告知用户
    "建议先运行 control-plane-auditor 补齐约束"

## Phase 1 — Scope
  确定 review 范围：
  - 自动检测：staged changes / PR diff / branch diff / specific files
  - 加载目标仓库的约束上下文：
    - 读取相关 AGENTS.md
    - 读取 glossary（如果存在）
    - 读取 dependency rules（如果存在）
    - 读取 error model（如果存在）

## Phase 2 — Analyze
  按六个维度扫描变更：

  ### 2a. 命名一致性
  - 新标识符和 glossary / 已有命名模式比较
  - 识别：同一概念的新叫法、风格不一致（camelCase vs snake_case 混用）
  - 参考 [entropy-checklist.md](references/entropy-checklist.md)

  ### 2b. 错误处理一致性
  - 新 error handling 和项目标准 envelope 比较
  - 识别：新的错误返回格式、不一致的 HTTP status 使用、静默吞错误

  ### 2c. 依赖方向
  - 新 import/require 是否违反分层规则
  - 识别：跨层直接调用、绕过 adapter、util 膨胀

  ### 2d. 文档同步
  - 如果改动影响行为或接口，相关 docs / AGENTS.md 是否同步更新
  - 识别：行为变了但文档没跟上

  ### 2e. 状态模型
  - 新枚举/常量/status 字段是否和现有定义兼容
  - 识别：影子状态机、重复定义

  ### 2f. 模式复制
  - 新代码是否在复制已知的"应回收"模式
  - 或者是否引入了和相邻模块不一致的新模式

## Phase 3 — Synthesize
  输出格式（参考 review skill 的 severity grading）：

  Severity 等级（适配熵场景）：
  - **E0 — 模式分叉**：引入新的错误模型 / 状态定义 / 返回格式，和项目标准直接冲突
  - **E1 — 命名漂移**：同一概念引入新叫法，或命名风格不一致
  - **E2 — 结构偏离**：依赖方向违规、分层穿透、util 膨胀
  - **E3 — 文档脱节**：行为变了但文档没跟上
  - **Suggestion**：不构成问题但可以改进一致性的建议

  每个 finding：
  - severity 等级
  - 位置（文件:行号）
  - 描述（具体说明偏离了什么）
  - 项目标准参考（如果能找到对应的 AGENTS.md 或 glossary 条目）

  Verdict：
  - ✅ 无熵问题（或仅有 Suggestion）
  - ⚠️ 有 E1-E3 发现，建议修复
  - ❌ 有 E0 发现，强烈建议在合并前修复

## Phase 4 — Recommend
  - 对每个 E0/E1 finding，给出具体的修复建议
  - 如果缺少约束上下文（glossary / error model / dependency rules），
    在报告末尾单独列出"约束缺口"，建议运行 control-plane-auditor

## References
  - [Entropy Checklist](references/entropy-checklist.md)
  - 引用 control-plane-auditor 的方法论：
    [Six Entropy Axes](../control-plane-auditor/references/methodology/six-entropy-axes.md)

## Caveats
```

#### 2.4 references/entropy-checklist.md

每个检查维度的详细 checklist：

- 具体的 grep/find 模式（怎么发现命名不一致、怎么发现新的 error envelope 等）
- 常见 false positive 及如何排除
- 和 AGENTS.md 约束维度的映射关系

#### 2.5 验证

- `npm test` 通过
- 在 heyi 上找一个真实 diff，运行 entropy-review，确认：
  - 能正确加载相关 AGENTS.md 约束
  - 能识别命名不一致或错误处理不一致
  - 报告格式和 severity grading 可操作
  - 在约束缺失时能正确报告"约束缺口"

**依赖**：Phase 0（方法论文档引用）。和 Phase 1 无强依赖，可并行开发。

---

### Phase 3: Skill — repo-entropy-audit

**目标**：全仓库级别的熵状态扫描和趋势报告

#### 3.1 包结构

```
skills/repo-entropy-audit/
  skill.json
  SKILL.md
  CHANGELOG.md
  references/
    scan-dimensions.md          # 每个扫描维度的具体方法
    heatmap-format.md           # 热力图输出格式定义
    baseline-format.md          # 基线 snapshot 格式定义
```

#### 3.2 skill.json

```json
{
  "schemaVersion": 1,
  "name": "repo-entropy-audit",
  "displayName": "Repo Entropy Audit",
  "description": "Scan an entire repository for entropy across six axes (structure, semantics, behavior, context, protocol, control) and produce a module-level heatmap, trend comparison against baseline, and prioritized cleanup targets. Use for periodic health checks or before major releases.",
  "version": "0.1.0",
  "maturity": "experimental",
  "categories": ["workflow", "review", "refactoring"],
  "tags": [
    "entropy", "audit", "heatmap", "baseline",
    "refactoring", "tech-debt", "cleanup"
  ],
  "authors": [{ "name": "Qiongyu Li" }],
  "entrypoints": {
    "skillDoc": "SKILL.md",
    "changelog": "CHANGELOG.md"
  },
  "requirements": {
    "tools": ["git"]
  },
  "capabilities": {
    "shell": true,
    "filesystemRead": true,
    "filesystemWrite": true
  }
}
```

注意：`filesystemWrite: true` — 需要写基线 snapshot 文件。

#### 3.3 SKILL.md 结构设计

**Frontmatter**：

```yaml
---
name: repo-entropy-audit
description: >-
  Full-repository entropy scan across six axes: structure (dependency graph,
  layering, SCC), semantics (naming diversity, state model fragmentation),
  behavior (error model variants, boundary handling), context (doc freshness,
  AGENTS.md coverage), protocol (instruction-file consistency), and control
  (rule enforcement gaps). Produces a module-level heatmap, trend comparison,
  and prioritized cleanup targets. Activate when the user asks for "entropy
  audit", "repo health scan", "heatmap", "tech debt scan", or "full entropy
  report". Do NOT use for PR-level review (use entropy-review) or control-plane
  audit (use control-plane-auditor).
invocation_posture: manual-first
---
```

**Body 结构**：

```
# Repo Entropy Audit

## When To Use / When Not To Use
  和 control-plane-auditor 的边界：
  - control-plane-auditor 检查"消防设施"（控制系统本身）
  - repo-entropy-audit 检查"有没有着火"（代码本身的熵状态）

## Phase 1 — Scope
  确定扫描范围：
  - 整个仓库 or 指定子目录/模块
  - 是否存在历史基线（查找 .entropy-baseline/ 或 docs/entropy/）
  - 识别模块/包的划分方式（monorepo packages、目录层级等）

## Phase 2 — Scan
  按六类熵轴逐一扫描：

  ### 2a. 结构熵
  - 依赖方向分析（import/require 语句 → 模块间依赖图）
  - 循环依赖检测（SCC 识别）
  - util/common/helpers 目录体积和被依赖度
  - 文件大小分布（超长文件识别）
  - 分层违规（跨层直接调用）
  - 参考 [scan-dimensions.md](references/scan-dimensions.md) § 结构

  ### 2b. 语义熵
  - 标识符多样性分析（同一语义簇的命名变体数）
  - 状态/枚举定义分散度（多少个文件定义了类似的 status/state/phase）
  - glossary 覆盖率（如果有 glossary，多少核心概念被覆盖）
  - 参考 [scan-dimensions.md](references/scan-dimensions.md) § 语义

  ### 2c. 行为熵
  - 错误处理模式统计（try-catch vs Result vs error code vs 静默返回）
  - API 响应格式变体数
  - 边界行为处理方式的多样性（null vs 空数组 vs 异常 vs 默认值）
  - 参考 [scan-dimensions.md](references/scan-dimensions.md) § 行为

  ### 2d. 上下文熵
  - AGENTS.md / instruction file 覆盖率（多少关键目录有 AGENTS.md）
  - 文档新鲜度（docs/ 文件最后修改时间 vs 对应代码最后修改时间）
  - ADR 和代码的一致性信号
  - 参考 [scan-dimensions.md](references/scan-dimensions.md) § 上下文

  ### 2e. 协议熵
  - instruction files 间的约定一致性
  - 不同模块的 AGENTS.md 是否遵循相同模板
  - CI workflow 间的约定一致性
  - 参考 [scan-dimensions.md](references/scan-dimensions.md) § 协议

  ### 2f. 控制熵
  - lint/guard/validator 的规则覆盖率
  - cleanup 机制状态（doctor script 最近运行时间、GC backlog）
  - 测试覆盖分布的均匀性
  - 参考 [scan-dimensions.md](references/scan-dimensions.md) § 控制

## Phase 3 — Synthesize
  ### 模块级热力图
  按模块/顶级目录聚合，每个模块在六个轴上打分：
  - 🟢 Low（该维度健康）
  - 🟡 Medium（有信号但不紧急）
  - 🔴 High（需要关注）

  输出为文本表格，参考 [heatmap-format.md](references/heatmap-format.md)

  ### 趋势比较
  如果存在历史基线：
  - 哪些指标在上升（⬆）/ 下降（⬇）/ 稳定（➡）
  - 哪些模块从 Low 变成了 Medium/High

  ### 高扩散风险模式
  识别被多处复制的坏模式（命名变体、错误处理分叉、依赖违规路径）：
  - 出现次数
  - 涉及文件列表
  - 预估扩散趋势

  ### Cleanup 优先级
  按 (扩散风险 × 修复难度) 排序：
  - 优先回收高扩散、低修复难度的问题
  - 对每个目标推荐使用哪个 skill 或工具

## Phase 4 — Baseline
  - 首次运行：生成基线 snapshot，写入 `.entropy-baseline/` 或用户指定位置
  - 后续运行：自动和最近基线比较
  - 基线格式参考 [baseline-format.md](references/baseline-format.md)

## References
  - [Scan Dimensions](references/scan-dimensions.md)
  - [Heatmap Format](references/heatmap-format.md)
  - [Baseline Format](references/baseline-format.md)
  - 引用 control-plane-auditor 的方法论：
    [Six Entropy Axes](../control-plane-auditor/references/methodology/six-entropy-axes.md)
    [Metric Definitions](../control-plane-auditor/references/methodology/metric-definitions.md)

## Caveats
  - 全仓库扫描可能消耗较多 token/时间，大仓库建议按模块分批
  - 指标是趋势信号，不是绝对标准；重要的是方向而非精确数值
  - 热力图只标出"需要关注"的区域，不自动修复
```

#### 3.4 references/ 文件

**scan-dimensions.md**：每个扫描维度的具体实现方法

对每个维度：
- 具体的 shell 命令/grep 模式/文件扫描方法
- 怎么量化（计数、比率、分布）
- 已知局限和 false positive
- 针对不同技术栈（TypeScript/Python/Go 等）的适配说明

**heatmap-format.md**：热力图的输出格式模板

```
| Module         | Structure | Semantics | Behavior | Context | Protocol | Control |
|----------------|-----------|-----------|----------|---------|----------|---------|
| apps/api       | 🟢        | 🟡        | 🔴       | 🟢      | 🟢       | 🟡      |
| packages/db    | 🟢        | 🟢        | 🟡       | 🟡      | 🟢       | 🟢      |
| ...            |           |           |          |         |          |         |
```

加上各列的含义说明和阈值定义。

**baseline-format.md**：基线 snapshot 的 JSON 格式定义

```json
{
  "version": 1,
  "timestamp": "...",
  "repo": "...",
  "modules": {
    "apps/api": {
      "structure": { "score": "medium", "details": {...} },
      "semantics": { ... },
      ...
    }
  },
  "global": {
    "total_files": ...,
    "total_test_files": ...,
    "agents_md_count": ...,
    ...
  }
}
```

#### 3.5 验证

- `npm test` 通过
- 在 heyi 上运行，确认：
  - 能正确识别模块划分（apps/ + packages/）
  - 热力图中 apps/api 的行为熵标记为 high（已知错误 envelope 分裂）
  - 上下文熵能反映 AGENTS.md 覆盖率
  - 基线 snapshot 正确生成并可读

**依赖**：Phase 0（方法论引用）。和 Phase 1、Phase 2 无强依赖，可在 Phase 2 之后或并行。

---

### Phase 4: 集成验证

**目标**：在 heyi 项目上验证三个 skill 的闭环协作

#### 4.1 验证场景

1. **先跑 control-plane-auditor**
   - 预期：识别出 heyi 的 Memory Layer 和 Invariant Layer 较强，但 glossary/dependency rules/error model 缺失
   - 预期：报告建议补充 AGENTS.md 约束维度

2. **再跑 entropy-review on a real diff**
   - 找一个 heyi 的真实 PR 或构造一个 diff
   - 预期：能基于已有 AGENTS.md 做部分检查
   - 预期：对缺失约束维度能正确报告"约束缺口"

3. **最后跑 repo-entropy-audit**
   - 预期：产出 heyi 的模块级热力图
   - 预期：生成基线 snapshot

4. **验证闭环**
   - control-plane-auditor 的建议是否和 repo-entropy-audit 的发现一致
   - entropy-review 的"约束缺口"是否指向 control-plane-auditor 的报告

#### 4.2 验证后调整

根据验证结果迭代：
- 调整检查维度的粒度（太粗→加细，太细→合并）
- 调整 severity 阈值
- 修正方法论文档中的示例和建议
- 更新 CHANGELOG

---

## Implementation Sequence

```
Week 1:  Phase 0 (方法论文档)
         ↓
Week 2:  Phase 1 (control-plane-auditor)
         Phase 2 可并行启动
         ↓
Week 3:  Phase 2 (entropy-review)
         ↓
Week 4:  Phase 3 (repo-entropy-audit)
         ↓
Week 5:  Phase 4 (集成验证 on heyi)
```

每个 Phase 完成后立即 `npm run build && npm test`。

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| 方法论文档过长导致 token 成本高 | Medium | Medium | 保持文档简洁，skill 选择性加载 |
| heyi 的 AGENTS.md 结构特殊性导致 skill 过度适配 | Medium | High | 设计时考虑 heyi 以外的项目形态 |
| 全仓库扫描在大 monorepo 上太慢 | Medium | Medium | 支持按模块分批扫描 |
| 三个 skill 的边界在实际使用中模糊 | Low | Medium | SKILL.md 的 When To Use / When Not To Use 中明确边界 |

## Rollback / Containment

所有工作都是纯新增文件，不修改任何已有代码。如果任何 skill 出问题，直接删除目录即可。risk 极低。

## Next Step

按 Phase 0 → Phase 1 顺序开始实现。Phase 0 的四份方法论文档是所有后续工作的基础。
