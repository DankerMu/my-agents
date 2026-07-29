# Stage Playbooks (Phases 2–8 detail)

Full procedures for each routed stage. SKILL.md holds the router, gates, and skeleton; read the playbook for the stage you are entering. Stage selection and depth rules: [lifecycle-modes.md](lifecycle-modes.md).

## Phase 2: Discover

Use Discover when the domain is unfamiliar, the user wants comparison, or you suspect an official/community pattern should be reused rather than reinvented. If the Discover-first gate fired, Discover is mandatory: do not "just draft a first version" and research later, and do not treat a nearby local skill as permission to skip overlap checks.

1. Prefer **official sources first**: OpenAI and Anthropic are the strongest structural references.
2. If the task needs broader ecosystem comparison, invoke `skill-researcher` as a delegated workflow rather than recreating a landscape survey manually.
3. Once delegated, inherit the specialist's checkpoints: resolve the depth-mode choice first (Quick/Standard/Deep); stop after candidate inventory and show the candidate set for confirmation; do not continue into Collect/Analyze/Synthesize or `Create / Update` until that gate is satisfied.
4. If Discover stays local, capture a short source inventory: primary official anchors, supplemental sources worth borrowing from, patterns to reject.
5. If delegated research completes, keep the result as a separate fusion brief or research handoff artifact before authoring begins.
6. Convert confirmed research into writing inputs: required lifecycle stages, trigger language cues, reusable files/scripts, evaluation expectations.

Until the delegated Discover workflow completes its required handoff, these are out of bounds: drafting the target skill package; creating its references/scripts/eval fixtures; claiming `Create / Update` is underway; running validation on files that should not exist yet.

**Discover vs `skill-researcher`**: the researcher is the deep external research specialist; this skill decides **when** that research is necessary and how it reconnects to the lifecycle. Once Discover delegates, the specialist workflow governs pause points and outputs.

## Phase 3: Create Or Update

Precondition: if the Discover-first gate fired, do not enter until the research handoff and any candidate confirmation are complete.

1. Capture 2-4 realistic examples first.
2. Decide invocation posture (`manual-first` / `hybrid` / `auto-first`) before writing the trigger.
3. Write the frontmatter description to match the posture: `manual-first` — short, boundary-heavy, explicit negative cases; `hybrid` — concise but broad enough for a few high-confidence implicit triggers; `auto-first` — stronger in-scope coverage, but still not a keyword dump.
4. Decide whether the skill has a **canonical core** plus target projections: shared workflow in the canonical package; platform-only behavior out of the core unless intentionally single-platform.
5. Plan reusable contents: `scripts/` for deterministic or repetitive operations; `references/` for longer guidance or domain variants; `assets/` only if the output really needs them.
6. Create or update the repo-compatible package: `SKILL.md`, `skill.json`, `CHANGELOG.md`.
7. Keep the skill router-shaped: stage-based, concise, explicit about when to delegate and when not to use it.
8. Run the writing-quality bar in [authoring-craft.md](authoring-craft.md) before handing off to Validate: checkable completion criteria, per-sentence no-op test, leading-word collapse opportunities, and the failure-mode sweep (duplication, sediment, sprawl, negation, negative space).

Installable-outside-repo skills keep their runtime helpers inside the package or an explicitly shipped distribution unit — never another skill package's private script path. Use `scripts/init_skill.py` for a fresh scaffold (`--project-to codex,claude-code` for immediate projections). When updating, preserve the name unless the rename is deliberate and accompanied by metadata/catalog updates.

## Phase 4: Validate

Validation comes before broad evaluation. Run in order:

1. `uv run python "$SLM_DIR/scripts/quick_validate.py" <skill-dir>`
2. Projections, if the skill targets runtime surfaces: `uv run python "$SLM_DIR/scripts/validate_projection.py" <skill-dir> --platform all`
3. Structured eval suite, if present: `uv run python "$SLM_DIR/scripts/validate_eval_suite.py" <eval-file>`
4. If you changed validation/projection/eval-runner code in this package itself: `uv run python "$SLM_CANONICAL_DIR/scripts/run_unit_tests.py"` (uses `uv run --with pytest`; canonical-only — projected copies exclude `tests/`)
5. Repo-local validation if relevant: `npm run validate`; `npm run build` if indexes need refresh
6. Fix structural issues first: missing files, name mismatches, category drift, changelog/version mismatch, too-short docs, projection drift.

