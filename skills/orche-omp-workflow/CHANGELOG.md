# Changelog

All notable changes to this skill will be documented in this file.
This project adheres to [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2026-08-08

### Added

- **`explorer` 成为第四个 omp 执行角色**，pin `sub-gpt/gpt-5.6-luna` + `--reasoning-effort max`。此前 skill 里只在 Phase 7 原生边界里提过 explorer 一句禁令，没有任何相位真正编排它。
- Phase 0.0 profile bootstrap 的仓库结构扫描：单包以上的仓库改为委派一个只读 omp `explorer` 任务采证，profile 字段仍由编排器写。
- Phase 0.5 影响面测绘：change surface 不明朗（陌生子系统／共享 helper／疑似多面爆炸半径／将要判 `high`/`broad-expanded`）时先跑一个只读 explorer，产出 producers / validators / storage / entrypoints / downstream / 失败回滚路径及其现有测试，喂给第 8-9 步的 Invariant Matrix 与边界清单。单文件且已了解的改动跳过。

### Changed

- explorer brief 多一条硬约束：**只报证据，不判风险等级、不提设计、不给实现建议**。带着结论回来的报告按越权处理——留证据、丢结论。fixture level / repair intensity / risk pack 始终是编排器的决定。
- `omp-delegation.md` 分工表、Model Pins、role header、只读边界一节同步；`SKILL.md` 前置条件、Core Rules、边界适用相位（新增 0.0）、相位骨架同步。

## [0.1.4] - 2026-08-08

### Changed

- `reviewer` 的模型改为 `sub-gpt/gpt-5.6-terra`（仍走 sub-gpt 渠道、仍是 `--reasoning-effort max`）；implementer/verifier 保持 `sub-gpt/gpt-5.6-luna`。Phase 4 / 6.5 的并行 reviewer 批量示例同步。

## [0.1.3] - 2026-08-08

### Fixed

- **纠正 effort 传递方式**：`--reasoning-effort` 并未被 omp backend 丢弃 —— wrapper 会把它翻译成 omp 的 `--thinking`（实测 `--model openai-codex/gpt-5.6-luna --reasoning-effort max` 生成 `--thinking max`，session 记录 `thinkingLevel=max`）。`--parallel` 的 `reasoning_effort:` 头同样生效。此前 0.1.0–0.1.2 写的"静默丢弃"是错的。

### Changed

- 三个角色的 pin 统一改为 `sub-gpt/gpt-5.6-luna` + `--reasoning-effort max`，模型与强度分开传。
- Model Pins 一节重写：明确"不要把 effort 写进 model 串"（`provider/model:effort` 只对 omp 权威列出的 provider 有效，网关自定义 provider 上会直接 `Model not found` 退出 1），以及"裸 pin 不带 effort 会静默落到 high"。
- 并行 task 头要求同时写 `backend` / `model` / `reasoning_effort` 三项；示例（Phase 1 单任务、worktree worker 批量、reviewer 批量）全部同步。
- 保留自查手段：`grep -h thinking_level_change ~/.omp/agent/sessions/*<project>*/*.jsonl`，并注明少数调用中未观察到 `--thinking` 输出、成因未定位，effort 不符按 degraded delegation 处理。

## [0.1.2] - 2026-08-08

### Fixed

- 修正 Model Pins 一节的错误说法：裸 pin（不带 `:effort`）**不会**继承 `~/.omp/agent/config.yml` 里 `modelRoles` 的 effort —— 那些 role 只在完全不传 `--model` 时生效；显式传 `--model` 而没有后缀时落到固定的 `high`。因此 implementer/verifier 的 `sub-claude/claude-opus-4-8` 实际跑在 `high` 而非 `max`，表格已如实标注。
- 新增自查方法：`grep -h thinking_level_change ~/.omp/agent/sessions/*<project>*/*.jsonl`，看实际生效的 thinking level 而不是你写下的那个。

## [0.1.1] - 2026-08-08

### Changed

- `omp-delegation.md` brief 组装新增第 4 步 **项目规则指针**：委派会话不加载 `AGENTS.md`/`CLAUDE.md`，且 wrapper 没有对应的注入通道（`--skills` 只补 skill，不补 rules），所以每个写代码的 brief 必须用路径指针把规则文件指给它。implementer 强制，只读角色可选。
- 明确 `--no-skills` 与 `--no-rules` 的性质差异：前者是职责划分（wrapper 独占 skill 注入，避免同一 skill 两个来源），后者是无补偿损失。
- 补充 `--auto-approve` 默认开启的后果：委派写任务没有审批闸，这是"写代码任务绝不指向父 PR worktree"的理由之一。

## [0.1.0] - 2026-08-08

### Added

- 从 `subagent-workflow` 0.31.0 派生：相位骨架、gate 体系（round ledger / 三轮 gate / 五轮天花板 / 跨 PR 记忆）、fixture 契约、finding 契约、Phase 4.5 verdict+disposition、pre-merge 硬闸、cross-run loop log 与打包的 Python 校验脚本全部原样继承，只替换执行基座。
- `references/omp-delegation.md`（新增，本 skill 的核心差异）：codeagent-wrapper `--backend omp` 的调用契约（实测 `omp -p --mode json --auto-approve --no-title --no-skills --no-rules --model <pin>`）、模型钉死表、role contract 注入顺序、omp delegation boundary、`--parallel` 批量任务 DSL、超时与失败分类（tooling failure 不计 review round）。
- Phase 7 显式保留为原生 cc/cx `reviewer` subagent，并写明理由：Phase 0.5–6.5 全部跑在同一引擎上，合并前最后一道闸必须换引擎，否则同源盲区会让 loop 收敛到"clean"。跑到 omp 上判为 gate failure。

### Changed

- Phase 0.5 fixture review、Phase 1 实现、Phase 4/6.5 交叉评审、Phase 4.5 验证、Phase 6 修复与诊断、Phase 6.2 不变量审计：全部改为 omp 会话委派，briefs 增加 role header + 契约条目 + operating-guide 路径指针。
- `phase-4-cross-review.md`：reviewer/verifier 模板改为 omp `--parallel` 形态；verifier 明确禁止 `resume` 产出候选的会话。
- `parallel-worktree-delegation.md`：worker 通过 `workdir:` 绑定到 orchestrator 建好的 `.worktrees/`，禁用 wrapper 自带的 `--worktree`；补充 worktree-guard hook 管不到委派进程内部的作用域说明。
- `skill-map.md`：新增 Substrate 节，标注与 `subagent-workflow`（全原生兄弟）和 `codeagent`（wrapper 契约来源）的关系。

### Known limitations

- 委派会话带 `--no-skills --no-rules`，不加载任何项目 skill、`AGENTS.md`/`CLAUDE.md` 规则或 agent 定义；角色定义完全依赖 brief 注入与 operating-guide 文件路径。
- reasoning effort 只能写进 model 串（`provider/model:effort`），`--reasoning-effort` 对 omp 后端被静默丢弃；且 `:effort` 后缀仅对本地 omp 模型缓存中权威列出的模型可解析，缓存为空的 provider 需退回裸 pin。
