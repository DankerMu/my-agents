---
name: skill-lifecycle-manager
description: >
  Manage the lifecycle of agent skills: discover patterns, create or update a
  skill, validate it, evaluate it, project or install it, or audit a skill
  library. Use only when the request is explicitly about skills or skill
  libraries, not for general code tasks or agent management.
version: 0.12.0
---

# Skill Lifecycle Manager

Manage skill work as a lifecycle, not as isolated one-off edits. This skill is a thin router: it figures out which lifecycle stage matters now, runs only those stages, and hands off deep specialist work to the right sub-skill or helper instead of re-embedding every workflow inline.

Design bias: **OpenAI-style structure discipline** for authoring, packaging boundaries, and progressive disclosure; **Anthropic-style evaluation discipline** for realistic test prompts, baselines, and separate trigger optimization; **repo-local conventions** for `skill.json`, `CHANGELOG.md`, categories, generated catalogs, and validation commands.

## When Not To Use

- The task is really general research, planning, or implementation — not skills
- The user only wants to install a known skill with no lifecycle guidance — use the platform installer directly
- The workflow is still too vague to identify what a skill should do — clarify intent first, then come back

## Router First

Do not force all seven stages every time. Identify the current request, run only the relevant stages in order. "Audit this skill" does not start by scaffolding a new one.

**Discover-first gate** — before choosing `Create / Update` for a **new** skill, start with `Discover` (and do not draft any package files) if any of these hold:

- the target skill is meant to be general-purpose, project-generic, domain-agnostic, or broadly reusable
- the request explicitly asks for research, comparison, best practices, existing skills, or fusion
- overlap with existing local or ecosystem skills is plausible and would materially affect the design
- the design is likely to borrow from external patterns rather than only local source material

| Stage | Primary question | Default move | Deeper helper |
| --- | --- | --- | --- |
| **Discover** | Do we need external patterns, official references, or upstream comparisons before writing? | Build a focused source inventory | `skill-researcher` (binding workflow when delegated) |
| **Create / Update** | Are we authoring a new skill or materially revising one? | Write or revise the skill package | `skill-creator` patterns |
| **Validate** | Does the skill meet structural, metadata, and repo requirements? | Run local validation before broader eval | `scripts/quick_validate.py` |
| **Evaluate** | Does the skill actually help on realistic tasks? | Run qualitative or mixed eval loop | Anthropic-style eval workflow |
| **Optimize Trigger** | Is the skill under- or over-triggering? | Optimize frontmatter description separately | Trigger eval prompts |
| **Install / Publish** | Does the user want the skill distributed or activated somewhere? | Generate and validate the platform projection, then install or publish | `scripts/project_skill.py` |
| **Audit / Governance** | Is the problem library health, drift, duplicates, or stale hygiene? | Scan inventory and classify issues | `scripts/audit_skill_inventory.py` |

Per-stage procedures: [stage-playbooks.md](references/stage-playbooks.md). Stage checklists, depth modes, and escalation: [lifecycle-modes.md](references/lifecycle-modes.md). Core-vs-platform decisions: [platform-surfaces.md](references/platform-surfaces.md). Projections: [projection-model.md](references/projection-model.md). Serious evaluation passes: [evaluation-loop.md](references/evaluation-loop.md). Formal audits: [audit-rubric.md](references/audit-rubric.md). Read [invocation-posture.md](references/invocation-posture.md) before writing or optimizing a description.

## Operating Rules

