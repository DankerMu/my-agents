# Cross-Skill Workflow Routing Evaluation

This directory tests competition among adjacent workflow skills rather than asking each skill to grade its own boundary in isolation.

`workflow-stage-routing.json` keeps user prompts unlabeled: prompts do not name any candidate skill. Each case declares one expected winner (or `none`), routes that must not win, allowed later followups, and the expected workflow depth. Coverage rules require at least two positive cases per candidate, two no-skill controls, and negative pressure against every candidate.

Validate the suite before running it:

```bash
uv run python skills/skill-lifecycle-manager/scripts/validate_eval_suite.py \
  eval/routing/workflow-stage-routing.json
```

Install or project every skill listed in the suite on the target surface, then seed and run an iteration:

```bash
uv run python skills/skill-lifecycle-manager/scripts/seed_eval_workspace.py \
  workflow-stage-routing \
  --eval-file eval/routing/workflow-stage-routing.json

uv run python skills/skill-lifecycle-manager/scripts/run_surface_eval.py \
  codex \
  workflow-stage-routing \
  --eval-file eval/routing/workflow-stage-routing.json \
  --workdir .
```

The loader appends a strict `Route:` / `Followups:` / `Depth:` response contract. `result.json` records the parsed route, forbidden-route hits, unexpected followups, actual versus expected depth, and pass/fail status. A `baseline` run temporarily hides every project-local candidate projection and restores all of them afterward:

```bash
uv run python skills/skill-lifecycle-manager/scripts/run_surface_eval.py \
  codex \
  workflow-stage-routing \
  --eval-file eval/routing/workflow-stage-routing.json \
  --stage baseline \
  --workdir .
```

Live model runs are intentionally not part of `npm test`. Shared validation checks the suite structure and coverage deterministically; surface runs remain explicit because they consume model time and may depend on locally installed CLIs.
