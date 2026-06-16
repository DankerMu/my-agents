# Changelog

All notable changes to this skill will be documented in this file.
This project adheres to [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-06-15
- Initial port of `improve-codebase-architecture`, adapted from `mattpocock/skills` (zh-CN reference `vinvcn/mattpocock-skills-zh-CN`).
- Deep-modules architecture review: explorer-subagent codebase sweep, deletion-test triage, a self-contained HTML report (Tailwind + Mermaid, before/after per candidate), then a grilling loop to land each deepening.
- Persistence localized to this repo's stack: domain terms in `openspec/glossary.md`, long-lived decisions in `docs/adr/`, reusing the `grill-with-docs` GLOSSARY-FORMAT.md and ADR-FORMAT.md discipline.
- Uses the orchestrator's native `explorer` subagent (Claude Code Task subagent or Codex subagent) instead of a hardcoded Explore agent type.
- Bundles references: LANGUAGE.md (architecture vocabulary), DEEPENING.md (dependency categories + seam discipline), INTERFACE-DESIGN.md (parallel "design it twice" subagents), HTML-REPORT.md (report scaffold).