`quick_validate.py` prefers a real YAML parser when available; in minimal environments it falls back to a flat parser, so unusually complex frontmatter may need the full repo validator. Do not start nuanced evaluation while the skill still fails basic structure checks.

## Phase 5: Evaluate

Anthropic-style loop — details in [evaluation-loop.md](evaluation-loop.md):

1. Create realistic eval prompts for the actual work the skill improves.
2. Align the eval mix with the posture: `manual-first` overweights should-not-trigger and adjacent-task prompts; `hybrid` balances in-scope with negative-boundary; `auto-first` overweights in-scope variation and near-misses while keeping negative controls.
3. Decide whether a baseline is needed: new skill — compare with no skill when the difference matters; revision — compare against the prior version.
4. Seed the workspace when useful: `uv run python "$SLM_DIR/scripts/seed_eval_workspace.py" <skill-name> --eval "label|prompt|success criteria"` (or `--eval-file` for a reusable suite).
5. Store artifacts under `workspaces/<skill-name>/iteration-<N>/`.
6. Evaluate qualitative outputs (usefulness, correctness, completeness) and quantitative assertions (only when objective checks exist).
7. Review failures, revise, rerun.
8. For human review of a seeded iteration: `uv run python "$SLM_DIR/scripts/render_review_panel.py" <iteration-dir>`.

`run_surface_eval.py --stage baseline` automates the project-local baseline path by temporarily hiding the active surface projection. Direct surface evals require the relevant platform CLI; structure validation and unit tests do not.

When several adjacent skills plausibly compete, use a repo-level `cross-skill-routing` suite instead of asking each skill to grade itself: unlabeled prompts, one expected winner or `none`, forbidden plausible wrong winners, allowed later followups, expected depth. Canonical suite: `eval/routing/workflow-stage-routing.json`.

Qualitative review by default for ambiguous/creative skills; quantitative assertions for transformations, extraction, formatting, deterministic workflows. When subagents are available, pass them the skill and a realistic task prompt, not your diagnosis — measure whether the skill generalizes.

## Phase 6: Optimize Trigger

A separate stage, not a side effect of general editing. Run when the skill under-triggers, over-triggers on adjacent tasks, or the user asks for description quality.

1. Confirm the invocation posture before editing the description.
2. Draft realistic trigger eval prompts: should-trigger, should-not-trigger, near-miss.
3. Review the set with the user if they want visibility.
4. Improve `description` without simultaneously rewriting the whole body unless necessary.
5. Record before/after description, chosen posture, and rationale.

The goal is not keyword stuffing — it is a legible activation boundary for the intended posture.

## Phase 7: Project, Install Or Publish

Distribution is an adapter step. Identify the target surface (repo-local, Codex `.agents/skills/`, Claude `.claude/skills/` or marketplace/plugin, external registry), then:

1. Generate the projection: `uv run python "$SLM_DIR/scripts/project_skill.py" <skill-dir> --platform all`
2. Validate it: `uv run python "$SLM_DIR/scripts/validate_projection.py" <skill-dir> --platform all` (use `projection.json` to exclude author-only roots)
3. Local repo packaging: refresh indexes with `npm run build`.
4. Local install into supported surfaces: `npm run install-skill -- <name>`.
5. External install/publish: use the platform-native mechanism, never a bespoke path.
6. Confirm the runtime boundary is portable: conceptual references to other skills are fine; private script paths of other packages are not — ship shared tooling in the same package or an explicitly distributed pack.

Do not promise publishing unless credentials, marketplace rules, and packaging expectations are actually satisfied.

## Phase 8: Audit / Governance

Library health, not just one file. Use for "what's stale?", "which skills overlap?", "are we loading too many skills?", "which are low quality or risky?".

Run `uv run python "$SLM_DIR/scripts/audit_skill_inventory.py" --root skills --format markdown` first, then deepen with [audit-rubric.md](audit-rubric.md). The script automates trigger-quality heuristics, reference hygiene, readiness signals, projection health, and context-cost warnings; human review still judges usefulness and wording.

Audit dimensions: duplicate/overlapping intent; stale versions or mismatched changelogs; trigger under-specification or overreach; missing validation/evaluation evidence; context waste from bloated bodies (diagnose with the failure-mode vocabulary in [authoring-craft.md](authoring-craft.md)); risky or undeclared script behavior; install/publish readiness gaps; cross-package private runtime dependencies.
