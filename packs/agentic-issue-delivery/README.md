# Agentic Issue Delivery Pack

## Purpose

This pack bundles the repository's design-to-issue and issue-to-PR delivery workflow skills into one installable unit. It is intended for projects that want a two-step automated delivery path:

1. `stage-change-pipeline`: design documents and implementation plans become reviewed OpenSpec changes plus implementation-ready GitHub issues.
2. `subagent-workflow`: implementation-ready issues become reviewed, verified PRs with CI and merge gates, delegating implementation/review/verification to the `implementer`, `reviewer`, and `verifier` subagents.

## Included Skills

- `stage-change-pipeline`
- `subagent-workflow`
- `risk-adaptive-cross-review`
- `gh-create-issue`
- `clarify`
- `blind-spot-pass`
- `grill-me`
- `grill-with-docs`
- `brainstorming`
- `future-aware-architecture`
- `implementation-planning`
- `review`
- `entropy-review`
- `repo-entropy-audit`
- `git-worktree-workflows`
- `project-documentation`

## Included Agents

This pack installs the worker subagents that `subagent-workflow` delegates to:

- `implementer` — implements features, fixes, refactors, and tests from a spec/plan/brief; push-free (the orchestrator owns commit/push/PR).
- `reviewer` — risk-adaptive cross-review plus read-only fixture and final review.
- `verifier` — independent Phase 4.5 finding verification (CONFIRMED/PLAUSIBLE/REFUTED).
- `explorer` — read-only codebase investigation that `reviewer` spawns for deeper context.
- `monitor` — cheap-model watchdog (Claude: haiku, Codex: spark) for harness-external waits such as CI runs during Phase 8; ID-based completion detection, quiet blocking waits, read-only.
- `issue-scribe` — follow-up capture for scope discipline: when primary work surfaces an out-of-scope finding (bug in passing, tech debt, deferred review finding), the orchestrator delegates the raw observation; issue-scribe verifies it read-only, dedups, and files one structured issue (来源/边界/解决思路/验收标准/readiness) that a later delivery run picks up via the normal issue DAG. Never fixes anything itself.

## Included Hooks

- `worktree-guard` — PreToolUse path guard that mechanically enforces the parallel-worktree write discipline `subagent-workflow` relies on. Installed everywhere but inert until the orchestrator declares `.worktree-guard.json` at the project root when entering worktree-delegation mode; blocked writes are denied with the reason fed back to the model.

## Install

```bash
npx my-agents install pack agentic-issue-delivery
npx my-agents install pack agentic-issue-delivery --platform codex --scope project
```

## Notes

External tools are still required by the workflows and are not installed by this pack:

- `openspec` CLI
- authenticated `gh` CLI
- `git`
- the target project's build/test toolchain
- a subagent-capable orchestrator (Claude Code Task subagents or Codex subagents)

The pack membership is explicit: every member is routed to or referenced by the two main workflows. `subagent-workflow` delegates to the bundled `implementer`, `reviewer`, and `verifier` subagents instead of an external code-agent CLI. The legacy `codeagent` skill (docs for the `codeagent-wrapper` CLI) is no longer bundled; install it separately if you still use that CLI.

## Versioning

The pack version tracks membership and pack-level docs only. Bundled skills evolve independently on their own changelogs (see `skills/<name>/CHANGELOG.md`, e.g. `stage-change-pipeline`, `subagent-workflow`); a member-skill release does not bump this pack.

## Pairs With: `codebase-stewardship`

This pack and [`codebase-stewardship`](../codebase-stewardship/README.md) form a loop: stewardship decides _what to improve_ and holds the code-health baseline; this pack turns those decisions into reviewed PRs, and the new code it produces flows back into the next stewardship pass. They share `openspec/glossary.md` + `docs/adr/` as the single source of truth, the grill skills as a common decision base, and `entropy-review` as the in-delivery health gate.

Full workflow: [Delivery + Stewardship pairing](../../docs/architecture/delivery-and-stewardship.md).
