# Product Manager Pack

This pack bundles the repository's product strategy, planning, and research capabilities into one installable unit, covering the path from product discovery through validated plans to a tracked backlog. It is intended for projects that want a ready-to-use product toolkit without choosing every skill and agent by hand.

## Included Skills

- `clarify` — converge ambiguous product asks into scoped, testable requirements before planning.
- `brainstorming` — structured option exploration and direction pressure-testing.
- `business-plan` — business model, market sizing, and commercial framing deliverables.
- `deep-research` — multi-source, fact-checked research reports feeding product decisions.
- `implementation-planning` — deep execution planning; the `planner` agent's declared dependency.
- `prd-authoring` — turn validated discovery into a review-ready PRD with prioritized requirements and testable acceptance criteria; the bridge between the discovery skills and `gh-create-issue`.
- `gh-create-issue` — turn requirements or PRD-level output into tracked GitHub issues (epic + sub-issues for complex work), closing the discovery-to-backlog handoff.
- `project-documentation` — govern the project's docs set as product deliverables evolve.

## Included Agents

- `explorer` — read-only codebase investigation; the `planner` agent's declared dependency.
- `planner` — turns validated requirements into staged implementation plans.
- `researcher` — web-backed research and verification.

The pack keeps membership explicit, including the `explorer` dependency used by `planner`, so catalog output and installation behavior stay aligned.

## Install

```bash
npx my-agents install pack product-manager
npx my-agents install pack product-manager --platform codex --scope project
```

Use project scope when you want the pack projected into the current repository's `.claude/`, `.agents/`, and `.codex/` runtime surfaces rather than your global user home.
