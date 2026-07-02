# Changelog

All notable changes to this skill will be documented in this file.
This project adheres to [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.1] - 2026-07-02

### Changed
- Recognize `openspec/glossary.md` as the canonical domain glossary in constraint loading (step 1b), aligning naming-drift checks with the persistence convention maintained by `grill-with-docs`. AGENTS.md-level constraints remain supplementary.
- Add a dimension-to-axes mapping table to `entropy-checklist.md`: the review dimensions are the diff-granularity instantiation of the suite's shared six-axes vocabulary (owned by `control-plane-auditor`'s methodology reference). Dimension names stay as-is for findings; the axes are for cross-change aggregation and comparison with `repo-entropy-audit`.

## [0.1.0] - 2026-05-24

### Added
- Six-dimension entropy analysis: naming consistency, error handling consistency, dependency direction, documentation sync, state model, pattern duplication
- Severity grading system: E0 (Pattern Fork), E1 (Naming Drift), E2 (Structural Deviation), E3 (Doc Desync), Suggestion
- Constraint gap detection with handoff to control-plane-auditor
- Entropy checklist reference with detection patterns and false-positive guidance
