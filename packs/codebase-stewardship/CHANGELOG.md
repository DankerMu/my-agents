# Changelog

All notable changes to this pack will be documented in this file.
This project adheres to [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-06-15

- Initial codebase stewardship pack: periodic/on-demand code-health governance, separate from the one-shot issue-delivery pipeline.
- Bundles `improve-codebase-architecture` (newly ported from `mattpocock/skills`), the entropy suite (`repo-entropy-audit`, `entropy-review`, `control-plane-auditor`), `future-aware-architecture`, and the shared grill base (`grill-with-docs`, `grill-me`, `clarify`), plus the `explorer` agent.
- Persistence is unified on this repo's stack: domain glossary at `openspec/glossary.md`, long-lived decisions at `docs/adr/`.
- Members intentionally overlap with `agentic-issue-delivery`; skills are references, not copies.
- README cross-links the delivery pairing overview (`docs/architecture/delivery-and-stewardship.md`) and `agentic-issue-delivery`.
