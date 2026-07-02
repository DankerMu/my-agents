# Changelog

All notable changes to this skill will be documented in this file.
This project adheres to [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.1] - 2026-07-02

### Changed
- Declare the sharing contract at the top of `six-entropy-axes.md`: the six axes are the entropy suite's canonical abstract vocabulary (consumed by `repo-entropy-audit`, `entropy-review`, and this skill), while detection methods stay per-object — the repo scan, the diff review, and this skill's seven-layer control-system model instantiate the axes at their own granularity by design. Also qualify the `docs/decisions/agent-era-metric-recalibration.md` link as a repo-level doc not shipped with standalone installs.

## [0.1.0] - 2026-05-24

### Added
- Seven-layer control stack audit (Memory, Invariant, Protocol, Permission, Sensorium, Evaluation/GC, Governance)
- AGENTS.md constraint dimension audit (glossary, dependency rules, error model, naming conventions, doc freshness, state model references)
- Structured report output with coverage status, gap analysis, and prioritized improvement recommendations
- Shared methodology references: six entropy axes, seven-layer checklist, AGENTS.md spec, metric definitions
