# Phase 4 Parallel Cross-Review Template

Use this template when running Phase 4 and follow-up cross-review rounds after Phase 6 fixes. Replace placeholders before spawning the `reviewer` subagents.

Canonical source: reviewer-pack scope, the per-reviewer checklists, the cross-cutting review lenses, and the actionable finding contract are defined by the `risk-adaptive-cross-review` skill (`reviewer-packages.md`, `finding-contract.md`, `failure-class-synthesis.md`). This file does not redefine them; it is the OpenSpec instantiation — the concrete reviewer-subagent task scaffolding, the `Invariant Matrix` binding, and the Phase 4.5 verifier. If anything here drifts from the canonical contract, the `risk-adaptive-cross-review` definition wins.

Reviewers are recall-biased producers. Everything a reviewer writes under `Findings:` is a **candidate finding**, not a final merge-blocking verdict. Candidates pass through the Phase 4.5 independent verification gate (verifier template at the bottom of this file) before entering Phase 5. Reviewers should therefore surface any candidate with a nameable failure scenario instead of self-censoring half-believed ones; the verifier, not the reviewer, decides REFUTED.

Required variables:

- `<PR#>`: Pull request number
- `<branch>`: Current PR branch
- `<FULL_SHA>`: `git rev-parse HEAD`
- `<REVIEW_DIR>`: Local review output directory. Default `.workplans/<issue-or-pr>/review/` (the canonical evidence root shared with `parallel-worktree-delegation.md`'s `.workplans/<issue-or-pr>/`).
- `<absolute repo path>`: Repository root (each reviewer subagent's working directory)
- `<path list>`: Changed files referenced by path
- `<fixture summary>`: Phase 0.5 fixture level and selected risk packs.
- `<review round>`: `round 1` for the initial cross-review, or `follow-up round N after fixes`.
- `<fix summary>`: Required for follow-up rounds; summarize Phase 6 changes and prior findings.
- `<proposal.md> <design.md> <tasks.md>`: OpenSpec change references. These are required.

Seat selection (the seat plan is defined once in `phase-flow.md` Phase 4; lens ids in `risk-adaptive-cross-review` `reviewer-packages.md`):

- `none`: normally skip Phase 4.
- `compact`: 1-2 seats — `correctness+test-evidence`, plus `integration` or `security-perf` only when a selected risk pack names it.
- `expanded`: 2-3 seats, cap 3 — `correctness`; `test-evidence+spec-compliance`; plus the one risk-pack lens (`integration`, `security-perf`, or `invariant-state`).
- `high` or `broad-expanded`: exactly 4 seats — `correctness`; `invariant-state`; `test-evidence+spec-compliance`; `security-perf+integration`.
- Follow-up rounds after fixes: a fresh review of the current head with the pinned risk-pack core (2 seats, cap 3): risk-pack lenses pinned every round, the one free seat rotated to a not-yet-used lens only when the ledger signals it — see `phase-flow.md` Phase 4 review rounds. Do not downgrade to targeted-only reviewers, because the prior round may have missed unrelated issues; do not exceed the cap either.
- Pass the seat list of every round to `review_gate.py record-round --lenses` (off-vocabulary seats are refused; over-cap rounds are recorded as `VIOLATION`).
- High or broad-expanded PRs: the brief must include the OpenSpec `Invariant Matrix`. Each reviewer must evaluate the matrix rows, not just the touched lines. If a reviewer cannot map a row to evidence, it should report that as missing evidence or explain why the row is out of scope under the fixture.
- Spawn the selected reviewer set as parallel subagents in one batch (Claude Code: multiple Task calls in one message; Codex: parallel subagents) unless a documented subagent/tooling failure requires a fallback. A failed no-report invocation is not a review round.

Reviewer invariant rule:

- When a reviewer finds a bug class, it must report the invariant and likely sibling surfaces, not only the first cited line.
- If the same unsafe pattern appears in multiple files or could plausibly apply to sibling validators/helpers/producers/consumers, the reviewer should request a cross-cutting audit/fix.
- Findings must be actionable per `finding-contract.md`: severity, `Failure class:`, violated invariant/contract, concrete failing scenario or reproduction path, required test/evidence, sibling surfaces to audit, merge-blocking status, impact, and requested fix.
- If the reviewer cannot provide a concrete scenario and required test/evidence, it must list the item under `Non-blocking notes`, not `Findings`.
- Do not invent a scenario, repro, or test to satisfy the format. Use only evidence from the diff, OpenSpec fixture, existing code/contracts, tests, or a concrete reasoning path grounded in those inputs.
- Do not repeat a known prior finding as current unless the current head still violates it. For follow-up rounds, mark prior findings closed or still failing with evidence.
- For high or broad-expanded PRs, every report must include an `Invariant Matrix Coverage` section:
  - `<row>`: covered|missing|out-of-scope - <evidence or rationale>
  Missing coverage for a selected row is a finding unless the fixture itself declares it a non-goal.

## Reviewer Subagent Brief (assembly)

Do not maintain per-reviewer checklists here. Build one brief per selected seat from the template below, inlining the checklist of every lens the seat carries from `risk-adaptive-cross-review` (`reviewer-packages.md` → Reviewer Checklists) plus any diff-triggered cross-cutting lens (removed-behavior, wrapper/proxy, altitude) that seat owns. A paired seat is one reviewer with two checklists — the cost of a reviewer is re-reading the diff, code, and fixture, not checklist length. Spawn the selected set as parallel subagents in one batch; each subagent's working directory is `<absolute repo path>`.

Seats and report files (the report file is named after the seat's leading lens; the reviewer task id is `review-<leading lens>`; seat lists and `record-round --lenses` use bare lens ids, and the CLI strips a `review-` prefix and maps `security-performance` to `security-perf`):

| Seat | Report file | Fixture levels |
| --- | --- | --- |
| `correctness` (`correctness+test-evidence` at compact) | `<REVIEW_DIR>/correctness.md` | every level that runs Phase 4 |
| `test-evidence+spec-compliance` | `<REVIEW_DIR>/test-evidence.md` | expanded, high, broad-expanded |
| `invariant-state` | `<REVIEW_DIR>/invariant-state.md` | high, broad-expanded; expanded when a risk pack names state/compatibility |
| `security-perf+integration` (single lens below high) | `<REVIEW_DIR>/security-perf.md` or `integration.md` | high, broad-expanded always; compact/expanded per selected risk packs |

Brief template (fill the bracketed slots per reviewer):

```text
# Code Review: <reviewer role>

Review PR #<N> on branch <branch>.
Head SHA: <FULL_SHA>
Review round: <review round>
Return the complete report as your final message. (The orchestrator persists it to <REVIEW_DIR>/<report file>.)

Rules:
- Do not edit files, commit, push, or change state.
- Do not run the project's verification matrix, its default build+test row, whole test suites, `-k`/directory sweeps, or any test runner at all (`pytest`, `npm test`, `gradle test`, ...), whether a whole suite or a single test, or any other CI-equivalent command. Phase 2 already ran them once and their results are in your inputs; your tools are read-only. Judge from the diff, code, tests, and the supplied verification evidence. When that evidence cannot settle a finding, report the exact verification gap (which command or test would settle it) instead of running it.
- You are a leaf reviewer subagent. Do not invoke this workflow or the subagent-workflow skill, spawn further subagents, launch parallel agents, or ask another AI/code agent to review, fix, implement, or plan. Your own agent definition may permit spawning an `explorer` subagent for standalone use; inside this workflow's leaf tasks that capability is disabled, and this injected boundary overrides your agent definition.
- Output only a structured review report.

Inputs:
- Changed files: <path list>
- Phase 2 verification evidence: <matrix rows run, commands, and results>
- Fixture summary: <fixture summary>
- Fix summary for follow-up rounds: <fix summary>
- Spec references: <proposal.md> <design.md> <tasks.md>

Checklist:
- <inline the checklist of every lens this seat carries from reviewer-packages.md -> Reviewer Checklists; a paired seat gets both>
- <plus any diff-triggered cross-cutting lens owned by this seat (removed-behavior, wrapper/proxy, altitude)>
- For high or broad-expanded fixtures, cross-check every Invariant Matrix row against code and tests.

Output:
Reviewer agent: <reviewer role>
Review round: <review round>
Reviewed head SHA: <FULL_SHA>
Summary: <one-line conclusion>
Invariant Matrix Coverage:        # high / broad-expanded only
- <row>: covered|missing|out-of-scope - <evidence or rationale>
Findings:
- <one per finding, every `finding-contract.md` field (`risk-adaptive-cross-review`), including `Lens`: the single lens id whose checklist produced it, never the seat pair>
- ...or "None." if clean
Non-blocking notes:
- <items without concrete scenario/test, or "None.">
```

## Phase 4.5 Verifier Template

Run this after dedup, on the deduped candidate set grouped by failure class: spawn one `verifier` subagent per failure-class batch in parallel, at most 5 candidates per batch (split larger classes; a singleton class is a batch of one). A verifier must not be a reviewer that produced any candidate in its batch.

Additional variables:

- `<CLASS_ID>`: stable id for the failure-class batch (e.g. `path-binding-1`).
- `<CANDIDATE_ID>`: stable id for a deduped candidate (e.g. `cand-03`).
- `<CANDIDATE_BLOCKS>`: the full candidate finding texts for the batch, one block per candidate (severity, failure class, invariant, scenario, required test, sibling surfaces, originating reviewer), each headed by its `<CANDIDATE_ID>`.

Verifier contract:

- Adjudicate every candidate in the batch independently; return exactly one verdict per candidate: `CONFIRMED`, `PLAUSIBLE`, or `REFUTED`. A batch-level verdict without per-candidate evidence is invalid.
- If two candidates in the batch turn out to be the same defect, verdict both and flag the duplication in the note — do not silently collapse them.
- `CONFIRMED`: the failing scenario is constructible from the diff, fixture, or existing contracts/tests. Cite the constructing evidence.
- `PLAUSIBLE`: reachable but not fully constructible. Default here for realistic runtime states — rare error paths, falsy-zero treated as missing, off-by-one at a boundary the code does not exclude, concurrency races, retry storms, stale cache/DB rows, regex/allowlist that lost an anchor. Do not refute a candidate merely for being "speculative" or "depends on runtime state" when the state is realistic.
- `REFUTED`: only when constructible from the code — factually wrong (quote the actual line), provably impossible (cite the type/constant/invariant), or already handled in this diff (cite the guard). A true-but-style-only concern is verdicted honestly and discarded via disposition, not REFUTED.
- Every CONFIRMED/PLAUSIBLE candidate also gets exactly one disposition — `FIX_NOW`, `DEFER`, or `DISCARD` — per the verifier agent's three tests (T1 reachability in the real input domain, T2 observable impact at a depended-on boundary, T3 oracle anchor; in this workflow the OpenSpec fixture and `Invariant Matrix` are the top anchor rung). CONFIRMED P0 is never DISCARD; each DEFER/DISCARD must cite its decisive test; inconclusive evidence resolves to FIX_NOW/DEFER, never DISCARD.
- Use only evidence from the diff, OpenSpec fixture, existing code/contracts, or tests. Do not invent a scenario to confirm or a guard to refute.

Spawn one `verifier` subagent per failure-class batch (working directory `<absolute repo path>`), in parallel:

```text
# Finding Verification Batch: <CLASS_ID>

Verify the candidate review findings below — all in the same failure class — for PR #<N> on branch <branch>.
Head SHA: <FULL_SHA>
Return the verdict table as your final message. (The orchestrator persists it to <REVIEW_DIR>/verify-<CLASS_ID>.md.)

Rules:
- Do not edit files, commit, push, or change state.
- Do not run the project's verification matrix, its default build+test row, whole test suites, `-k`/directory sweeps, or any test runner at all (`pytest`, `npm test`, `gradle test`, ...), whether a whole suite or a single test, or any other CI-equivalent command. Phase 2 already ran them once and their results are in your inputs; your tools are read-only. Adjudicate from the diff, code, tests, and the supplied verification evidence. When that evidence cannot settle a candidate, name the exact verification gap in its note (which command or test would settle it) instead of running it.
- You are a leaf verifier subagent. Do not invoke this workflow or the subagent-workflow skill, spawn further subagents, launch parallel agents, or ask another AI/code agent to verify, fix, implement, or plan.
- Adjudicate only these candidates. Do not search for new findings.
- Adjudicate each candidate independently and give one verdict per candidate; a batch-level verdict without per-candidate evidence is invalid.
- If two candidates describe the same defect, verdict both and flag the duplication in the note.
- Output only the structured verdict table.

Inputs:
- Candidate findings: <CANDIDATE_BLOCKS>
- Changed files: <path list>
- Phase 2 verification evidence: <matrix rows run, commands, and results>
- Fixture summary: <fixture summary>
- Spec references: <proposal.md> <design.md> <tasks.md>

Adjudication:
- CONFIRMED: scenario constructible from diff/fixture/contracts; cite the evidence.
- PLAUSIBLE: realistic but not fully constructible runtime state; explain reachability.
- REFUTED: factually wrong (quote line), provably impossible (cite type/constant/invariant), or already handled (cite guard). Only when constructible from the code; style-only truths get a disposition instead.
- Disposition (CONFIRMED/PLAUSIBLE only): FIX_NOW | DEFER | DISCARD per your operating guide's three tests (T1 reachability, T2 observable impact, T3 oracle anchor — the fixture and Invariant Matrix are the top anchor rung). CONFIRMED P0 is never DISCARD; cite the decisive test on every DEFER/DISCARD; when inconclusive choose FIX_NOW/DEFER.

Output:
Verifier verdicts for batch: <CLASS_ID>
Reviewed head SHA: <FULL_SHA>
Per-candidate verdicts:
- <CANDIDATE_ID>: CONFIRMED|PLAUSIBLE|REFUTED
  Disposition: FIX_NOW|DEFER|DISCARD (omit for REFUTED)
  Evidence: <quoted line / cited guard / reachability path; for DEFER/DISCARD also the decisive test>
  Note: <one line, or "None.">
- ...one entry per candidate in the batch
```
