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

## Pairs With: `research-engineering`

Use [`research-engineering`](../research-engineering/README.md) when the upstream uncertainty is scientific: a phenomenon, model-process capability, numerical method, observational/data question, scientific evidence claim, or qualification study. It owns the research profile, study protocol, evidence synthesis and named human research decision.

When that decision creates a user-facing or operational need, hand the approved result to this pack. `prd-authoring` and the product workflow translate the bounded evidence into users, requirements, success metrics, prioritization and backlog. They must preserve the evidence scope and limitations instead of upgrading “supported within this study” into a universal product claim. Pure scientific/model implementation changes may go directly from `research-engineering-handoff` to `agentic-issue-delivery` without a PRD.

See [Research Engineering flow](../../docs/architecture/research-engineering-flow.md).
