---
name: study-design
description: >
  Design a reviewable scientific study protocol for observational,
  experimental, modeling, method, data-product, field/lab, forecast,
  capability-development, or mixed research. Define units, baselines, controls,
  interventions, observables, uncertainty, evidence oracles, stop/branch gates,
  execution budget, protocol freeze and amendments. Use after research framing;
  do not use for implementation planning or result interpretation.
invocation_posture: manual-first
version: 0.1.2
---

# Study Design

Translate an approved research contract into a protocol that can produce
interpretable evidence. The protocol is not limited to controlled experiments.
It can govern observations, numerical model experiments, field/lab campaigns,
data-product construction, forecast evaluation, method development, new process
capabilities, operational qualification, or a combination.

## Preconditions

Load:

- `research/project-profile.md`
- the approved research contract or equivalent question/capability brief
- relevant theory-to-code traceability when the scientific representation changes
- prior studies, baselines, glossary and decision records

If intended claims, alternatives or scope are still unstable, return to
`research-question-framing` rather than hiding ambiguity inside a protocol.

## When Not To Use

- Do not use for technical implementation sequencing; use
  `implementation-planning` after the scientific design is approved.
- Do not use to analyze completed results; use
  `scientific-evidence-synthesis`.
- Do not use for trivial one-off calculations with no durable research claim.
- Do not design a parameter search before the governing theory, data semantics
  and verification requirements are adequate for the intended claim.

## Design Principles

1. **Design against claims.** Every intended claim maps to observations,
   comparisons or tests capable of supporting or contradicting it.
2. **Use real baselines and controls.** Include status quo, unchanged sibling
   surfaces, negative controls and benchmark cases where relevant.
3. **Respect the oracle owner.** Software tests, observations, target hardware,
   field instruments and production environments answer different questions.
4. **Separate verification, validation, calibration and qualification.** They may
   coexist in one program but cannot substitute for one another.
5. **Predeclare branches.** Negative/no-go/inconclusive outcomes are planned
   paths, not failures to be hidden.
6. **Preserve result-aware changes.** Freeze the protocol before primary results;
   later changes become explicit amendments.
7. **Match rigor to impact.** Physical-process, benchmark-authority, data-semantic
   and operational changes require deeper controls and human gates.

## Workflow

### Phase 1: Define the Study Unit and Sampling Frame

State what is being observed or manipulated:

- event, site, basin, grid cell, profile, station, model configuration,
  simulation member, forecast cycle, instrument, dataset version, code version,
  or another unit
- spatial and temporal extent, resolution and support
- inclusion/exclusion criteria
- sampling/selection mechanism and risks of leakage or cherry-picking

For multi-regime claims, sample the regimes rather than relying on one convenient
case.

### Phase 2: Define Arms, Alternatives and Baselines

Record:

- status quo or current production/reference baseline
- candidate alternatives or interventions
- unchanged controls and sibling surfaces
- idealized/synthetic cases where the expected behavior is known
- observational or external reference data
- holdout cases or independent validation periods

When comparison conditions differ, document normalization and fairness rules
before execution.

### Phase 3: Define Scientific and Data Contracts

Name:

- state variables, fluxes, observables, parameters and units
- space/time/calendar/cycle/lead/accumulation semantics
- missing/QC/uncertainty rules
- conserved quantities, bounds and forbidden states
- data and software identities that must be frozen

If equations, parameterizations, scientific state, coupling or numerical methods
change, invoke `theory-to-code-traceability` and bind its invariants into this
protocol.

### Phase 4: Define Measurements, Metrics and Uncertainty

For each claim, define:

- primary and secondary observables
- metric formula, units, aggregation and weighting
- uncertainty source and reporting method
- repeats, ensemble members, seeds or sensitivity dimensions
- practical and scientific significance thresholds
- missing/failure handling

Avoid selecting only metrics that favor one alternative. Include conservation,
stability, failure and boundary behavior for scientific software.

### Phase 5: Build the Evidence-Oracle Matrix

Create one row per claim or governing invariant:

```text
<claim/invariant> -> <oracle/environment> -> <procedure> -> <evidence artifact>
```

Examples:

- equation implementation -> idealized/unit verification -> test report
- hydrologic response -> observation/benchmark dataset -> metric table + plots
- parallel speedup -> target hardware -> repeat timing manifest
- forecast usefulness -> independent hindcast + operational baseline -> skill report
- data-product lineage -> immutable source/checksum chain -> provenance manifest

Never let a convenient local test impersonate a remote, observational or
production oracle.

### Phase 6: Define Branch, Stop and No-Go Gates

Predeclare:

- minimum evidence needed to continue
- thresholds that select an alternative
- results that close a line with no implementation
- inconclusive branch and maximum allowed refinement
- safety/scientific blockers
- compute or data budget cap
- rollback or containment for operational trials

A no-go decision is a valid deliverable.

### Phase 7: Plan Execution and Artifacts

Define:

- ordered runs and true dependencies
- parallelizable independent arms
- code/data/config/environment manifests
- command, log and output locations
- long-job monitoring via `monitor`
- result-blind preprocessing and analysis steps
- expected artifact names from
  [protocol-template.md](references/protocol-template.md)

Use `implementation-planning` only when approved scientific work requires a
complex technical rollout or implementation sequence. Do not let it reopen the
scientific scope.

### Phase 8: Pressure-Test the Protocol

Record one explicit gate decision on the protocol: `grill-me` when terminology
is stable, `grill-with-docs` when terms, process boundaries or durable
decisions must persist to `openspec/glossary.md` / `docs/adr/`, or
`skipped:<reason>` — only for genuinely narrow, low-impact work. A delegated
grill stays interactive (one question at a time) and must not be simulated.
The canonical gate contract lives in `research-lifecycle`
(`references/pressure-test-contract.md`).

Focus questions on decisions that could change the scientific conclusion:
selection bias, hidden confounders, baseline fairness, non-identifiability,
process boundaries, data leakage, units/time/space mismatch, invalid oracle,
and result-dependent stopping.

For expensive or high-risk loops, invoke `meta-loop` to audit the
produce/check/fix/recheck design.

### Phase 9: Freeze

Write the protocol and a lock record before inspecting primary results. The lock
records:

- protocol path and digest
- code/data/config identities
- approved claim list and primary metrics
- date and approver

Do not hand-author the lock when avoidable: the `research-lifecycle` skill
ships mechanical provenance tooling that computes the digest, refuses
re-freezing, and later verifies runs and outputs against it.

Changes after freeze use an amendment. Label analyses added after seeing results
as exploratory unless an independent confirmatory run is performed.

## Model-Process Capability Ladder

For work such as adding a snow module, design a staged ladder instead of jumping
directly to basin calibration:

1. theory/representation review and alternative selection
2. units, bounds, conservation and limiting-case checks
3. isolated process tests: snowfall/rainfall partition, accumulation, melt,
   refreeze/sublimation as applicable
4. synthetic cold/warm transitions and no-snow/no-melt controls
5. coupling tests with infiltration, ET, runoff, restart and output
6. regression against snow-free regimes and unchanged basins
7. observational validation with SWE/snow cover/discharge where available
8. sensitivity and identifiability analysis
9. calibration only after verification is adequate
10. performance and operational qualification if relevant

Each rung has its own oracle and gate. Passing a lower rung does not imply the
higher claim.

## Output

Use [protocol-template.md](references/protocol-template.md). Report:

- protocol path and state
- claims covered and uncovered
- pressure-test result
- frozen identities
- open decisions and named owner
- whether technical implementation planning or engineering handoff is next
