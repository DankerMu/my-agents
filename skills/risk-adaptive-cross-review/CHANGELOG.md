# Changelog

All notable changes to this skill will be documented in this file.
This project adheres to [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2026-06-18
- Add a "Cross-Cutting Review Lenses" section to `reviewer-packages.md`: change-triggered lenses (removed-behavior audit, wrapper/proxy faithfulness, altitude/ownership) that named reviewers apply on top of pack scope, each tagged with owning reviewers, triggers, and failure classes, and bound to the existing finding contract. Adapted (clean-room, with author permission) from the stellarlinkco/skills `code-review` finder angles.
- Promote the detailed per-reviewer checklists into `reviewer-packages.md` as the canonical "Reviewer Checklists" (Correctness, Integration, Security/Performance, Test & Evidence, Spec Compliance, Invariant/State-Machine/Compatibility), so workflows inline them instead of forking their own copies. This is the single source `subagent-workflow` Phase 4 now consumes.
- Wire the lenses into `SKILL.md` reviewer-pack guidance and into the per-reviewer prompt requirements.

## [0.1.1] - 2026-06-15
- Update stale cross-reference: `codex-codeagent-workflow` -> `subagent-workflow` (skill renamed).

## [0.1.0] - 2026-05-25
- Initial risk-adaptive cross-review skill.
- Supports PR/diff/branch review and OpenSpec/stage-change review modes.
- Adds reviewer-pack selection, actionable finding contracts, and failure-class synthesis references.
