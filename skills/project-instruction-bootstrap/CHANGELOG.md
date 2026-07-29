# Changelog

All notable changes to this skill will be documented in this file.
This project adheres to [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.3.0] - 2026-07-29

### Changed

- **模板对齐上下文工程新规则，只播种不可推导内容**："项目速览"（技术栈/目录/标准命令）删除，改为"非显而易见的约定"（一行用途 + 非标准命令 + 禁区 + gotchas TODO）——可推导内容是目标项目每会话付费的死重与失同步源。
- **"已装能力"清单降级为路由纠偏**：shared 段只保留反直觉路由（subagent-workflow vs codeagent）与成对 pack 指向，清单指向 `my-agents.project.json`；已装能力简表移入 `codex.md` 段（Codex 无自动 skill listing，Claude 侧平台已自动载入 description，复述即双重计费）。
- **uv 条款改为条件写入**：扫描到 Python 才写，取消"无条件默认"——不为假设性未来付每会话租金，项目长出 Python 时重跑本 skill 补上。
- **Observable Completion 移出默认骨架**：改为用户点名才写入的可选段。
- 增量模式补充：追加缺失段时同样遵守"不可推导"内容准则。

## [0.2.1] - 2026-07-11

- Remove the body invocation-posture restatement; posture lives in frontmatter/description.

## [0.2.0] - 2026-07-11
- Mark the skill user-invoked: SKILL.md frontmatter now sets `disable-model-invocation: true`, enforcing the manual-first posture at the platform level. Claude Code drops the description from standing context and only explicit `/project-instruction-bootstrap` invocation reaches it; the Codex projection/install target moves to `.agents/skills-manual/` (skill-lifecycle-manager 0.10.0 tooling). Discoverability lives in the `ask-danker` router.

## [0.1.1] - 2026-06-16
- The portable skeleton carries a defensive Python->`uv` convention (no bare `python`/`python3`/`pip`, to avoid polluting the system/Homebrew Python on macOS) unconditionally — written even when the project currently has no Python — while other language toolchain conventions are added per detected stack.
- Templates and process steer execution orchestration to the installed `subagent-workflow` + native subagents (implementer/reviewer/verifier) and explicitly warn against defaulting to `codeagent` or the old `codex-codeagent-workflow` name.

## [0.1.0] - 2026-06-16
- Initial release: a post-install skill that bootstraps or aligns a target project's own `CLAUDE.md` / `AGENTS.md` after a pack is installed into it.
- Two modes: a recommended generation mode where the project keeps `instructions/agents/{shared,claude,codex}.md` sources and the skill itself acts as the generator (`CLAUDE.md = shared + claude`, `AGENTS.md = shared + codex`, with a do-not-edit header) — single source of truth for the shared section, zero drift, no scripts/hooks imposed on the business project; and an incremental-compat mode that respects existing hand-written root instructions (append-only, with optional migration to the source layout).
- Reads the target project's `my-agents.project.json` manifest (`platforms` / `packs` / `skills` / `agents`) plus the actual `.claude/`, `.agents/`, `.codex/` projections to decide which instruction files to touch and what installed capabilities to document.
- Writes three content blocks: project-own conventions (stack/commands/layout, inferred or left as explicit TODO), installed capabilities (packs/skills/agents with triggers and per-platform split), and the portable orchestration skeleton (Observable Completion, anti-entropy push-down, per-model calibration, project-local adaptation via `openspec/project-profile.md` / `glossary.md` / `docs/adr/`).
- Incremental and non-destructive: never overwrites existing instruction content; always presents a plan/diff before writing; does not touch the my-agents repo's own generated root instructions.
- Ships `references/instruction-templates.md` with CLAUDE.md / AGENTS.md skeletons and the shared-vs-platform section split.
