# Changelog

All notable changes to this pack will be documented in this file.
This project adheres to [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
