# Changelog

All notable changes to this pack will be documented in this file.
This project adheres to [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2026-07-29

### Changed

- 移除 `grill-with-docs`（并入 `grill-me` 0.5.0 的 docs 模式）。research 流水线的领域压测 + glossary/ADR 沉淀改用 `grill-me` docs 模式（pressure-test 契约 token 由 `grill-with-docs` 改为 `grill-me:docs`）。skills 由 17 减为 16。

## [0.1.0] - 2026-07-10

- Initial research-engineering role pack with an open-axis research lifecycle rather than a closed task taxonomy.
- Adds project-local research profile bootstrap, research framing, study design, theory-to-code traceability, evidence synthesis, and a governed research-to-engineering handoff.
- Reuses `grill-me`, `grill-with-docs`, `blind-spot-pass`, `deep-research`, `future-aware-architecture`, `implementation-planning`, `meta-loop`, and existing read-only/research/monitor agents as delegated capabilities.
- Defines explicit coupling to `agentic-issue-delivery`, `product-manager`, and `codebase-stewardship` while keeping each pack independently installable.
