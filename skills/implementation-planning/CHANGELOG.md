# Changelog

All notable changes to this skill will be documented in this file.
This project adheres to [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.1] - 2026-07-11
- Tighten the description to a lean identity + explicit-invocation clause (slimming batch 2): this skill is reached by name — by the user or an orchestrating skill — so trigger vocabulary and negative boundary lists move out of standing context into the body/router. Body and behavior unchanged.

## [0.2.0] - 2026-07-06
- Phase ordering is now a review-attention allocation, not just a build order (adapted from Thariq's "A Field Guide to Fable"): within dependency constraints, front-load decision-dense phases — data models, type interfaces, user-visible flows — and push mechanical refactors and low-judgment work to late phases.
- `plan-structure.md`: each phase template gains a `Review attention` field (decision-dense — review closely / mechanical — skim) so plan consumers (`stage-change-pipeline` Stage 5, `subagent-workflow`) know where human attention belongs.

## [0.1.5] - 2026-07-02

### Added
- Added a `Pipeline Consumers` note naming the two downstream consumers and this skill's role for each: `stage-change-pipeline` (Stage 2 `tasks.md`, Stage 5 issue grouping) and `subagent-workflow` (execution-strategy aid).

## [0.1.4] - 2026-03-29

### Changed
- Extended the durable eval suite and eval notes so the newly required `Success criteria` contract is scored alongside current-state grounding, verification, and rollback handling.

## [0.1.3] - 2026-03-28

### Changed
- Added explicit `invocation_posture` and `version` frontmatter metadata so the canonical skill doc matches the repo's newer skill-package conventions.
- Replaced the platform-specific question-tool table with platform-neutral question-handling guidance in the canonical core.
- Aligned the planning contract, quality gate, and reusable deep-plan template around explicit `Constraints` and `Success criteria` sections.

## [0.1.2] - 2026-03-28

### Changed
- Made the direction-choice boundary stricter so explicit invocation still routes back to `brainstorming` when the user is choosing between options.
- Added guidance that local drafts, prior plan files, or model preference do not count as permission to skip the route-back step.

## [0.1.1] - 2026-03-28

### Changed
- Tightened the hard gate so the skill routes back to `brainstorming` when the direction is not chosen and to `clarify` when contradictions remain.
- Added explicit guidance for routing-only answers so the skill responds with a verdict and next step instead of opportunistically drafting a full plan.

## [0.1.0] - 2026-03-28

### Added
- Initial cross-platform canonical package for `implementation-planning`
- Manual-first deep technical planning workflow for complex features, refactors, migrations, and architecture changes
- Reusable deep-plan template and scope-challenge checklist in `references/plan-structure.md`
- Durable evaluation fixtures for plan-quality checks and trigger-boundary review under `eval/`
