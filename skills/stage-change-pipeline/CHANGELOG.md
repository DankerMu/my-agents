# Changelog

All notable changes to this skill will be documented in this file.
This project adheres to [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.7.0] - 2026-06-18
- Stage 3 review contract now draws the finding's failure type from the `risk-adaptive-cross-review` `finding-contract.md` Failure-Class Vocabulary (including the spec classes `design-consistency`/`spec-completeness`/`task-executability`) and applies its Reject precision gate so vague, unanchored, or style-only items become notes instead of P0/P1.
- Add an **Oracle Integrity** constraint to the Stage 4.5 verification gate: the source design docs, implementation plan, and Stage 1 stage goals/acceptance criteria are the immutable oracle; fixes edit the OpenSpec change, never the artifacts that judge it. A genuine source-design change routes back through `brainstorming`/`future-aware-architecture` and is recorded, never silently rewritten to clear a finding.
- Add a **completion self-audit (premature-completion guard)** as a Stage 4.5 exit precondition: before entering Stage 5, re-derive each Stage 1 stage goal and acceptance criterion and confirm every requirement maps to a spec requirement plus task with no dropped design goal/boundary and no internally contradictory fix — an uncovered requirement returns to Stage 4 instead of passing on "looks done". Adapted from stellarlinkco/skills `harness`/`code-review` (clean-room, with author permission).

## [0.6.0] - 2026-06-18
- Add a cross-run "Loop Accountability" section (meta-loop dimension 6): a committed, append-only catch-rate log (`docs/stage-pipeline-log.jsonl`) records per-run `gate_net_catch` (findings the independent Stage 4.5 verifier overturned that Stage 3 review and `openspec status` missed), rounds, residuals, regressions, and cost.
- Define a kill criterion (≥5-run minimum sample; retire or narrow the gate if `gate_net_catch` ≈ 0) and a ratchet rule (promote a finding-class recurring across ≥2 runs into a permanent openspec/lint/CI check), so the gate keeps earning its cost and resolved issues become invariants.
- Scope explicitly to organizational accountability only — no Reflexion-style cross-change learning — to avoid importing bias across unrelated changes.

## [0.5.0] - 2026-06-18
- Harden Stage 4.5 trigger reliability (meta-loop dimension 8): forbid skipping straight from Stage 4 to Stage 5, require per-round acknowledgement tokens (`round <N>: started` / `verdict ...`) as auditable proof the gate ran, and honestly document that a portable doc-skill cannot install a host-repo pre-commit/pre-PR hook — per-project skip-rate stays an audited open question.
- Rework severity gating (meta-loop dimensions 1 + 4): P0 is the blocking band that drives the loop; P1 becomes a non-blocking carry band — still fixed opportunistically each round but no longer blocks exit or forces extra rounds. Exit gate is now "P0 cleared + P1 resolved-or-carried-to-issue", removing the prior "until clean" non-convergence smell.

## [0.4.0] - 2026-06-18
- Replace the single review→fix pass with a bounded verification loop: Stage 4 now resolves both P0 and P1 findings, and a new Stage 4.5 independent verification gate adversarially confirms each finding is resolved (default `unresolved` without evidence) and delta-scans for regressions in touched artifacts.
- Loop back to Stage 4 while any P0/P1 stays `unresolved`/`regressed`, capped at 3 rounds; on cap or convergence, residual findings are recorded into the issue body with a `needs-followup` marker instead of being silently dropped.
- Add the `verifier` subagent (`verify-review-fixes`) as a Stage 4.5 dependency that must not be the fixer; update pipeline diagram, skip strategy, and quick reference accordingly.

## [0.3.0] - 2026-06-15
- Add `grill-with-docs` as the Stage 2 domain-modeling pass: align terminology against `openspec/glossary.md` and persist long-lived decisions to `docs/adr/` while writing design/specs.

## [0.2.0] - 2026-06-15
- Integrate the `grill-me` skill as an optional pre-OpenSpec design stress-test gate between Stage 1 and Stage 2.
- Migrate Stage 3 review execution from the `codeagent`/`codeagent-wrapper` CLI to the orchestrator's native parallel subagents (`reviewer`), aligning with `subagent-workflow`. Drop `codeagent-wrapper` from requirements and the `codeagent` tag.
- Rename stale references from `codex-codeagent-workflow` to `subagent-workflow` (dependency note, When-Not-To-Use, implementation-ready contract, quick reference).

## [0.1.0] - 2026-05-25
- Initial canonical package for the stage-change pipeline.
- Converts design-stage context into OpenSpec changes, parallel Codex review, fixes, and fine-grained GitHub issues.
- Includes small-PR issue splitting rules based on module, ownership, dependency, and verification boundaries.
- Documents how Stage 3 aligns with `risk-adaptive-cross-review` OpenSpec review semantics.
- Documents reuse points for `clarify`, `future-aware-architecture`, `implementation-planning`, `project-documentation`, and `gh-create-issue`.
- Adds an Implementation-Ready Issue Contract so downstream implementation workflows should not need requirements clarification.
- Requires `Implementation Ready: yes` on generated sub-issues before they can enter `codex-codeagent-workflow`.
