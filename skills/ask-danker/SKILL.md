---
name: ask-danker
description: 本仓库 skills 的路由器——按你当前的处境指路：该用哪个 skill、走哪条流、下一步交给谁。手动调用（/ask-danker），模型不会自动触发。
disable-model-invocation: true
invocation_posture: manual
version: 0.7.0
---

# Ask Danker

你不需要记住每个 skill——问这张地图。一条**流**是穿过若干 skill 的路径：大多数工作走一条主流，几条 on-ramp 汇入它，其余是独立工具或跑在底下的治理层。每条路由是"你现在的处境"，不是 skill 简介；细节以各 skill 自己的 SKILL.md 为准。

## 主流：想法 → 交付

1. **方向还没选** → `brainstorming`（探索/对比方向）；**需求含糊、验收标准缺失** → `clarify`。
2. **压测已选的方向** → `grill-me`（对话式逼清决策，默认不写文档；需要同时对齐术语、沉淀 `openspec/glossary.md` 与 ADR 时用其 docs 模式）。**任务进入陌生领域、计划还不存在**时先跑 `blind-spot-pass` 从代码库挖出你没想到要问的问题。
3. **需要产品文档** → `prd-authoring`（方向已定才进，产出可评审的 PRD）；**生意本身还没论证**（商业模式、市场、财务）→ `business-plan`（在 PRD 之前）。
4. **设计变交付物** → `stage-change-pipeline`：设计文档 → OpenSpec change → 三路并行审核 → 修复与独立验证门 → implementation-ready GitHub issues。它内部按需调用 `implementation-planning`、`future-aware-architecture`、`grill-me`（docs 模式）、`gh-create-issue`。
5. **实现 issue** → `subagent-workflow`（单 issue 全周期：实现 → PR → 交叉评审 → 合并；多 issue 按 DAG 顺序逐个跑它）。想把实现/评审/验证压到 omp（oh-my-pi）上跑、只留 Phase 7 终审在原生 subagent → `orche-omp-workflow`（同一套相位与闸门，只换执行基座；需要 `codeagent-wrapper` + omp 可用）。
6. **评审，二选一**：单遍 diff/PR/staged 评审、或只关心一致性漂移/命名/模式重复 → `review`（后者走其 consistency 模式）；高风险、多视角、不变量/状态机聚焦 → `risk-adaptive-cross-review`。

## On-ramps（汇入主流的起点）

- **方向已定、要深执行计划**（跨子系统、迁移、回滚路径）→ `implementation-planning`。
- **架构方向、技术选型、可逆性权衡** → `future-aware-architecture`。
- **只是要把需求变成 GitHub issue** → `gh-create-issue`（含 Epic/子 issue 拆分与宽改造 expand–contract 切法）。
- **出了毛病、原因不明**（难缠 bug、性能回归、修了又复发、CI 挂但本地复现不了）→ `diagnosing-bugs`：先建红色反馈回路后假设，确诊后修复回所在工作流；`subagent-workflow` 的修复环节内部也消费它。原因已确诊只差动手的修复不必进——直接修。
- **多后端 AI 代码任务（Codex/Claude/Gemini 执行）** → `codeagent`。

## Stellarlink 流（证据驱动交付；除注明外均手动调用）

来自 `stellarlink` pack 的另一条交付链，与主流平行；重叠处按下述分界选：

- **新项目定架构 / 存量架构审计** → `architecture-design`（用 `grill-me` 的访谈协议逐轮推进，落定决策记 ADR）；greenfield 产出接 `to-spec`，brownfield 深化接 `improve-codebase-architecture`。
- **把想法/会话上下文压成紧凑 PRD+执行 spec、切可认领 issue 分片** → `to-spec`（要正式可评审 PRD 走主流的 `prd-authoring`）。
- **拿着 spec/tickets 直接动手实现** → `implement`（内部在预定 seam 用 `tdd`/`vdd`，完成后走 `review`；要 issue→PR 全周期编排走主流 `subagent-workflow`）。
- **测试先行的红-绿-重构** → `tdd`（**模型可调**——被 `implement`/`code-migration` 运行中调用）。
- **以可执行证据治理开发**（oracle 资格审查、独立验收、证据 attestation）→ `vdd`（**模型可调**——同上）。
- **代码库级迁移**（语言移植、同栈升级、strangler 重写）→ `code-migration`（验收委托 `vdd`，局部修复委托 `tdd`/`diagnosing-bugs`；假定外部 Missions 运行时，缺席时按其降级路径征询）。
- **仓库 agent 就绪 bootstrap/审计/修复** → `eng-init`（与 `project-instruction-bootstrap`/`control-plane-auditor` 职能重叠，同一目标项目二选一）。
- **可度量工件的变异-评估-门控进化循环** → `self-evolution`（eval 工作区在 `workspaces/self-evolution/`）。
- **要做出界面/原型/落地页/仪表盘/deck 这类视觉产物** → `visual-design`：先定页面形态与设计契约，再补齐非 happy-path 状态，最后才做排版配色，交付前跑四层证据。软件架构设计走上面的 `architecture-design`，别混。
- **逆向工程 / APK / 二进制 / 固件 / CTF / 渗透（仅授权场景）** → `reverse-skill`（包内自带子 skill 路由）。

