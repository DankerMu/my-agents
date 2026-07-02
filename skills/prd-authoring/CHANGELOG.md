# Changelog

All notable changes to this skill will be documented in this file.
This project adheres to [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-07-02
- Initial release: PRD authoring for already-chosen directions. Intake gate (chosen direction, named user + problem evidence, success sketch) routes incomplete discovery upstream to `brainstorming`/`clarify`/`deep-research` instead of drafting on air.
- Lean (~1-2 pages) and Full (~3-6 pages) document depths; nine-section template with MoSCoW-prioritized requirements and Given/When/Then acceptance criteria.
- Quality bar + self-review checklist (testable Must criteria, decision-grade non-goals, measurable metrics, solution-free problem statement, owned open questions).
- Handoff to `gh-create-issue` (epic + sub-issues), `implementation-planning`, or `stage-change-pipeline`; recognizes `openspec/glossary.md` as the canonical term source when present.
- Fills the repo-level gap found in the product-manager pack audit: no PRD/requirements-authoring skill existed between discovery skills and backlog creation.
