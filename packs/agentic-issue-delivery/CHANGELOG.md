# Changelog

All notable changes to this pack will be documented in this file.
This project adheres to [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
