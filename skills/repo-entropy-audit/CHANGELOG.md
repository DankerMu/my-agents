# Changelog

All notable changes to this skill will be documented in this file.
This project adheres to [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2026-07-02

### Added
- Findings-to-delivery handoff in Phase 3d: after the user confirms cleanup priorities, offer `gh-create-issue` for direct cleanup issues or `stage-change-pipeline` for targets that need a reviewed OpenSpec change first. Audits previously stopped at report-only recommendations.
- Recognize `openspec/glossary.md` as the canonical domain glossary in constraint loading (Phase 1d), aligning the semantic axis with the persistence convention maintained by `grill-with-docs`.

## [0.1.0] - 2026-05-24

### Added
- Six-axis entropy scanning: structure, semantics, behavior, context, protocol, control
- Module-level heatmap output with color-coded scores and priority ranking
- Baseline snapshot management with trend comparison
- High-spread pattern detection with replication risk ranking
- Prioritized cleanup target list with tool recommendations
- Scan dimensions reference with shell-based detection methods per axis
