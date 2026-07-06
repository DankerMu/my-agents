# Changelog

All notable changes to the **issue-scout** agent will be documented in this file.

## [0.1.2] - 2026-07-06

### Changed

- Add the `issue-agent-os` suppression tag: catalog visibility is now purely tag-driven. The old `issue-` directory-name-prefix rule in `catalog.js` (which existed only because this agent and `issue-solver` lacked the tag) is removed — it wrongly hid any future agent whose name legitimately starts with `issue-` (first victim: `issue-scribe`). No visibility change for this agent.

## [0.1.1] - 2026-06-14

### Changed

- Codex definition: reasoning effort `high` -> `xhigh` (model `gpt-5.3-codex-spark` unchanged).

## [0.1.0] - 2026-03-31

### Added

- Initial release: read-only issue context scout.
- Claude Code definition with Glob, Grep, Read, Bash(readonly) tools.
- Codex definition with read-only sandbox mode and gpt-5.3-codex-spark.
