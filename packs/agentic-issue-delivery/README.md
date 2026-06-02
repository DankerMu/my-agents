# Agentic Issue Delivery Pack

## Purpose

This pack bundles the repository's design-to-issue and issue-to-PR delivery workflow skills into one installable unit. It is intended for projects that want a two-step automated delivery path:

1. `stage-change-pipeline`: design documents and implementation plans become reviewed OpenSpec changes plus implementation-ready GitHub issues.
2. `codex-codeagent-workflow`: implementation-ready issues become reviewed, verified PRs with CI and merge gates.

## Included Skills

- `stage-change-pipeline`
- `codex-codeagent-workflow`
- `risk-adaptive-cross-review`
- `codeagent`
- `gh-create-issue`
- `clarify`
- `brainstorming`
- `future-aware-architecture`
- `implementation-planning`
- `review`
- `entropy-review`
- `git-worktree-workflows`
- `project-documentation`
- `deep-research`

## Included Agents

This pack does not install agents. The workflow is skill-led and delegates implementation/review work through `codeagent-wrapper` when the target workflow requires it.

## Install

```bash
npx my-agents install pack agentic-issue-delivery
npx my-agents install pack agentic-issue-delivery --platform codex --scope project
```

## Notes

External tools are still required by the workflows and are not installed by this pack:

- `openspec` CLI
- `codeagent-wrapper` with Codex backend configured
- authenticated `gh` CLI
- `git`
- the target project's build/test toolchain

The pack membership is explicit. It includes local support skills that the two main workflows route to or reference. The `codeagent` and `gh-create-issue` skills document how to use the required CLIs; the CLIs themselves must still be installed and authenticated separately.
