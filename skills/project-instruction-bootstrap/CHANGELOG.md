# Changelog

All notable changes to this skill will be documented in this file.
This project adheres to [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-06-16
- Initial release: a post-install skill that bootstraps or aligns a target project's own `CLAUDE.md` / `AGENTS.md` after a pack is installed into it.
- Two modes: a recommended generation mode where the project keeps `instructions/agents/{shared,claude,codex}.md` sources and the skill itself acts as the generator (`CLAUDE.md = shared + claude`, `AGENTS.md = shared + codex`, with a do-not-edit header) — single source of truth for the shared section, zero drift, no scripts/hooks imposed on the business project; and an incremental-compat mode that respects existing hand-written root instructions (append-only, with optional migration to the source layout).
- Reads the target project's `my-agents.project.json` manifest (`platforms` / `packs` / `skills` / `agents`) plus the actual `.claude/`, `.agents/`, `.codex/` projections to decide which instruction files to touch and what installed capabilities to document.
- Writes three content blocks: project-own conventions (stack/commands/layout, inferred or left as explicit TODO), installed capabilities (packs/skills/agents with triggers and per-platform split), and the portable orchestration skeleton (Observable Completion, anti-entropy push-down, per-model calibration, project-local adaptation via `openspec/project-profile.md` / `glossary.md` / `docs/adr/`).
- Incremental and non-destructive: never overwrites existing instruction content; always presents a plan/diff before writing; does not touch the my-agents repo's own generated root instructions.
- Ships `references/instruction-templates.md` with CLAUDE.md / AGENTS.md skeletons and the shared-vs-platform section split.
