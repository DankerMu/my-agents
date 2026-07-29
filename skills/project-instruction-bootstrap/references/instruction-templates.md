# CLAUDE.md / AGENTS.md 源与骨架模板

目标项目的两份根指令由**共享段**（逐字一致）+ 各自**平台差异段**组成。默认用生成模式：把内容拆进 `instructions/agents/` 三个源，由本 skill 拼接生成两文件。已有手写文件时走增量模式，逐段比对、只补缺失段。

**内容准则（比模板本身更重要）**：只写目标项目的会话**自己推导不出来**的东西。技术栈、目录布局、标准命令（`npm test`、`cargo build` 这类工具默认调用）都能从 manifest 和 `ls` 直接读出——写进根指令就是每个会话都在付费的死重，且命令一变就是文档失同步。该进来的是：一行项目用途、**非标准**命令（带特殊 flag、环境准备、非常规脚本名）、禁区与 gotchas、领域规则。能从扫描确定的填实，不确定的留 `<!-- TODO -->`，不臆造。模板默认中文，可按目标项目语言调整。

## 源文件结构（生成模式）

```
instructions/agents/
  shared.md   # 两平台共享主体（项目用途/非标准命令/禁区/路由纠偏/本地适配）
  claude.md   # Claude 平台增量（Claude Code Notes）
  codex.md    # Codex 平台增量（Codex Notes + 已装能力简表 + <对话风格>）
```

生成关系：

```
CLAUDE.md = shared.md + claude.md
AGENTS.md = shared.md + codex.md
```

生成物头部统一加 do-not-edit 标记（识别"是否已是生成物"也靠它）：

```md
<!--
Generated from instructions/agents/shared.md and instructions/agents/{claude,codex}.md
by the project-instruction-bootstrap skill. Edit those sources, then re-run the skill.
Do not hand-edit this file.
-->
```

## instructions/agents/shared.md（两平台共享，逐字进 CLAUDE.md 与 AGENTS.md）

```md
# {{Project Name}} — Agent 指南

{{一行：这个项目是什么、为谁服务}}

## 非显而易见的约定

<!-- 只留会话自己查不出来的条目；查得出来的不写 -->
- {{非标准命令：带特殊 flag / 环境准备 / 非常规脚本名的，写全；标准调用不写}}
- {{禁区："never do X"（如：不要动 generated/、不要直推 main）}}
<!-- TODO: 领域规则 / 不变量 / gotchas（"X 看着安全其实会 Y"，扫描无法确定，需人工补） -->

## 能力路由

- 已装清单见 `my-agents.project.json`（权威来源，不在此复述）。
- {{路由纠偏，只写反直觉的：如"执行编排走 `subagent-workflow` + native 子代理（implementer/reviewer/verifier），不要默认套 `codeagent`——它仅限确需 codex CLI 执行的场景"}}
<!-- 装了成对 pack（如 agentic-issue-delivery + codebase-stewardship）时，在此指向其搭配说明 -->

## 项目本地适配（living 文件，按需创建）

- `openspec/project-profile.md` — workflow 适配（入口/契约/风险轴）；`subagent-workflow` 首次运行可自动 bootstrap。
- `openspec/glossary.md` — 领域 ubiquitous language 单一来源；由 `grill-me` docs mode / `improve-codebase-architecture` 维护。
- `docs/adr/NNNN-slug.md` — 长期架构决策账本（三门槛：难回退 + 无背景会困惑 + 真实权衡）。

## 反熵约定

根指令保持精简。包/能力的操作细节下沉到各自 `SKILL.md` / pack `README.md` / `CHANGELOG.md`，不在本文件展开；子树需细化时就近新增 scoped 指令文件。
```

按扫描结果**有条件**追加到"非显而易见的约定"：

- 扫描到 Python（`pyproject.toml` / `requirements*.txt` / `*.py`）→ 加一条：`Python 一律用 uv（uv run、uv pip 等），禁止裸 python / python3 / pip`。**没有 Python 就不写**——不为假设性未来付每会话的租金；项目日后长出 Python 时重跑本 skill 补上。
- 其它语言工具链同理：只写扫描到的栈里**偏离默认**的纪律（如强制的 Node 包管理器、Rust toolchain pin）；工具默认行为不写。

## instructions/agents/claude.md（Claude 平台增量，仅进 CLAUDE.md）

```md
## Claude Code Notes

- 知识域类 skill（如 `prompt-engineering`、调试方法论）自动触发率低，优先显式 `/skill-name` 调用。
<!-- 仅保留与本项目实际装入能力相关的条目；Claude 会自动把已装 skill 的 description 载入上下文，不要在这里复述清单 -->
```

## instructions/agents/codex.md（Codex 平台增量，仅进 AGENTS.md）

```md
## Codex Notes

- 仓库级指令集中在根 `AGENTS.md`；子树需细化时新增 scoped `AGENTS.md`，勿膨胀根文件。
- Codex runtime 安装：skills → `.agents/skills/`，agents → `.codex/agents/`；改 canonical 后重装，勿编辑投影副本。

## 已装能力简表

<!-- Codex 没有自动 skill listing，这份简表是它的发现面；Claude 侧不需要（勿放 shared） -->
- {{skill-a}} — {{一句触发/用途}}
- {{skill-b}} — {{一句触发/用途}}

<对话风格>
自然段落写作，克制标题、列表与加粗。禁止在结尾进行"如果你…/需要我…/可以的话…"式追问。
</对话风格>
```

## 段落归属速查

| 段落 | 源文件 | CLAUDE.md | AGENTS.md |
|---|---|---|---|
| 项目用途 / 非显而易见约定 / 能力路由 / 本地适配 / 反熵 | `shared.md` | ✓ | ✓ |
| Claude Code Notes | `claude.md` | ✓ | — |
| Codex Notes + 已装能力简表 + `<对话风格>` | `codex.md` | — | ✓ |

## 可选段（用户点名才加，不进默认骨架）

- **Observable Completion**（`Execution Summary: agents=…; skills=…; tools=…; verification=…; limits=…`）：每轮输出税，仅在用户明确要可观测完工契约时写入 `shared.md`。

## 增量模式（已有手写根指令，无源）

不强制建源。逐段比对现有 `CLAUDE.md`/`AGENTS.md`，只**追加缺失段**、保留既有内容；shared 段尽力对齐两文件并注明这是无源退化方案。可向用户提议把现有内容拆进上述三源、转入生成模式。增量补段时同样遵守顶部内容准则——不往既有文件里添可推导内容。
