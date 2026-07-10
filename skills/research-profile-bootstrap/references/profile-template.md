# Research Project Profile Template

```markdown
# Research Project Profile

Status: living
Last reviewed: YYYY-MM-DD
Owner: <role/person>
Engineering profile: `openspec/project-profile.md` (separate; may be absent)

## Identity and Scope
- Project/system:
- Research domains:
- Intended scales/regimes:
- Out-of-scope claims:

## Research Objects and Recurring Surfaces
- <object/process/model/data/instrument/workflow> — <authority path>

## Canonical Sources and Authority Order
1. <highest authority and path>
2. <next authority>
- Conflict rule:

## Scientific Invariants and Claim Boundaries
- <invariant, conservation law, semantic constraint, or forbidden overclaim>

## Data, Space, Time and Units
- Spatial reference/support:
- Time/calendar/cycle/lead/accumulation semantics:
- Units/sign conventions:
- Missing/QC/uncertainty conventions:

## Baselines, Controls and Benchmark Cases
- <baseline/control/case> — <purpose and immutable identity>

## Evidence-Oracle Matrix
- <claim/surface> -> <oracle/environment> -> <required evidence>

## Execution and Run Identity
- Environments/endpoints:
- Required code/data/config/environment identity:
- Long-run monitoring and artifact location:

## Human Gates
- <decision class> -> <approver role>
- Agents must not:

## Engineering Handoff Mapping
- Research artifact -> OpenSpec/engineering field:
- New recurring implementation risks that must update `openspec/project-profile.md`:

## Open Assumptions and Confidence
- [human-confirmed|inferred|unknown] <statement> — <evidence anchor or owner>
```

## Composable lens prompts

These lenses are additive and non-exclusive.

### Process or model representation

Inspect governing equations, state/flux/parameter semantics, coupling, initial and
boundary conditions, conservation, numerical behavior, restart/output contracts,
and the ladder from idealized verification to observational validation.

### Observation, instrument, field or laboratory evidence

Inspect instrument/product versions, calibration, detection limits, sampling and
representativeness, QC, missingness, spatial/temporal support, ground truth,
field/lab protocols and chain of custody.

### Data product and transformation pipeline

Inspect source lineage, versioning, reprojection/regridding/interpolation,
aggregation, unit conversion, QC propagation, uncertainty, licensing, publishing,
rollback and immutable release identity.

### Forecast, ensemble and operational qualification

Inspect initialization, cycle/lead/valid time, accumulation windows, ensemble
semantics, hindcast independence, baseline skill, reliability, failure modes,
target environment evidence and release/rollback gates.

### Numerical method and performance

Inspect solver contracts, stability, convergence, precision/reproducibility,
hardware/compiler identity, profiling methodology, Amdahl/roofline constraints,
accuracy-performance trade-offs and no-go thresholds.

### Coupled or cross-system integration

Inspect exchanged variables, units, grids, clocks, interpolation, conservation,
feedback order, ownership, restart/state compatibility, error propagation and
independent component baselines.

## Snow-module example

A SHUD snow-module profile update would compose process/model, observation/data,
numerical and integration lenses. It might add snow water equivalent, snowfall/
rainfall phase partition, melt/refreeze/sublimation fluxes, energy or degree-day
assumptions, coupling to infiltration/ET/runoff, cold-start/restart semantics,
SWE and discharge benchmark observations, mass-balance invariants, cold/warm
transition cases, and the human gate for accepting the process representation.
It would not contain the study's final parameter ranges or results.
