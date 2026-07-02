# Changelog

All notable changes to this skill will be documented in this file.
This project adheres to [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.3.0] - 2026-07-02

### Changed
- Deletion test unified into one 4-step operational procedure: enumerate the module's callers, inline the implementation into each, judge three outcomes (消失 / 重现 / 集中迁移), then map to a report badge. SKILL.md, LANGUAGE.md, and the Explore step now share one vocabulary; the incompatible "删除会集中复杂性 = 信号" framing is removed.
- Explorer sweep is now a contract: SKILL.md step 1 hands the `explorer` subagent a compact brief (scan scope, friction question checklist, `file:line` evidence, observe-only) and a defined return shape `{ 区域/文件组, friction 观察, 证据 file:line, 影响半径 }`. Responsibility is split explicitly — the explorer only gathers evidence; the deletion test and depth judgment stay with the orchestrator.
- HTML report described honestly: "self-contained" becomes "单文件 HTML（样式与图表经 CDN 加载，查看时需要网络）", with an offline-degradation note in SKILL.md and HTML-REPORT.md.
- Report filename `<timestamp>` pinned to `YYYYMMDD-HHMMSS` (colon-free, Windows-legal).
- ADR proposal surfaces all three gates (难回退 / 无背景会困惑 / 真实权衡, all true) instead of paraphrasing one; still links ADR-FORMAT.md.

### Added
- Handoff on the trigger surface: SKILL.md frontmatter and skill.json descriptions note that a settled deepening can become a trackable work item via `gh-create-issue` / `stage-change-pipeline`.
- Mass-diagram annotation (HTML-REPORT.md): rectangle height encodes behaviour/leverage, not lines of code — do not fake depth by drawing the implementation tall.
- Note that Mermaid `securityLevel: "loose"` is only acceptable because report content is locally generated from repo paths; never feed it untrusted text.
- Nesting caveat (SKILL.md step 1 + INTERFACE-DESIGN.md): when the skill runs inside a subagent with no spawn capability, the explorer sweep and parallel design-it-twice degrade to inline sequential execution.
- "replace, don't layer" grilling bullet: on landing, replace the old shallow module and delete unit tests that existed only for the old structure.
- Drift-guard note "Canonical definitions: LANGUAGE.md" above the SKILL.md glossary block; "Design It Twice (or more)" now notes 3–4 alternatives.

## [0.2.0] - 2026-07-02

### Added
- Handoff step (Process step 4): once a deepening survives grilling and the user wants execution, route it out of the skill — `gh-create-issue` for a single well-bounded refactor, `stage-change-pipeline` for a batch that forms a stage. Closes the audit-findings-stop-at-recommendations gap; the skill's own scope stays "decide what and why".

## [0.1.0] - 2026-06-15
- Initial port of `improve-codebase-architecture`, adapted from `mattpocock/skills` (zh-CN reference `vinvcn/mattpocock-skills-zh-CN`).
- Deep-modules architecture review: explorer-subagent codebase sweep, deletion-test triage, a self-contained HTML report (Tailwind + Mermaid, before/after per candidate), then a grilling loop to land each deepening.
- Persistence localized to this repo's stack: domain terms in `openspec/glossary.md`, long-lived decisions in `docs/adr/`, reusing the `grill-with-docs` GLOSSARY-FORMAT.md and ADR-FORMAT.md discipline.
- Uses the orchestrator's native `explorer` subagent (Claude Code Task subagent or Codex subagent) instead of a hardcoded Explore agent type.
- Bundles references: LANGUAGE.md (architecture vocabulary), DEEPENING.md (dependency categories + seam discipline), INTERFACE-DESIGN.md (parallel "design it twice" subagents), HTML-REPORT.md (report scaffold).
