---
name: research-engineering-handoff
description: >
  Convert an approved research decision into a bounded engineering handoff preserving scientific intent, invariants, evidence oracles, and human decision authority. Invoke explicitly, typically from research-lifecycle before stage-change-pipeline.
invocation_posture: manual-first
version: 0.2.1
---

# Research Engineering Handoff

Bridge the scientific control plane and the software delivery control plane. The
handoff says **what approved change engineering must realize and what scientific
meaning it must preserve**. It does not replace OpenSpec design, implementation
planning, GitHub issue decomposition, code review, or post-implementation
scientific evaluation.

## Entry Gate

Do not create a handoff until all of the following are present:

- `research/project-profile.md`
- a bounded question, capability-gap or decision contract
- an approved study protocol or an explicit human decision that no additional
  pre-implementation study is required
- evidence synthesis or another named decision basis
- a human verdict authorizing engineering work
- theory-to-code traceability when scientific semantics, equations, process
  representation, state, units, coupling or numerical method change

If the decision is still exploratory, return to `research-lifecycle`. If the
outcome is primarily a user/product/operational requirement rather than a
scientific change, route through the `product-manager` pack before delivery.

## Output

Write:

```text
research/studies/<study-id>/engineering-handoff.md
```

using [handoff-template.md](references/handoff-template.md). A valid handoff is
status `ENGINEERING_HANDOFF_READY` and names the approver, source study, accepted
decision, scope, invariants, evidence obligations and downstream route.

## Delegated Skills

- Use `explorer` or `blind-spot-pass` to map affected code, data, formats,
  consumers and legacy surfaces before freezing the handoff.
- Use `grill-me` to challenge a stable handoff for missing decisions,
  cross-surface impacts and untestable acceptance criteria.
- Use `grill-with-docs` when scientific terms, implementation boundaries or
  long-lived decisions must be reconciled with `openspec/glossary.md` and
  `docs/adr/` before OpenSpec authoring.
- Use `future-aware-architecture` for high-impact architecture choices after the
  scientific representation is approved.
- Use `implementation-planning` only when staged rollout, dependency order,
  rollback or PR boundaries need a deep execution plan. It cannot change the
  scientific decision.
- Pass the completed handoff to `stage-change-pipeline`; do not bypass it by
  creating implementation issues directly for a complex change.

## Workflow

### 1. Bind the Source Decision

Record immutable references to:

- study ID and profile
- frozen protocol and amendments
- traceability package
- evidence synthesis
- human decision and approval date

Quote the accepted decision narrowly. Do not rewrite it into a broader feature
claim.

### 2. Define Required Behavioral Change

Describe observable behavior, scientific capability and affected regimes. For a
snow module, this might include:

- new snow states and forcing inputs
- phase partition, accumulation, melt and coupling behavior
- expected outputs and restart behavior
- explicit excluded processes
- fallback or compatibility behavior when snow is disabled or unavailable

Keep implementation choices out unless the scientific decision already fixes
them.

### 3. Carry Scientific Invariants Forward

List every non-negotiable scientific or numerical contract that OpenSpec and
implementation must preserve:

- equations/process rules and approved approximations
- units, sign conventions, calendars and spatial/temporal support
- mass/energy conservation and admissible state bounds
- update order, coupling and solver interaction
- baseline and unchanged sibling behavior
- source data authority and lineage
- forbidden shortcuts, such as weakening tests or recalibrating parameters to
  hide an implementation error

Each invariant must map to verification evidence or an explicit post-implementation
scientific study.

### 4. Separate Verification from Scientific Evaluation

Create two sections:

**Engineering verification** answers whether software faithfully implements the
approved contract. It may include unit/limit/conservation tests, reference
solutions, parser/restart compatibility, build matrices, deterministic behavior,
and target-platform execution.

**Scientific evaluation** answers whether the implemented representation is
credible or useful in the intended domain. It may include independent events,
regions, observations, intercomparison, uncertainty analysis and calibration
only after verification gates pass.

