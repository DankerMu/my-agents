# Changelog

All notable changes to this skill will be documented in this file.
This project adheres to [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2026-06-01
- Add Phase 4.5 independent finding verification gate, borrowing the find/verify separation from the `code-review` skill: Phase 4 reviewers now emit candidate findings, and a separate codeagent verifier adjudicates each deduped candidate as CONFIRMED/PLAUSIBLE/REFUTED before Phase 5.
- Make verification recall/precision bias follow the fixture level (`high`/`broad-expanded` keep PLAUSIBLE merge-blocking; `low`/`compact` block only on CONFIRMED); REFUTED candidates are dropped with recorded rationale and do not count toward the review round budget.
- Add a removed-behavior auditor checklist item to the Integration reviewer and a dedup step ahead of verification.
- Add the Phase 4.5 verifier template to `references/phase-4-cross-review.md`.
- Slim `SKILL.md`: collapse 16 review/fix-governance Core Rules (round budgets, hard gates, escalation, CI-only, large-PR staging) into 3 navigational non-negotiables that defer mechanics to `references/phase-flow.md`; always-loaded skill doc drops from 32 to 18 Core Rules (~20KB to ~13KB) with no loss of executable detail.
- De-duplicate review semantics: `risk-adaptive-cross-review` is now the canonical source for reviewer packs, the finding contract, and failure-class synthesis. This workflow references those definitions instead of hand-forking them; `references/phase-4-cross-review.md` is declared the codex/OpenSpec instantiation only.

## [0.1.0] - 2026-05-25
- Initial canonical package for the Codex + codeagent issue workflow.
- Adds OpenSpec fixture gates, risk-adaptive review/fix loops, parallel worktree delegation rules, PR evidence, CI, and human-gated merge guidance.
- Documents relationship to `risk-adaptive-cross-review` and upstream `stage-change-pipeline`.
- Documents reuse points for `implementation-planning`, `review`, `entropy-review`, `git-worktree-workflows`, and `project-documentation`.
- Keeps requirements clarification and issue-readiness checks out of this automated implementation flow; `stage-change-pipeline` owns those upstream.
