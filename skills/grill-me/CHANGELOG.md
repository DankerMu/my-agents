# Changelog

All notable changes to this skill will be documented in this file.
This project adheres to [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.6.0] - 2026-09-05

### Changed

- **访谈节奏从"一次一问"改为"按前沿逐轮"**（同步 `mattpocock/skills` v1.2.x `grilling`）：前沿 = 前置决策都已定、现在就能问而不必猜的决策；一轮问完整个前沿，每题编号、固定格式（`❓ **Qn** - **标题**` / `➡️ 推荐答案`），用户答完后重算前沿再问下一轮；答案依赖本轮未答问题的留到后面的轮次。前沿为空才算问完。动机：一次一问在分支多的计划上轮次爆炸，且互不依赖的问题串行问是在浪费用户等待；逐轮前沿把并行度交还给决策树的依赖结构，收敛判据（铁律 7/8、逐分支清单）不变。
- 铁律 3 补充：环境事实可派子 agent 查且**不阻塞本轮**——只有依赖该事实的问题等结果。流程第 4 步给查询分级：单命令/单文件当场查，跨文件查询一轮合并派一个子 agent（防止一题一个子 agent 的默认路径）。
- 铁律 4 由"逐分支推进"改为"每轮重算前沿"；流程第 3/4 步与"输出"节同步改写。tag `one-question-at-a-time` → `frontier-rounds`。
- 已知同步点：`architecture-design` 引用的"design tree / frontier / question format"访谈协议自此与本 skill 一致；`stage-change-pipeline` 的 `grillGate` 凭证、研究流的委托压测措辞及其 canonical 合同 `research-lifecycle/references/pressure-test-contract.md` 同批更新。`eng-init` 的 Stage 2 grill 是它自己的问题库协议（带问题预算、`AskUserQuestion` 优先），不随本变更。

## [0.5.0] - 2026-07-29

### Added

- **合并 `grill-with-docs` 为本 skill 的 docs 模式**：领域增强四件事、术语/ADR 沉淀纪律与落点（`openspec/glossary.md`、`docs/adr/`）移入 `references/docs-mode.md`，`ADR-FORMAT.md`/`GLOSSARY-FORMAT.md` 迁至 `references/`。默认模式行为不变（只对话、不写文档）；docs 模式按触发词或领域复杂度显式升级。合并动机：两个 skill 的 description 高度近义，常驻 listing 里构成路由税，且 grill-with-docs 自述即为"grill-me 的领域增强变体"——变体应是模式，不是独立 skill。

### Changed

- `capabilities.filesystemWrite` 改为 `true`（docs 模式需要写 glossary/ADR）；categories 增加 `documentation`，tags 增加 `glossary`/`adr`/`domain-model`。

## [0.4.0] - 2026-07-17

### Added

- **铁律 8：嵌入工作流时退出判据不变**。实跑发现被 `stage-change-pipeline` 嵌入时压测强度塌缩——单独使用能追问很多轮，管道内两三问就"passed"。根因是目标竞争：管道内压测只是通往下一 stage 的闸门，模型的主目标是推进管道，最便宜的路径就是敷衍几问。铁律 8 明确：收敛判据与单独使用完全一致（分支收敛 + 用户确认），推进压力不是收敛信号，"问了几个问题"不构成完成。
- **收敛小结升级为逐分支清单**（分支 / 结论 / 由谁定：用户拍板或事实核查）：写不出这份清单 = 压测没跑完。清单直接充当 `full-pipeline` `grillGate` 凭证对象的数据源，使压测深度可被下游机械校验。

### Changed
- 泛化适用范围：压测靶子从软件 plan/design 放宽到**任何计划、决策或想法**（description 与开篇明确"不限软件"）；事实来源措辞从 codebase 泛化为**环境**（codebase、文档、数据、其它已有产物），铁律 #3、锚定靶子、交叉核对步骤同步改写，审讯技法不变。Adapted from `mattpocock/skills` 未发布 changeset `grilling-general-use`（post-v1.1.0）。

## [0.3.1] - 2026-07-11

- Remove the body invocation-posture restatement; posture lives in frontmatter/description.

## [0.3.0] - 2026-07-11
- Backport the upstream `mattpocock/skills` v1.1.0 `grilling` hardening. Non-negotiable #3 now splits **facts** (look them up in the codebase/docs) from **decisions** (put each one to the user and wait — never answer them yourself), closing the failure mode where grill-me running inside another workflow (e.g. `stage-change-pipeline`) treated "能查就别问" as license to decide autonomously.
- New non-negotiable #7: an explicit confirmation stop-gate — the plan is not enacted until the user confirms shared understanding has been reached. The convergence summary is a proposal, not a release; the Output section names this gate for downstream stages.
- Frontmatter description updated to carry the facts-vs-decisions split.

## [0.2.0] - 2026-07-06
- New non-negotiable #6 "说不清就要 reference": when the user can't articulate a preference on a branch (unknown knowns), switch to asking for a reference (doc / screenshot / source directory — source code is best) or suggest a disposable fake-data prototype, instead of asking a third time. Adapted from Thariq's "A Field Guide to Fable: Finding Your Unknowns".
- Branch-ordering criterion added to the decision-tree step: branches whose answer would change architecture, interfaces, data models, or user-visible flows are grilled first; pure implementation-detail branches go last or are skipped.
- Cross-referenced the new sibling `blind-spot-pass` (When Not To Use + relations): it digs the territory (codebase → questions) before a plan exists; grill-me interrogates the map (plan → questions). Run blind-spot-pass first in unfamiliar territory and feed its decision points in as grill branches.

## [0.1.1] - 2026-07-02
- Fix stale persistence path in `When Not To Use`: the sibling `grill-with-docs` writes `openspec/glossary.md` (+ `docs/adr/`), not `CONTEXT.md`.
- Correct wording that called `grill-with-docs` "上游": it is a same-repo sibling (`同仓的`); the true upstream is `mattpocock/skills`. Kept the genuine upstream reference where it describes the mattpocock original.

## [0.1.0] - 2026-06-15
- Initial port of the `grill-me` skill, adapted from `mattpocock/skills` (zh-CN reference `vinvcn/mattpocock-skills-zh-CN`) and localized to this repo's skill conventions.
- Adversarial plan/design stress-testing: walk the decision tree branch by branch, one question at a time, each question carrying a recommended answer; resolve from the codebase instead of asking the user when possible.
- Integrated into the `stage-change-pipeline` workflow as a pre-OpenSpec design stress-test gate between Stage 1 and Stage 2.
- Scoped to conversation only: no document writes. The CONTEXT.md/ADR persistence of the upstream `grill-with-docs` variant is intentionally excluded.