Do not let an OpenSpec acceptance test claim more than its oracle can prove.

### 5. Map Affected Surfaces and Ownership

Identify:

- model/process core
- data and forcing contracts
- configuration and parameter schemas
- state initialization, restart and migration
- solvers, scheduling and performance surfaces
- outputs and downstream readers/products
- tests, examples, docs and operational environments

State which surfaces are in scope, out of scope, unchanged but must be regressed,
or owned by a later change. Use project-local evidence, not guessed paths.

### 6. Define Delivery and Rollback Boundaries

Record:

- dependency order and safe PR boundaries
- feature flags, staged qualification or inactive asset strategy where relevant
- rollback target and data/state compatibility
- whether no-go is possible after implementation evidence
- post-merge research obligations

A high-risk scientific capability should normally be reversible until its
qualification gate passes.

### 7. Pressure-Test the Handoff

Record one explicit gate decision on the handoff: `grill-me` when terminology
is stable, `grill-with-docs` when terms, process boundaries or durable
decisions must persist to `openspec/glossary.md` / `docs/adr/`, or
`skipped:<reason>` — only for genuinely narrow, low-impact work. A delegated
grill stays interactive (one question at a time) and must not be simulated.
The canonical gate contract lives in `research-lifecycle`
(`references/pressure-test-contract.md`).

Challenge:

- whether requirements are scientifically unambiguous
- whether every invariant has an oracle
- whether implementation could pass while changing scientific meaning
- whether disabled/default/restart/legacy paths are covered
- whether post-implementation validation is being mistaken for code acceptance
- whether the PR decomposition can preserve a working, interpretable system

Record resolved decisions and remaining human questions.

### 8. Synchronize the Two Profiles

Keep the profile separation explicit:

- `research/project-profile.md` remains the authority for scientific objects,
  data/model authorities, invariants, benchmark regimes, evidence and human gates.
- `openspec/project-profile.md` remains the authority for software entry surfaces,
  contracts, risk packs, commands and verification matrix.

When the handoff introduces a **recurring new implementation surface** (for
example a persistent model-process plug-in boundary, scientific state schema, or
new target-platform oracle), update `openspec/project-profile.md` during the
`stage-change-pipeline`/`subagent-workflow` profile-gap step. Do not copy the
whole research profile into OpenSpec.

### 9. Handoff to Delivery

Pass the handoff and source artifacts to `stage-change-pipeline`. Delivery
packs install independently and know nothing about research artifacts, so this
skill owns the gate at the boundary:

- before invoking the pipeline, verify the handoff status is
  `ENGINEERING_HANDOFF_READY` and the named human approval is recorded; a
  `DRAFT`, `REVIEWED` or `REJECTED` handoff must not enter delivery
- the handoff's pressure-test record covers the scientific contract only; it
  does not satisfy the pipeline's own Stage-1 grill gate (`grillGate`). Decide
  that gate on the engineering design package in its own right — run it, or
  skip with a recorded reason.

The resulting OpenSpec change must:

- cite the handoff and decision
- reproduce the scientific invariants without weakening them
- separate engineering verification from later scientific evaluation
- map each invariant to a requirement, scenario, task, evidence or explicit
  non-goal
- preserve unresolved scientific questions instead of silently deciding them

After issues are implementation-ready, `subagent-workflow` owns implementation,
review, verifier adjudication, CI/evidence and human merge. After merge,
`codebase-stewardship` owns architecture and entropy governance; neither may
rewrite the scientific evidence record to make delivery look clean.

## Hard Rules

1. No human-approved research decision, no engineering handoff.
2. Scientific invariants must survive translation into OpenSpec.
3. Verification and validation remain separate evidence tracks.
4. Unresolved science is not delegated to an implementer.
5. Every forbidden shortcut and rollback boundary is explicit.
6. Complex research-driven changes do not bypass `stage-change-pipeline`.
