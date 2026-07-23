# Changelog

All notable changes to this pack will be documented in this file.
This project adheres to [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.14.0] - 2026-07-23

### Changed

- **上下游联合改版：`stage-change-pipeline` 0.16.0 + `subagent-workflow` 0.28.0/0.29.0 + `risk-adaptive-cross-review` 0.4.2**——pack 两条主干之间从单向交接升级为回路。上游 Stage 5 契约新增 `Suggested fixture level` 与 `Minimal mergeable slice`（下游 triage 与 Split rebuttal 的锚）；下游终局事件（round-ceiling 拆分/放弃/降档）回流为上游 sizing-retro，拆分子项重过 Stage 5 契约。下游同批新增 per-issue ceiling 记忆（`review_gate.py --issue` + `.review-gate-issues.json`）、终局记账行与子 PR 全覆盖、`loop_log_audit.py` keep/cut 裁决欠账检查、evidence_check gate-lock 与 loop-log 词表校验、分支尖一致性 merge 前置、fixture 修复两轮封顶、merge 后 `openspec archive` 认领；0.29.0 追加 P2 延期默认 + P1 顺风车（严重度配给复审轮），P0-P2 与 critical/major/minor 的显式 crosswalk 落 canonical finding-contract（0.4.2）。动机与实跑证据（SHUD-Harness 26 merges、xagent 双 ceiling 复盘）详见各 skill changelog。同批结构减重收尾：`subagent-workflow` 0.30.0 与 `stage-change-pipeline` 0.17.0 删除战史散文、Stage 细节下沉 references、手抄词表改 canonical 指针——行为契约零变化。

### Added

- 新增 hook 成员 `review-gate` 0.1.0：`subagent-workflow` 三轮硬门的机械派发拦截（锁定期间拒绝 implementer/reviewer 子代理派发），与 skill 0.21.0 打包的 `review_gate.py` 状态机 CLI 配套。引用完整性：由主干 skill `subagent-workflow`（Prerequisites 可选件 + Phase 4/5/8 挂接）直接引用，与 `worktree-guard` 同一"可选机械底座"模式。

## [0.12.0] - 2026-07-16

### Removed

- **成员瘦身（引用完整性判据，18 → 15）**：pack 承诺"每个成员被两条主干流程路由或引用"，按 backbone 引用数据执行：
  - `review`：交付流内评审是 `risk-adaptive-cross-review`；单遍轻评审与之并列只制造触发歧义（三个 review 类 skill 竞争同一意图）。独立安装仍可用。
  - `brainstorming`：主干对它的全部引用是反向路由（"方向没定别进流水线"）——出口路牌不是交付依赖；`ask-danker` 照常路由。
  - `repo-entropy-audit`：全仓周期体检归 `codebase-stewardship`（本就在那），交付流内健康门是 `entropy-review`；双 pack 挂名徒增成员维护。

### Changed

- `blind-spot-pass` 留任的前提兑现：`stage-change-pipeline` 0.13.0 把它正式接进 Stage 1（此前 0 引用、违反成员规则）。
- 配合 `subagent-workflow` 0.19.1 / `stage-change-pipeline` 0.13.0 的描述减重，pack 常驻上下文税约降 40%（成员切除 + 触发词枚举删除）。

## [0.11.0] - 2026-07-16

### Added

- 收入 `handoff` 0.1.0（user-invoked）：issue 工作流的跨会话续跑——`/handoff` 把会话独有状态（决策、round counter、gate 状态、已排除路径、下一步）压成交接文档写到 `.workplans/` 证据束旁，新会话加载接续；与 `git-worktree-workflows` 分别覆盖跨会话与并行两类续跑场景。

## [0.10.0] - 2026-07-14

- Add `diagnosing-bugs`（0.1.0，ported from `mattpocock/skills` v1.1.0）: 因未知失败的诊断纪律（红色反馈回路优先、红命令硬闸、可证伪假设、seam 纪律的回归测试）。`subagent-workflow` 0.14.0 在 Phase 2/5/6/8 以诊断闸门消费它（canonical 词汇技能模式，同 `risk-adaptive-cross-review`）；独立场景经 on-ramp 直接调用。

## [0.9.1] - 2026-07-10

- Document the upstream contract with the new `research-engineering` pack: only a human-approved `research-engineering-handoff` enters the design-to-issue pipeline, and its scientific invariants, oracle separation, later evaluation requirements, forbidden shortcuts, rollback and profile boundary must survive OpenSpec translation.

## [0.9.0] - 2026-07-06

