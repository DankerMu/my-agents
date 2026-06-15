# Agentic Issue Delivery Pack

## Purpose

This pack bundles the repository's design-to-issue and issue-to-PR delivery workflow skills into one installable unit. It is intended for projects that want a two-step automated delivery path:

1. `stage-change-pipeline`: design documents and implementation plans become reviewed OpenSpec changes plus implementation-ready GitHub issues.
2. `subagent-workflow`: implementation-ready issues become reviewed, verified PRs with CI and merge gates, delegating implementation/review/verification to the `implementer`, `reviewer`, and `verifier` subagents.

## Included Skills

- `stage-change-pipeline`
- `subagent-workflow`
- `risk-adaptive-cross-review`
- `codeagent`
- `gh-create-issue`
- `clarify`
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
- `deep-research`

## Included Agents

This pack installs the three worker subagents that `subagent-workflow` delegates to:

- `implementer` — implements features, fixes, refactors, and tests from a spec/plan/brief; push-free (the orchestrator owns commit/push/PR).
- `reviewer` — risk-adaptive cross-review plus read-only fixture and final review.
- `verifier` — independent Phase 4.5 finding verification (CONFIRMED/PLAUSIBLE/REFUTED).
- `explorer` — read-only codebase investigation that `reviewer` spawns for deeper context.

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

The pack membership is explicit. It includes local support skills that the two main workflows route to or reference. `subagent-workflow` delegates to the bundled `implementer`, `reviewer`, and `verifier` subagents instead of an external code-agent CLI. The `codeagent` skill remains bundled as optional documentation for the `codeagent-wrapper` CLI; it is no longer required by the delivery path.
