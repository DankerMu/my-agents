# Skill Map

Routing guide for skills adjacent to this workflow. Consult when deciding whether an adjacent skill applies; canonical-vocabulary relationships are binding, the rest is routing advice.

## Canonical vocabulary sources (consume, never fork)

- `risk-adaptive-cross-review`: reviewer packs, risk-triage levels, the actionable finding contract, failure-class synthesis. This workflow only binds them to OpenSpec fixture levels, the `Invariant Matrix`, and the omp task scaffolding in `phase-4-cross-review.md`. Use the standalone skill directly for a risk-adaptive review outside Phase 0-8.
- `diagnosing-bugs`: diagnosis vocabulary (feedback loop, red-capable command, minimal repro, falsifiable hypotheses), consumed at the Phase 2/5/6/8 diagnosis binding points — the orchestrator inlines the distilled diagnosis brief into omp `implementer` tasks, since delegated omp sessions run with `--no-skills` and cannot load it. Use the standalone skill directly for interactive debugging.

## Substrate

- `subagent-workflow`: the all-native sibling of this skill — identical phases, gates, and evidence rules, with every leaf task running as a Claude Code Task / Codex subagent instead of an omp session. Use it when omp or `codeagent-wrapper` is unavailable, or when a run should not cross process boundaries. The two are not meant to be mixed inside one PR.
- `codeagent`: the wrapper contract itself (backends, agent presets, skill injection, parallel task DSL, structured output). `omp-delegation.md` pins the subset this workflow uses; consult `codeagent` when the wrapper's own behavior is in question.

## Upstream

- `stage-change-pipeline`: turns design-stage documents into reviewed OpenSpec changes and fine-grained GitHub issues before implementation begins. Owns scope clarity, acceptance criteria, and PR boundary (see Upstream Contract in `SKILL.md`).
- `control-plane-auditor` (from the `codebase-stewardship` pack): further upstream when the host repo lacks a control plane — instruction files, unified command entry points, verification infrastructure. Its bootstrap scaffolds the command entry points and verification matrix that Phase 0.0 records in the project profile.

## Alongside

- `implementation-planning`: non-interactive execution-strategy aid when the accepted issue/fixture is clear but the path needs staged rollout, rollback, dependency ordering, or PR split strategy. Never for discovering or negotiating product scope.
- `review`: focused artifact review when the work does not justify multi-perspective cross-review.
- `review` (consistency mode): follow-up checks specifically about consistency, naming drift, error-model splits, or pattern duplication.
- `git-worktree-workflows`: user-facing worktree guidance or recovery only; parallel code-writing isolation inside this workflow stays governed by `parallel-worktree-delegation.md`.
- `project-documentation`: docs-set refresh, docs drift checks, or source-of-truth cleanup outside the PR evidence summary.

## Within this workflow

- Phase 4 and follow-up review rounds use `phase-4-cross-review.md` — the OpenSpec instantiation only (omp task scaffolding, `Invariant Matrix` binding, Phase 4.5 verifier).
- Every delegation's mechanics — invocation, model pins, brief assembly, boundary, parallel batches, failure classification — live in `omp-delegation.md`, and Phase 7 is the documented native exception. Reviewer-pack scope, per-reviewer checklists, cross-cutting lenses, and the finding contract are inlined from `risk-adaptive-cross-review` (`reviewer-packages.md`), not redefined.