## 仓库健康（多为手动调用）

- `repo-entropy-audit` — 全仓六轴熵体检，产出优先级清单（变更集级的一致性评审走 `review` consistency 模式）。
- `control-plane-auditor` — 控制面审计：CLAUDE.md/AGENTS.md、hooks、生成物、指令一致性。
- `improve-codebase-architecture` — 深模块机会扫描；选中的候选回到主流第 2 步压测。
- `project-documentation` — docs 漂移检查与刷新。
- `project-instruction-bootstrap` — 安装 pack 后对齐目标项目的根指令文件（安装命令会提示这一步）。
- `editorial-review` / `readme-craftsman` — 文档编辑评审 / README 打磨。

## 研究流

- `research-lifecycle` 是研究控制面的路由器，按需编排：`research-profile-bootstrap`（研究档案）→ `research-question-framing`（问题定型）→ `study-design`（实验设计）→ `scientific-evidence-synthesis`（证据合成）→ `theory-to-code-traceability`（理论-代码追溯）→ `research-engineering-handoff`（交给工程）。从 `research-lifecycle` 进，别直接凑叶子。
- `deep-research` — 独立的多源、带引用的深度研究报告（web 检索）。
- `meta-loop` — 昂贵或安全关键的评估/证据循环的元审计。

## 治理 / 元

- `skill-lifecycle-manager` — skill 的创建、验证、评测、投影、发布、审计全周期；深度生态调研委托 `skill-researcher`。
- `agent-lifecycle-manager` / `agent-architect` — agent 合约的同套治理 / 设计。
- `prompt-engineering` — 提示词与系统提示设计（知识型 skill，显式调用最可靠）。
- `hook-development` — Claude Code hooks 开发。
- `agentic-development` — 多 agent 系统的运行时调试与开发方法。
- `git-worktree-workflows` — worktree 并行开发的手动指引与恢复。

## 跨会话 / 阶段边界

上下文怎么处理只在**阶段边界**（"这一块干完了"的那一刻）决定，中途不决定——中途压缩会让 agent 丢线。到了边界按序自问，第一个"是"即停：

1. **能在本会话继续吗？** 下一阶段要把这一阶段当一手材料（压测 → 实现是标准情形：实现要的是推理原文，不是摘要），或剩余上下文够下一阶段用 → **继续**。零成本零损失，先排除它。
2. **这段上下文对下一步完全无关吗？** 探索、决策、死胡同都可弃 → **清空上下文**（Claude Code `/clear`，Codex `/new`）。最便宜的一步，但单向：清掉相关上下文就丢了"为什么"，读 diff 找不回来。
3. **有东西要随身带走吗？** 换 harness（Claude → Codex）、换目录/仓库、交给同事、把中途发现的 side task 分叉出去而不打断当前工作，以及 issue / 流水线工作流跨会话续跑（本会话结束后由新会话接手；round counter、gate 状态、尚未启动脚本的 grill 凭证只在会话记忆里）→ **`/handoff`**：把会话独有状态（已定决策、工作流计数器、已排除路径、下一步）压成可携带的交接文档，issue 工作流中写到 `.workplans/` 证据束旁，新会话第一条消息加载接续。没有东西在移动，就不需要它。
4. **任务能 AFK 跑吗？** 范围收得够紧、不需要你盯着 → 交给**子 agent**（自动评审是标准情形），本会话不动。
5. **其余情况 → 原生压缩**（Claude Code / Codex `/compact`，带一句指令说明下一阶段要保留什么）。它是默认项而非首选项：上面四问都更便宜或更精确；从它起手的失败模式是新会话对被摘要抹平的决策"自信地错"。

除"继续"外每一步都把一手材料换成二手摘要（信息有损、噪声更少、空间更多），所以第 1 问永远最先问。并行实现用 `git-worktree-workflows` 隔离工作区。

**要从一个主会话调度多个 issue、每个 issue 开独立子会话并行跑**（桌面端；子会话在 worktree 里跑 `subagent-workflow` 等，决策全部上行主会话仲裁，chip 点击即审批）→ `session-orchestrator`。单 issue 不必进——直接跑 `subagent-workflow`。

## User-invoked 清单

以下 skill 设了 `disable-model-invocation: true`——只能由你 `/name` 调用，模型不会自动触发，也不占常驻上下文：

`ask-danker`（本 skill）、`agentic-development`、`git-worktree-workflows`、`handoff`、`improve-codebase-architecture`、`project-instruction-bootstrap`、`prompt-engineering`、`control-plane-auditor`、`repo-entropy-audit`，以及 stellarlink pack 的 `architecture-design`、`to-spec`、`implement`、`code-migration`、`eng-init`、`self-evolution`、`reverse-skill`、`visual-design`（该 pack 仅 `tdd`、`vdd` 保持模型可调）。

> 维护约定：新增、改名、删除任何 skill，或改动上述任何流的走向时，必须回查本地图并更新——路由器撒谎比没有路由器更糟。校验器会检查每个 user-invoked skill 都出现在本地图中。