- 新增 `blind-spot-pass` skill：开工前对陌生区域的盲区侦察（源自 Thariq《A Field Guide to Fable: Finding Your Unknowns》）。从代码库考古出发（git 历史、相似实现、隐形约定、危险区、邻接面）挖 unknown unknowns，产出带证据的盲区清单 + 改写后的更好 prompt + reference 清单；决策点喂 `grill-me`（0.2.0 起互相引用），隐形约定沉淀走 `grill-with-docs`，范围外的雷交 `issue-scribe`。

## [0.8.0] - 2026-07-06

- 新增 `issue-scribe` agent：范围纪律的机械出口——主线工作中顺手发现的 follow-up（顺带撞见的 bug、tech debt、被 defer 的评审发现）委派给它，只读取证、去重后提交一个结构化 issue（来源/问题/边界/解决思路/验收标准/元信息+readiness 判定），后续交付轮经正常 issue DAG 拾起。绝不自己修；一个观察至多一个 issue，过大则标 needs-triage 并推荐 `splitter`/`stage-change-pipeline`。

## [0.7.0] - 2026-07-06

- 新增 `monitor` agent（Claude haiku / Codex spark）：Phase 8 CI 等待等 harness 外部长任务的廉价看护——JobID/RunID 级完成检测、单次阻塞静默等待、只读。
- 新增 `worktree-guard` hook：并行 worktree 委派的写入纪律机械化，项目根声明 `.worktree-guard.json` 后拦截越界文件写入，未声明时为 no-op。
- README 补充 Included Hooks 节。

## [0.6.0] - 2026-07-02

- Remove `codeagent`: legacy documentation for the `codeagent-wrapper` CLI with zero live references from any other member since the 0.2.0 native-subagent migration. Install it separately if you still use that CLI. The `codeagent` pack tag is dropped with it.
- Remove `deep-research`: never wired into either backbone workflow (`stage-change-pipeline`, `subagent-workflow`); it was thematic filler in a delivery pack.
- Add a README "Versioning" section: the pack version tracks membership and pack-level docs only; member skills evolve on their own changelogs (the bundled backbones are currently at `stage-change-pipeline` 0.8.x / `subagent-workflow` 0.8.x).

## [0.5.1] - 2026-06-16

- Add a "Pairs With" section cross-linking `codebase-stewardship` and the delivery + stewardship pairing overview (`docs/architecture/delivery-and-stewardship.md`). Docs only; no membership change.

## [0.5.0] - 2026-06-15

- Add `grill-with-docs`: the domain-aware variant of `grill-me` (glossary alignment, concrete-scenario boundary probing, code cross-referencing) wired into `stage-change-pipeline` Stage 2. Persistence is localized to this repo's stack: ubiquitous-language glossary at `openspec/glossary.md`, long-lived ADRs at `docs/adr/`. Ported from `mattpocock/skills` (zh-CN reference `vinvcn/mattpocock-skills-zh-CN`).

## [0.4.0] - 2026-06-15

- Add `grill-me`: adversarial plan/design stress-testing (decision-tree interrogation, one question at a time, recommended answer per question) wired into `stage-change-pipeline` as a pre-OpenSpec design gate between Stage 1 and Stage 2. Ported from `mattpocock/skills` (zh-CN reference `vinvcn/mattpocock-skills-zh-CN`).
- `stage-change-pipeline` (now 0.2.0) migrates Stage 3 review execution to native parallel subagents (`reviewer`) and drops the `codeagent-wrapper` dependency; stale `codex-codeagent-workflow` references across bundled skills are renamed to `subagent-workflow`.

## [0.3.0] - 2026-06-14

- Add `repo-entropy-audit` (whole-repo entropy governance: six-axis scan, module heatmap, baseline trend, prioritized cleanup) for periodic health checks and pre-release hygiene. Complements the per-change `entropy-review` already in the pack.

## [0.2.0] - 2026-06-14

- Replace the `codex-codeagent-workflow` member with its renamed successor `subagent-workflow`, which delegates implementation, review, and verification to native subagents instead of an external code-agent CLI.
- Bundle the worker subagents the workflow depends on: `implementer`, `reviewer`, and `verifier`, plus their declared `explorer` dependency (previously the pack installed no agents).
- Update the pack description and notes: the delivery path no longer requires `codeagent-wrapper`; it requires a subagent-capable orchestrator (Claude Code Task subagents or Codex subagents). The `codeagent` skill remains bundled as optional CLI documentation.

## [0.1.0] - 2026-05-25

- Initial agentic issue delivery workflow pack.
- Bundles `stage-change-pipeline`, `codex-codeagent-workflow`, `risk-adaptive-cross-review`, and local planning/review/documentation support skills.
- Includes `codeagent` and `gh-create-issue` as canonical local support skills while documenting the external CLI prerequisites.