1. **Description is the trigger.** Frontmatter `description` is production behavior, not marketing copy.
2. **Keep the body lean.** Heavy detail goes in references or scripts; `SKILL.md` stays actionable and navigable.
3. **Separate body quality from trigger quality.** Improve instructions and trigger wording in separate passes when possible.
4. **Prefer realistic eval prompts** over synthetic toy prompts.
5. **Broad new skills are research-first.** The Discover-first gate above is binding.
6. **Do not duplicate deep research inline** — delegate ecosystem research to `skill-researcher`.
7. **Delegated checkpoints are binding.** Inherit the specialist skill's required pauses, confirmations, and deliverables before resuming downstream stages.
8. **Do not merge create and install by default.** Well-authored and correctly installed are different lifecycle concerns.
9. **Audit for library health, not only single-skill correctness.** A valid skill can still be harmful in aggregate: duplication, context waste, stale metadata.
10. **Decide invocation posture before tuning the trigger**: `manual-first` (default — especially meta-skills, audit/governance skills, risky workflows), `hybrid`, or `auto-first`; then write the description to match.
11. **Keep installable packages self-contained.** Conceptual references to other skills are fine; private script paths of other packages are not. If no shared-runtime distribution exists, duplicate the tooling locally.

## Command Path Model

Treat `SLM_DIR` as the active skill directory: canonical `skills/skill-lifecycle-manager`, Codex projection `.agents/skills/skill-lifecycle-manager`, Claude projection `.claude/skills/skill-lifecycle-manager`. Eval fixtures need `SLM_EVAL_FILE` (canonical: `skills/skill-lifecycle-manager/eval/eval-cases.json`); projected surfaces don't ship `eval/`, so point `--eval-file` at a canonical/local copy or use inline `--eval`. Self-validating this package needs `SLM_CANONICAL_DIR=skills/skill-lifecycle-manager`; that self-validation path is canonical-only — projected copies exclude `tests/` (Claude projections also exclude `skill.json` and `CHANGELOG.md`).

## Workflow Skeleton

Nine phases around the seven routed stages; Phases 2–8 have full playbooks in [stage-playbooks.md](references/stage-playbooks.md).

1. **Scope and route**: classify the request (single-stage / multi-stage / end-to-end) and the artifact (new idea / local skill / installed skill / whole inventory). Decide invocation posture (default `manual-first`). Apply the Discover-first gate — if it fires and depth (Quick/Standard/Deep) is unresolved, stop and resolve it before searching. Summarize the chosen route in a sentence or two so the user can correct course early.
2. **Discover**: official sources first; delegate ecosystem research to `skill-researcher` and honor its checkpoints; convert confirmed research into writing inputs. No target-package drafting until the handoff completes.
3. **Create / Update**: examples first, posture-matched description, canonical-core-vs-projection decision, repo-compatible package, authoring-craft quality bar.
4. **Validate**: `quick_validate.py` → projections → eval-suite validation → packaged unit tests if runner code changed (`uv run python "$SLM_CANONICAL_DIR/scripts/run_unit_tests.py"`) → repo `npm run validate`/`build`. Structure before nuance.
5. **Evaluate**: posture-aligned eval mix, baseline when meaningful, seeded workspaces under `workspaces/<skill-name>/`, qualitative + quantitative review, cross-skill routing suites when adjacent skills compete.
6. **Optimize Trigger**: separate pass; should/should-not/near-miss prompts; record before/after and rationale.
7. **Project / Install / Publish**: generate and validate projections, refresh indexes, use platform-native install/publish, confirm the runtime boundary is portable.
8. **Audit / Governance**: `audit_skill_inventory.py` first pass, deepen with the rubric; rank issues actionably.
9. **Close the loop**: report which stages ran, what changed, what was validated vs not, and the next lifecycle stage. If paused at a delegated checkpoint, say so plainly ("candidate inventory completed; next step is user confirmation").

## Failure Patterns To Avoid

- Collapsing all stages into one giant pass when one stage was asked for
- Duplicating deep discovery inline, or treating `skill-researcher` as inspiration instead of a binding delegated workflow
- Treating a broad new skill as a direct local-drafting task because a nearby repo skill seems related
- Treating `description` as documentation instead of activation logic
- Running subjective evaluation with fake numeric precision
- Mixing trigger optimization with body rewrites so heavily you cannot tell what improved
- Starting `Create / Update` before resolving the Discover depth gate or the delegated confirmation gate
- Baking Codex-only or Claude-only behavior into the canonical core without a good reason
- Depending on another package's private script path at runtime
- Publishing or installing before the skill is structurally valid
- Auditing only for broken files while missing duplicates, drift, or context waste
